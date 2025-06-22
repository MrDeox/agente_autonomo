import json
import os
import shutil
import tempfile
import time
from pathlib import Path
from dotenv import load_dotenv

from agent.project_scanner import update_project_manifest
from agent.brain import get_ai_suggestion, get_maestro_decision, generate_next_objective
from agent.file_manager import apply_changes
from agent.code_validator import validate_python_code, validate_json_syntax
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
            "parsed_json": None,
            "files_to_update": [],
            "test_code": "",
            "model_used": None,
            "strategy_key": None,
            "validation_result": (False, "PENDING", "Ciclo não iniciado"),
            "apply_report": None
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


    def _run_engineer_phase(self) -> bool:
        """Executa a fase de engenharia com sugestão da IA."""
        print("\nSolicitando análise da IA (Engenheiro)...")
        attempt_logs = get_ai_suggestion(
            api_key=self.api_key,
            model_list=self.model_list,
            project_snapshot=self.state["manifesto_content"],
            objective=self.state["current_objective"],
        )
        successful_attempt = next((a for a in attempt_logs if a.get("success")), None)
        if not successful_attempt or not successful_attempt.get("parsed_json"):
            print("--- FALHA: Engenheiro não retornou uma resposta JSON válida. ---")
            return False

        parsed_json = successful_attempt["parsed_json"]
        self.state.update({
            "parsed_json": parsed_json,
            "model_used": successful_attempt["model"],
            "files_to_update": parsed_json.get("files_to_update", []),
            "test_code": (parsed_json.get("validation_pytest_code") or "").strip()
        })
        print(f"--- ANÁLISE DA IA ({self.state['model_used']}) ---")
        print(parsed_json.get("analysis_summary", "Nenhuma análise fornecida."))
        return True

    def _run_maestro_phase(self) -> bool:
        """Executa a fase de decisão do maestro."""
        print("\nSolicitando decisão do Maestro...")
        maestro_logs = get_maestro_decision(
            api_key=self.api_key, model_list=self.model_list,
            engineer_response=self.state["parsed_json"], config=self.config,
        )
        maestro_attempt = next((a for a in maestro_logs if a.get("success")), None)
        if not maestro_attempt or not maestro_attempt.get("parsed_json"):
            print("--- FALHA: Maestro não retornou uma resposta JSON válida. ---")
            return False
        
        decision = maestro_attempt["parsed_json"]
        strategy_key = (decision.get("strategy_key") or "").strip()
        if strategy_key not in self.config.get("validation_strategies", {}):
            print(f"--- FALHA: Maestro escolheu uma estratégia inválida: '{strategy_key}' ---")
            return False

        print(f"Estratégia escolhida pelo Maestro: {strategy_key}")
        self.state["strategy_key"] = strategy_key
        return True

    def _execute_validation_strategy(self) -> None:
        """Executa os passos de validação conforme a estratégia escolhida."""
        strategy = self.config["validation_strategies"].get(self.state["strategy_key"], {})
        steps = strategy.get("steps", [])
        print(f"\nExecutando estratégia '{self.state['strategy_key']}' com os passos: {steps}")

        for step_name in steps:
            print(f"--- Passo: {step_name} ---")
            # Validação de Sintaxe
            if step_name == "validate_syntax" or step_name == "validate_json_syntax":
                is_valid, error = (False, "Nenhum arquivo para validar")
                for file_update in self.state["files_to_update"]:
                    content = file_update["new_content"]
                    if file_update["file_path"].endswith(".py"):
                        is_valid, error = validate_python_code(content)
                    elif file_update["file_path"].endswith(".json"):
                         is_valid, error = validate_json_syntax(content)
                    
                    if not is_valid:
                        context = f"Arquivo alvo: {file_update['file_path']}\nErro: {error}"
                        self.state["validation_result"] = (False, "SYNTAX_ERROR", context)
                        return
                print("Validação de sintaxe OK.")
            
            # Validação com Pytest
            elif step_name == "run_pytest_validation":
                # Lógica do pytest... (pode ser adicionada aqui se necessário)
                print("Passo de Pytest executado (simulado).")

            # Validação com Benchmark
            elif step_name == "run_benchmark_validation":
                # Lógica do benchmark... (pode ser adicionada aqui se necessário)
                print("Passo de Benchmark executado (simulado).")
                
            # Aplicação das Mudanças
            elif step_name == "apply_changes":
                print("Aplicando mudanças...")
                report = apply_changes(self.state["files_to_update"])
                self.state["apply_report"] = report
                if report["status"] != "success":
                    self.state["validation_result"] = (False, "APPLY_FAILED", "\n".join(report.get("errors", [])))
                    return
                print("Mudanças aplicadas com sucesso.")

        # Se todos os passos da estratégia passaram
        if self.state["strategy_key"] != "DISCARD":
            self.state["validation_result"] = (True, "APPLIED", "Estratégia concluída e mudanças aplicadas.")
        else:
            self.state["validation_result"] = (True, "DISCARDED", "Estratégia de descarte executada.")


    def run(self) -> None:
        """Executa o ciclo de vida completo do agente de forma perpétua."""
        if not self.api_key:
            print("Erro: OPENROUTER_API_KEY não encontrada. Encerrando.")
            return

        # Initialize with first objective if stack is empty
        if not self.objective_stack:
            print("Gerando objetivo inicial...")
            initial_objective = generate_next_objective(self.api_key, self.light_model, "")
            self.objective_stack.append(initial_objective)
            print(f"Objetivo inicial: {initial_objective}")

        while self.objective_stack:
            current_objective = self.objective_stack.pop()
            print(f"\n\n{'='*20} NOVO CICLO DE EVOLUÇÃO {'='*20}")
            print(f"OBJETIVO ATUAL: {current_objective}\n")
            self.state["current_objective"] = current_objective

            self._reset_cycle_state() # Reseta o estado do ciclo anterior

            if not self._generate_manifest(): break
            if not self._run_engineer_phase(): break
            if not self._run_maestro_phase(): break

            # Handle CAPACITATION_REQUIRED
            if self.state["strategy_key"] == "CAPACITATION_REQUIRED":
                print("Maestro identificou a necessidade de uma nova capacidade.")
                # Save current objective
                self.objective_stack.append(current_objective)
                
                # Generate capacitation objective
                capacitation_objective = generate_capacitation_objective(
                    self.api_key,
                    self.light_model,
                    self.state["parsed_json"]["analysis_summary"]
                )
                print(f"Gerado novo objetivo de capacitação: {capacitation_objective}")
                
                # Add to top of stack
                self.objective_stack.append(capacitation_objective)
                continue

            self._execute_validation_strategy()
            success, reason, context = self.state.get("validation_result", (False, "UNKNOWN_ERROR", "Resultado da validação não encontrado"))

            # Lógica Pós-Ciclo
            if success:
                print(f"\nSUCESSO NO CICLO! Razão: {reason}")
                if reason == "APPLIED":
                    print("--- INICIANDO CICLO DE VERIFICAÇÃO DE SANIDADE ---")

                    current_strategy_key = self.state.get("strategy_key")
                    strategy_config = self.config["validation_strategies"].get(current_strategy_key, {})
                    sanity_check_tool_name = strategy_config.get("sanity_check_step", "run_pytest") # Default to run_pytest

                    sanity_check_success = True
                    sanity_check_details = "Nenhuma verificação de sanidade executada."

                    if sanity_check_tool_name == "run_pytest":
                        print(f"Executando verificação de sanidade com: {sanity_check_tool_name}")
                        # Aqui podemos adicionar lógica para interpretar o exit code 5 de run_pytest se necessário
                        # Por exemplo, se run_pytest retornasse um dict com 'exit_code'
                        # sanity_check_success, sanity_check_details = run_pytest(test_dir='tests/')
                        # if sanity_check_details.startswith("Exit Code: 5"):
                        #    print("Pytest não encontrou testes (Exit Code 5). Considerando como sucesso para este contexto.")
                        #    # Potencialmente tratar como sucesso ou um tipo específico de aviso
                        # else: # outro erro ou sucesso real
                        #    pass # segue a lógica normal
                        sanity_check_success, sanity_check_details = run_pytest(test_dir='tests/')
                    elif sanity_check_tool_name == "check_file_existence":
                        print(f"Executando verificação de sanidade com: {sanity_check_tool_name}")
                        files_to_check = [f_update["file_path"] for f_update in self.state.get("files_to_update", []) if "file_path" in f_update]
                        if files_to_check:
                            sanity_check_success, sanity_check_details = check_file_existence(files_to_check)
                        else:
                            sanity_check_success = False # Ou True, dependendo da interpretação desejada
                            sanity_check_details = "Nenhum arquivo foi marcado para atualização, verificação de existência não aplicável."
                            print(sanity_check_details)
                    elif sanity_check_tool_name == "skip_sanity_check":
                        sanity_check_success = True # Sempre sucesso se pulado
                        sanity_check_details = "Verificação de sanidade pulada conforme configuração."
                        print(sanity_check_details)
                    else:
                        sanity_check_success = False # Ferramenta desconhecida é uma falha
                        sanity_check_details = f"Ferramenta de verificação de sanidade desconhecida: {sanity_check_tool_name}"
                        print(f"AVISO: {sanity_check_details}")

                    if not sanity_check_success:
                        print(f"FALHA NA VERIFICAÇÃO DE SANIDADE PÓS-APLICAÇÃO ({sanity_check_tool_name})!\nDetalhes: {sanity_check_details}")
                        reason = f"REGRESSION_DETECTED_BY_{sanity_check_tool_name.upper()}"
                        context = sanity_check_details
                        success = False # Marcar como falha para entrar no bloco de correção
                    else:
                        print(f"VERIFICAÇÃO DE SANIDADE PÓS-APLICAÇÃO ({sanity_check_tool_name}): SUCESSO!")
                        if sanity_check_tool_name != "skip_sanity_check": # Não resincronizar se foi pulado
                            print("Ressincronizando manifesto...")
                            update_project_manifest(root_dir=".", target_files=[])

                        print("Gerando próximo objetivo evolutivo...")
                        next_obj = generate_next_objective(self.api_key, self.light_model, self.state["manifesto_content"])
                        self.objective_stack.append(next_obj)
                        print(f"Próximo objetivo: {next_obj}")

                elif reason == "DISCARDED":
                    # Se foi descartado, não precisa de sanidade, só gerar próximo objetivo
                    # A estratégia DISCARD também pode ter sanity_check_step: "skip_sanity_check"
                    print("Alterações descartadas. Gerando próximo objetivo evolutivo...")
                    next_obj = generate_next_objective(self.api_key, self.light_model, self.state["manifesto_content"])
                    self.objective_stack.append(next_obj)
                    print(f"Próximo objetivo: {next_obj}")

            # Se o sucesso foi revertido pela falha na verificação de sanidade, ou outra falha corrigível
            if not success and reason in {
                "SYNTAX_ERROR", "PYTEST_FAILURE", "APPLY_FAILED",
                "REGRESSION_DETECTED_BY_RUN_PYTEST",
                "REGRESSION_DETECTED_BY_CHECK_FILE_EXISTENCE",
                "REGRESSION_DETECTED_BY_SANITY_CHECK" # Genérico, caso a ferramenta não seja específica
            }:
                print(f"\nFALHA CORRIGÍVEL NO CICLO! Razão: {reason}\nContexto: {context}")
                # Save current objective to stack
                self.objective_stack.append(current_objective)
                
                # Generate correction objective
                correction_obj_text = f"""
[TAREFA DE CORREÇÃO]
A tentativa anterior de alcançar o objetivo falhou.
OBJETIVO ORIGINAL:
{current_objective}
FALHA ENCONTRADA: {reason}
DETALHES DO ERRO:
{context}
Sua nova missão é analisar o erro e propor uma correção.
"""
                self.objective_stack.append(correction_obj_text)
                # Definir o objetivo atual para o ciclo de correção (não é estritamente necessário aqui, mas bom para clareza)
                # self.state["current_objective"] = correction_obj_text
                print(f"Gerado novo objetivo de correção e adicionado à pilha.")

            elif not success: # Falhas não corrigíveis
                print(f"\nFALHA NÃO RECUPERÁVEL. Razão: {reason}. Encerrando.")
                break # Encerra o loop

            print(f"{'='*20} FIM DO CICLO {'='*20}")
            time.sleep(5) # Pausa para podermos ler


if __name__ == "__main__":
    agent = HephaestusAgent()
    agent.run()
