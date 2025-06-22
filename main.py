import json
import os
import shutil
import tempfile
import time
from pathlib import Path
from dotenv import load_dotenv

from agent.project_scanner import update_project_manifest
# Removida a duplicata de import project_scanner
from agent.brain import (
    get_action_plan,
    generate_code_for_action,
    get_maestro_decision,
    generate_next_objective,
    generate_capacitation_objective
)
# from agent.patch_applicator import apply_patches # Será substituído por manipulação em memória
from agent.code_validator import validate_python_code, validate_json_syntax # Reavaliar uso
from agent.tool_executor import run_in_sandbox, run_pytest, check_file_existence


class HephaestusAgent:
    """Classe principal que encapsula a lógica do agente autônomo."""

    def __init__(self):
        """Inicializa o agente com configuração."""
        self.config = self.load_config()
        self.api_key = os.getenv("OPENROUTER_API_KEY")
        self.model_list = ["deepseek/deepseek-r1-0528:free", "mistralai/devstral-small:free"]
        self.light_model = "anthropic/claude-3.5-haiku"
        self.state = {}
        self.objective_stack = []  # Pilha de objetivos
        self._reset_cycle_state() # Inicializa o estado


    def _reset_cycle_state(self):
        """Reseta o estado transitório do ciclo, mantendo o objetivo atual."""
        # Mantém o current_objective entre os ciclos, a não ser que seja um sucesso
        current_objective = self.state.get("current_objective")
        self.state = {
            "current_objective": current_objective,
            "manifesto_content": "",
            "action_plan_data": None, # Conterá o JSON do Arquiteto: {"analysis": "...", "action_plan": []}
            "in_memory_files": {},   # Dict[str, List[str]] para armazenar conteúdo de arquivos em memória
            "model_architect": None, # Modelo usado pelo Arquiteto
            "model_code_engineer": None, # Modelo usado pelo Engenheiro de Código
            "strategy_key": None,
            "validation_result": (False, "PENDING", "Ciclo não iniciado"),
            "applied_files_report": {} # Relatório de quais arquivos foram realmente modificados/criados
        }

    @staticmethod
    def load_config() -> dict:
        """Carrega o arquivo de configuração do agente."""
        with open("hephaestus_config.json", "r", encoding="utf-8") as f:
            return json.load(f)

    def _generate_manifest(self) -> bool:
        """Gera o manifesto do projeto."""
        print("Gerando manifesto do projeto (AGENTS.md)...")
        try:
            target_files = []
            if self.state["current_objective"] and "project_scanner.py" in self.state["current_objective"]:
                target_files.append("agent/project_scanner.py")
            update_project_manifest(root_dir=".", target_files=target_files)
            with open("AGENTS.md", "r", encoding="utf-8") as f:
                self.state["manifesto_content"] = f.read()
            print(f"--- MANIFESTO GERADO (Tamanho: {len(self.state['manifesto_content'])} caracteres) ---")
            return True
        except Exception as e:
            print(f"ERRO CRÍTICO ao gerar manifesto: {e}")
            return False

    def _get_file_content_from_memory_or_disk(self, file_path: str) -> Optional[List[str]]:
        """Obtém o conteúdo do arquivo da memória, se existir, senão do disco."""
        if file_path in self.state["in_memory_files"]:
            return self.state["in_memory_files"][file_path]
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                return f.read().splitlines()
        except FileNotFoundError:
            return None
        except Exception as e:
            print(f"Erro ao ler arquivo {file_path} do disco: {e}")
            return None

    def _write_files_from_memory_to_disk(self) -> bool:
        """Escreve todos os arquivos em self.state['in_memory_files'] para o disco."""
        print("Persistindo alterações do ciclo atual no disco...")
        self.state["applied_files_report"] = {}
        overall_success = True
        for file_path, lines in self.state["in_memory_files"].items():
            try:
                # Garantir que o diretório exista
                Path(file_path).parent.mkdir(parents=True, exist_ok=True)
                with open(file_path, "w", encoding="utf-8") as f:
                    f.write("\n".join(lines))
                self.state["applied_files_report"][file_path] = {"status": "success", "message": "Arquivo salvo com sucesso."}
                print(f"Arquivo salvo: {file_path}")
            except Exception as e:
                print(f"ERRO ao salvar arquivo {file_path}: {e}")
                self.state["applied_files_report"][file_path] = {"status": "error", "message": str(e)}
                overall_success = False

        if overall_success:
            print("Todas as alterações foram persistidas com sucesso.")
        else:
            print("Algumas alterações não puderam ser persistidas. Verifique o relatório.")
        return overall_success

    def _apply_action_to_in_memory_files(self, action_details: dict, generated_code: str) -> bool:
        """
        Aplica uma única ação (CREATE, APPEND, REPLACE) aos arquivos em memória.
        A ação DELETE_BLOCK é mais complexa e pode ser tratada separadamente ou
        generalizada se o Arquiteto fornecer start_line e end_line para ela.
        Por enquanto, focaremos nas ações de modificação de conteúdo.
        """
        action_type = action_details["action"]
        file_path = action_details["path"]

        current_lines = self.state["in_memory_files"].get(file_path)

        if action_type == "CREATE_FILE":
            if file_path in self.state["in_memory_files"]:
                print(f"Aviso: Tentando CREATE_FILE em arquivo já existente em memória: {file_path}. Sobrescrevendo.")
            self.state["in_memory_files"][file_path] = generated_code.splitlines()
            print(f"Ação CREATE_FILE: {file_path} preparado em memória.")
            return True

        if current_lines is None: # Para APPEND ou REPLACE, o arquivo deve existir (ou ter sido criado)
            # Se CREATE_FILE não foi chamado antes para este arquivo, isso é um erro de plano.
            # O Arquiteto deve primeiro criar o arquivo se ele não existir.
            # No entanto, podemos tentar ler do disco como fallback se não estiver em memória.
            print(f"Aviso: Arquivo '{file_path}' não encontrado em memória para '{action_type}'. Tentando ler do disco.")
            disk_lines = self._get_file_content_from_memory_or_disk(file_path) # Tenta ler do disco
            if disk_lines is None and action_type != "CREATE_FILE": # CREATE_FILE já tratado
                 print(f"ERRO: Arquivo '{file_path}' não existe e a ação é '{action_type}', que requer um arquivo existente.")
                 return False
            current_lines = disk_lines if disk_lines is not None else [] # Inicia com lista vazia se não leu nada e vai criar
            self.state["in_memory_files"][file_path] = current_lines


        if action_type == "APPEND_TO_FILE":
            self.state["in_memory_files"][file_path].extend(generated_code.splitlines())
            print(f"Ação APPEND_TO_FILE: Conteúdo adicionado a {file_path} em memória.")
            return True

        elif action_type == "REPLACE_BLOCK":
            start_line = action_details.get("start_line")
            end_line = action_details.get("end_line")
            if start_line is None or end_line is None:
                print(f"ERRO: REPLACE_BLOCK para {file_path} não especificou start_line ou end_line.")
                return False

            # Ajuste para base 0 para listas Python
            start_idx = start_line - 1
            end_idx = end_line # end_line é inclusivo na descrição, então o slice vai até end_idx

            if not (0 <= start_idx <= end_idx <= len(current_lines)):
                print(f"ERRO: Linhas inválidas para REPLACE_BLOCK em {file_path}. Start: {start_line}, End: {end_line}, Total Linhas: {len(current_lines)}")
                # Permitir substituição de arquivo inteiro se start_line=1 e end_line cobre tudo
                if start_line == 1 and end_line >= len(current_lines):
                    print(f"Interpretando como substituição total do arquivo {file_path}.")
                    start_idx = 0
                    end_idx = len(current_lines)
                else:
                    return False

            new_block_lines = generated_code.splitlines()
            self.state["in_memory_files"][file_path] = current_lines[:start_idx] + new_block_lines + current_lines[end_idx:]
            print(f"Ação REPLACE_BLOCK: Bloco substituído em {file_path} em memória ({start_line}-{end_line}).")
            return True

        # TODO: Implementar DELETE_BLOCK se necessário e se o Arquiteto o usar.
        # elif action_type == "DELETE_BLOCK":
        #     # ... lógica para deletar bloco ...
        #     pass

        else:
            print(f"ERRO: Tipo de ação desconhecido ou não suportado: {action_type}")
            return False
        return True


    def _run_architect_phase(self) -> bool:
        """Fase 2: Arquiteto gera o plano de ação."""
        print("\nSolicitando plano de ação da IA (Arquiteto)...")
        # Usar o primeiro modelo da lista para o Arquiteto, ou um modelo específico se definido
        architect_model = self.config.get("models", {}).get("architect_default", self.model_list[0])
        self.state["model_architect"] = architect_model

        action_plan_data, error_msg = get_action_plan(
            api_key=self.api_key,
            model=architect_model,
            objective=self.state["current_objective"],
            manifest=self.state["manifesto_content"]
        )
        if error_msg:
            print(f"--- FALHA: Arquiteto não conseguiu gerar um plano de ação. Erro: {error_msg} ---")
            return False
        if not action_plan_data or "action_plan" not in action_plan_data:
            print("--- FALHA: Arquiteto retornou uma resposta inválida ou sem 'action_plan'. ---")
            return False

        self.state["action_plan_data"] = action_plan_data
        print(f"--- PLANO DE AÇÃO GERADO PELO ARQUITETO ({architect_model}) ---")
        print(f"Análise do Arquiteto: {action_plan_data.get('analysis', 'Nenhuma análise fornecida.')}")
        # print(f"Plano: {json.dumps(action_plan_data.get('action_plan', []), indent=2)}") # Muito verboso
        return True

    def _run_code_engineer_phase_and_apply(self) -> bool:
        """Fase 3: Engenheiro de Código gera código para cada ação e aplica em memória."""
        print("\nIniciando fase de Engenharia de Código e aplicação em memória...")
        action_plan = self.state.get("action_plan_data", {}).get("action_plan", [])
        if not action_plan:
            print("Nenhuma ação no plano. Pulando Engenharia de Código.")
            return True # Não é uma falha se o plano estiver vazio

        # Usar o primeiro modelo da lista para o Engenheiro, ou um específico
        code_engineer_model = self.config.get("models", {}).get("code_engineer_default", self.model_list[0])
        self.state["model_code_engineer"] = code_engineer_model

        # Limpar/resetar os arquivos em memória para o novo ciclo de aplicação
        self.state["in_memory_files"] = {}

        for i, action_details in enumerate(action_plan):
            print(f"\nProcessando Ação {i+1}/{len(action_plan)}: {action_details.get('action')} para '{action_details.get('path')}'")

            file_path = action_details.get("path")
            if not file_path:
                print(f"ERRO: Ação {i+1} não tem 'path'. Pulando ação.")
                continue

            current_file_content_str = None
            if action_details.get("action") != "CREATE_FILE":
                # Para APPEND, REPLACE, etc., precisamos do conteúdo atual.
                # Ele é lido da memória (se modificado por ação anterior) ou do disco.
                file_lines = self._get_file_content_from_memory_or_disk(file_path)
                if file_lines is not None:
                    current_file_content_str = "\n".join(file_lines)
                # Se file_lines for None e a ação não for CREATE_FILE, generate_code_for_action
                # já tem um aviso sobre isso no prompt.

            generated_code, error_msg = generate_code_for_action(
                api_key=self.api_key,
                model=code_engineer_model,
                action=action_details,
                file_content=current_file_content_str
            )

            if error_msg:
                print(f"--- FALHA: Engenheiro de Código não conseguiu gerar código para a ação {i+1}. Erro: {error_msg} ---")
                self.state["validation_result"] = (False, "CODE_GENERATION_FAILED", f"Ação {i+1} ({action_details.get('action')} para {file_path}): {error_msg}")
                return False # Interrompe o processo se uma ação falhar

            # Nota: generated_code pode ser None ou "" se o LLM decidir que nada deve ser gerado (ex: para um DELETE)
            # A função _apply_action_to_in_memory_files deve lidar com isso.
            # Se generated_code for None devido a um erro, error_msg já o tratou.
            # Se for None intencionalmente, error_msg será None.

            print(f"Código gerado pela IA para Ação {i+1} (primeiras 100 chars): '{ (generated_code or '')[:100] }...'")

            if not self._apply_action_to_in_memory_files(action_details, generated_code if generated_code is not None else ""):
                print(f"--- FALHA: Não foi possível aplicar a ação {i+1} ({action_details.get('action')} para {file_path}) em memória. ---")
                self.state["validation_result"] = (False, "IN_MEMORY_APPLY_FAILED", f"Ação {i+1} ({action_details.get('action')} para {file_path})")
                return False # Interrompe se a aplicação em memória falhar

        print("\nTodas as ações do plano foram processadas e aplicadas em memória.")
        return True


    def _run_maestro_phase(self) -> bool:
        """Executa a fase de decisão do maestro."""
        print("\nSolicitando decisão do Maestro...")
        # O Maestro precisa de uma representação da "proposta" para avaliar.
        # No novo fluxo, isso é o plano do Arquiteto.
        # O prompt atual do Maestro espera "engineer_response" que era o JSON com patches.
        # Vamos passar o action_plan_data (que inclui analysis e o action_plan)
        # Pode ser necessário ajustar o prompt do Maestro em brain.py se isso não for adequado.
        if not self.state.get("action_plan_data"):
            print("--- FALHA: Nenhum plano de ação disponível para o Maestro avaliar. ---")
            return False

        maestro_model = self.config.get("models", {}).get("maestro_default", self.model_list[0])

        maestro_logs = get_maestro_decision(
            api_key=self.api_key, model_list=[maestro_model], # Passa como lista, mas só um modelo
            engineer_response=self.state["action_plan_data"], # Passando o plano do arquiteto
            config=self.config,
        )
        maestro_attempt = next((a for a in maestro_logs if a.get("success")), None)
        if not maestro_attempt or not maestro_attempt.get("parsed_json"):
            print("--- FALHA: Maestro não retornou uma resposta JSON válida. ---")
            # Adicionar mais detalhes do erro se disponíveis
            raw_resp = maestro_attempt.get("raw_response") if maestro_attempt else "Nenhuma tentativa registrada."
            print(f"Resposta bruta do Maestro: {raw_resp}")
            return False
        
        decision = maestro_attempt["parsed_json"]
        strategy_key = (decision.get("strategy_key") or "").strip()

        # Validar se a strategy_key é uma das chaves em validation_strategies OU "CAPACITATION_REQUIRED"
        valid_strategies = list(self.config.get("validation_strategies", {}).keys())
        valid_strategies.append("CAPACITATION_REQUIRED") # Adicionar explicitamente

        if strategy_key not in valid_strategies:
            print(f"--- FALHA: Maestro escolheu uma estratégia inválida ou desconhecida: '{strategy_key}' ---")
            print(f"Estratégias válidas são: {valid_strategies}")
            return False

        print(f"Estratégia escolhida pelo Maestro: {strategy_key}")
        self.state["strategy_key"] = strategy_key
        return True

    def _execute_validation_strategy(self) -> None:
        """Executa os passos de validação conforme a estratégia escolhida."""
        strategy_key = self.state["strategy_key"]
        strategy = self.config["validation_strategies"].get(strategy_key, {})
        steps = strategy.get("steps", [])
        print(f"\nExecutando estratégia '{strategy_key}' com os passos: {steps}")

        # Resetar resultado da validação para este ciclo de estratégia
        self.state["validation_result"] = (False, "STRATEGY_PENDING", f"Iniciando estratégia {strategy_key}")

        for step_name in steps:
            print(f"--- Passo de Validação: {step_name} ---")
            
            if step_name == "persist_changes_from_memory":
                if not self.state.get("in_memory_files"):
                    print("Nenhum arquivo em memória para persistir. Pulando passo.")
                    # Considerar se isso deve ser um sucesso ou um aviso.
                    # Se o plano era para não fazer nada, é um sucesso.
                    # Se o plano tinha ações mas resultou em nada em memória (erro anterior),
                    # então não deveria chegar aqui ou já deveria ter falhado.
                    # Por ora, se in_memory_files está vazio, é um "sucesso" para este passo.
                    continue

                if self._write_files_from_memory_to_disk():
                    print("Mudanças persistidas no disco com sucesso.")
                else:
                    print("ERRO: Falha ao persistir mudanças do disco.")
                    # Coletar mensagens de erro do relatório de apply
                    error_messages = []
                    for file_path, result in self.state.get("applied_files_report", {}).items():
                        if result.get("status") == "error":
                            error_messages.append(f"File {file_path}: {result.get('message')}")
                    self.state["validation_result"] = (False, "PERSISTENCE_FAILED", "\n".join(error_messages))
                    return # Interrompe a estratégia se a persistência falhar

            elif step_name == "run_pytest_validation":
                # Esta validação agora ocorre APÓS as mudanças serem persistidas (se persist_changes_from_memory foi um passo)
                # ou em arquivos temporários se quisermos validar antes de persistir.
                # Por simplicidade, vamos assumir que ocorre nos arquivos já modificados no disco.
                success, details = run_pytest(test_dir='tests/') # run_pytest já imprime seus resultados
                if not success:
                    self.state["validation_result"] = (False, "PYTEST_FAILURE", details)
                    return # Interrompe a estratégia
                print("Validação Pytest: SUCESSO.")


            elif step_name == "run_benchmark_validation":
                print("Passo de Benchmark executado (simulado).")
                # Adicionar lógica real de benchmark aqui se necessário

            # Outros passos de validação podem ser adicionados aqui

        # Se todos os passos da estratégia passaram (ou não houve falha que retornou):
        current_strategy_success, _, _ = self.state.get("validation_result", (False, "", ""))

        # Se o loop terminou e validation_result ainda é o inicial "STRATEGY_PENDING"
        # ou se não foi explicitamente setado para falha, então consideramos sucesso para a estratégia.
        # No entanto, cada passo que falha deve dar um `return`.
        # Se chegamos aqui, significa que nenhum passo falhou e retornou.

        if strategy_key == "DISCARD":
            self.state["validation_result"] = (True, "DISCARDED", "Estratégia de descarte executada.")
        elif "persist_changes_from_memory" in steps:
             # Se persist_changes_from_memory estava nos passos e não falhou:
            self.state["validation_result"] = (True, "APPLIED_AND_VALIDATED", f"Estratégia '{strategy_key}' concluída, patches aplicados e validados.")
        else:
            # Se a estratégia não envolvia persistência (ex: só validação de um plano teórico)
            self.state["validation_result"] = (True, "VALIDATED_ONLY", f"Estratégia '{strategy_key}' de validação concluída (sem persistência de patches).")


    def run(self) -> None:
        """Executa o ciclo de vida completo do agente de forma perpétua."""
        if not self.api_key:
            print("Erro: OPENROUTER_API_KEY não encontrada. Encerrando.")
            return

        # Initialize with first objective if stack is empty
        if not self.objective_stack:
            print("Gerando objetivo inicial...")
            # Usar o modelo light configurado ou um default para o primeiro objetivo
            initial_objective_model = self.config.get("models", {}).get("objective_generator", self.light_model)
            initial_objective = generate_next_objective(self.api_key, initial_objective_model, "")
            self.objective_stack.append(initial_objective)
            print(f"Objetivo inicial: {initial_objective}")

        while self.objective_stack:
            current_objective = self.objective_stack.pop()
            print(f"\n\n{'='*20} NOVO CICLO DE EVOLUÇÃO {'='*20}")
            print(f"OBJETIVO ATUAL: {current_objective}\n")

            self._reset_cycle_state() # Reseta o estado do ciclo anterior, mantendo current_objective
            self.state["current_objective"] = current_objective


            # Fase 1: Estrategista (já ocorreu ao pegar `current_objective` da pilha ou gerar inicial)
            # (Opcional: Poderia haver uma chamada explícita aqui se a lógica de objetivo fosse mais complexa)

            # Gerar Manifesto (necessário para Arquiteto e Engenheiro)
            if not self._generate_manifest():
                print("Falha crítica ao gerar manifesto. Encerrando ciclo.")
                break # Ou continue para o próximo objetivo se for recuperável

            # Fase 2: Arquiteto - Gera o plano de ação
            if not self._run_architect_phase():
                print("Falha na fase do Arquiteto. Tentando próximo objetivo se houver.")
                # Adicionar lógica de tratamento de erro, talvez um objetivo de correção?
                # Por ora, apenas continua para o próximo objetivo na pilha se houver.
                if not self.objective_stack: break
                continue

            # Fase 3: Engenheiro de Código - Gera código para cada ação e aplica em memória
            if not self._run_code_engineer_phase_and_apply():
                # _run_code_engineer_phase_and_apply já deve ter setado validation_result com falha.
                # A lógica de correção abaixo cuidará disso.
                print("Falha na fase de Engenharia de Código ou aplicação em memória.")
                # Não precisa de 'break' ou 'continue' aqui, a lógica de falha abaixo tratará.
                pass # Deixa a lógica de tratamento de falhas abaixo lidar com isso

            # Fase de Decisão do Maestro (após plano e possível geração de código)
            # Se _run_code_engineer_phase_and_apply falhou, o Maestro ainda pode ser consultado
            # para decidir se a falha é por CAPACITATION ou outra coisa, embora
            # o estado de `validation_result` já indique uma falha.
            # Vamos rodar o Maestro mesmo se a engenharia falhou, para o caso de CAPACITATION.
            if not self._run_maestro_phase():
                print("Falha na fase do Maestro. Tentando próximo objetivo se houver.")
                # Similar ao Arquiteto, tratar erro.
                if not self.objective_stack: break
                continue

            # Lidar com CAPACITATION_REQUIRED primeiro, pois desvia o fluxo
            if self.state["strategy_key"] == "CAPACITATION_REQUIRED":
                print("Maestro identificou a necessidade de uma nova capacidade.")
                self.objective_stack.append(current_objective) # Devolve o objetivo atual à pilha

                architect_analysis = self.state.get("action_plan_data", {}).get("analysis",
                                        "Nenhuma análise do arquiteto disponível para gerar objetivo de capacitação.")
                
                capacitation_objective_model = self.config.get("models", {}).get("capacitation_generator", self.light_model)
                capacitation_objective = generate_capacitation_objective(
                    self.api_key,
                    capacitation_objective_model,
                    architect_analysis # Passa a análise do arquiteto
                )
                print(f"Gerado novo objetivo de capacitação: {capacitation_objective}")
                self.objective_stack.append(capacitation_objective) # Adiciona novo objetivo no topo
                continue # Pula para o próximo ciclo com o objetivo de capacitação

            # Executar a estratégia de validação (que pode incluir persistência)
            # Só executa se não houve falha na engenharia de código que já setou validation_result
            # ou se o Maestro não pediu capacitação.
            # Se _run_code_engineer_phase_and_apply falhou, validation_result já está com erro.
            current_val_success, _, _ = self.state.get("validation_result", (False, "", ""))
            if not current_val_success: # Se já falhou (ex: CODE_GENERATION_FAILED)
                 print("Pulando execução da estratégia de validação devido a falha anterior no ciclo.")
            else:
                self._execute_validation_strategy()

            # Obter resultado final da validação para o ciclo
            success, reason, context = self.state.get("validation_result",
                                                      (False, "UNKNOWN_ERROR", "Resultado da validação não encontrado"))

            # Lógica Pós-Ciclo
            if success:
                print(f"\nSUCESSO NO CICLO! Razão: {reason}")
                # Se APPLIED_AND_VALIDATED, significa que as mudanças foram persistidas e validadas.
                if reason == "APPLIED_AND_VALIDATED":
                    print("--- INICIANDO CICLO DE VERIFICAÇÃO DE SANIDADE PÓS-APLICAÇÃO ---")
                    current_strategy_key = self.state.get("strategy_key")
                    strategy_config = self.config["validation_strategies"].get(current_strategy_key, {})
                    sanity_check_tool_name = strategy_config.get("sanity_check_step", "run_pytest")

                    sanity_check_success = True
                    sanity_check_details = "Nenhuma verificação de sanidade executada."

                    if sanity_check_tool_name == "run_pytest":
                        print(f"Executando verificação de sanidade com: {sanity_check_tool_name}")
                        sanity_check_success, sanity_check_details = run_pytest(test_dir='tests/')
                    elif sanity_check_tool_name == "check_file_existence":
                        print(f"Executando verificação de sanidade com: {sanity_check_tool_name}")
                        # Verificar arquivos que foram efetivamente escritos/modificados
                        files_to_check = list(self.state.get("applied_files_report", {}).keys())
                        if files_to_check:
                            sanity_check_success, sanity_check_details = check_file_existence(files_to_check)
                        else:
                            sanity_check_success = True
                            sanity_check_details = "Nenhum arquivo foi reportado como aplicado para verificação de existência."
                            print(sanity_check_details)
                    elif sanity_check_tool_name == "skip_sanity_check":
                        sanity_check_success = True
                        sanity_check_details = "Verificação de sanidade pulada conforme configuração."
                        print(sanity_check_details)
                    else:
                        sanity_check_success = False
                        sanity_check_details = f"Ferramenta de verificação de sanidade desconhecida: {sanity_check_tool_name}"
                        print(f"AVISO: {sanity_check_details}")

                    if not sanity_check_success:
                        print(f"FALHA NA VERIFICAÇÃO DE SANIDADE PÓS-APLICAÇÃO ({sanity_check_tool_name})!\nDetalhes: {sanity_check_details}")
                        reason = f"REGRESSION_DETECTED_BY_{sanity_check_tool_name.upper()}"
                        context = sanity_check_details
                        success = False # Reverte o sucesso do ciclo para entrar no bloco de correção
                    else:
                        print(f"VERIFICAÇÃO DE SANIDADE PÓS-APLICAÇÃO ({sanity_check_tool_name}): SUCESSO!")
                        if sanity_check_tool_name != "skip_sanity_check":
                            print("Ressincronizando manifesto (após sucesso e sanidade)...")
                            # Atualizar manifesto com base nos arquivos que foram realmente alterados
                            # Se self.state["in_memory_files"] reflete o estado final, podemos usar suas chaves.
                            # Ou, se a estratégia envolveu escrita, podemos escanear tudo.
                            # Por segurança, escanear tudo.
                            update_project_manifest(root_dir=".", target_files=[])
                            with open("AGENTS.md", "r", encoding="utf-8") as f: # Recarregar manifesto
                                self.state["manifesto_content"] = f.read()

                        print("Gerando próximo objetivo evolutivo...")
                        objective_model = self.config.get("models", {}).get("objective_generator", self.light_model)
                        next_obj = generate_next_objective(self.api_key, objective_model, self.state["manifesto_content"])
                        self.objective_stack.append(next_obj)
                        print(f"Próximo objetivo: {next_obj}")

                elif reason == "DISCARDED" or reason == "VALIDATED_ONLY":
                    # Se foi descartado ou apenas validado (sem aplicação), gerar próximo objetivo.
                    print(f"Alterações {reason}. Gerando próximo objetivo evolutivo...")
                    objective_model = self.config.get("models", {}).get("objective_generator", self.light_model)
                    next_obj = generate_next_objective(self.api_key, objective_model, self.state["manifesto_content"])
                    self.objective_stack.append(next_obj)
                    print(f"Próximo objetivo: {next_obj}")

            # Se o sucesso foi revertido pela falha na verificação de sanidade, ou outra falha corrigível do ciclo
            # Falhas como CODE_GENERATION_FAILED, IN_MEMORY_APPLY_FAILED, PERSISTENCE_FAILED, PYTEST_FAILURE
            # ou as de REGRESSION_DETECTED...
            # Definir as razões de falha corrigíveis
            correctable_failure_reasons = {
                "CODE_GENERATION_FAILED", "IN_MEMORY_APPLY_FAILED",
                "PERSISTENCE_FAILED", "PYTEST_FAILURE"
            }
            # Adicionar dinamicamente a razão de regressão se sanity_check_tool_name estiver definido
            if 'sanity_check_tool_name' in locals() and sanity_check_tool_name:
                correctable_failure_reasons.add(f"REGRESSION_DETECTED_BY_{sanity_check_tool_name.upper()}")

            if not success and reason in correctable_failure_reasons:
                print(f"\nFALHA CORRIGÍVEL NO CICLO! Razão: {reason}\nContexto: {context}")
                self.objective_stack.append(current_objective) # Devolve o objetivo original à pilha
                
                # Gerar objetivo de correção
                correction_obj_text = f"""
[TAREFA DE CORREÇÃO AUTOMÁTICA]
A tentativa anterior de alcançar o objetivo falhou.
OBJETIVO ORIGINAL:
{current_objective}
FALHA ENCONTRADA: {reason}
DETALHES DO ERRO/CONTEXTO:
{context}
PLANO DE AÇÃO ORIGINAL DO ARQUITETO (SE DISPONÍVEL):
{json.dumps(self.state.get("action_plan_data", {}).get("action_plan", "N/A"), indent=2)}
Sua nova missão é analisar o erro e o plano original, e então gerar um NOVO PLANO DE AÇÃO para corrigir o problema e alcançar o objetivo original.
Se a falha foi na geração de código para uma ação específica, foque em refinar a 'content_description' dessa ação ou quebre-a em sub-ações menores.
Se a falha foi numa validação (ex: Pytest), o novo plano deve visar corrigir o código que causou a falha.
"""
                # Adicionar o objetivo de correção ao topo da pilha
                self.objective_stack.append(correction_obj_text)
                print(f"Gerado novo objetivo de correção e adicionado à pilha.")

            elif not success: # Falhas não explicitamente corrigíveis ou desconhecidas
                print(f"\nFALHA NÃO RECUPERÁVEL OU DESCONHECIDA. Razão: {reason}. Contexto: {context}. Encerrando.")
                break # Encerra o loop principal

            print(f"{'='*20} FIM DO CICLO {'='*20}")
            # Pausa para permitir leitura do console, pode ser ajustada ou removida
            time.sleep(self.config.get("cycle_delay_seconds", 5))


if __name__ == "__main__":
    agent = HephaestusAgent()
    agent.run()
