import json
import os
import shutil
import tempfile
import time
import logging # ADICIONADO
from pathlib import Path
from dotenv import load_dotenv

from agent.project_scanner import update_project_manifest
# Removida a duplicata de import project_scanner
from agent.brain import (
    get_action_plan,
    get_maestro_decision,
    generate_next_objective,
    generate_capacitation_objective,
    generate_commit_message # ADICIONADO para auto-versionamento
)
# from agent.patch_applicator import apply_patches # Será substituído por manipulação em memória
# AGORA: from agent.patch_applicator import apply_patches # Será usado com o novo patch_applicator
from agent.code_validator import validate_python_code, validate_json_syntax # Reavaliar uso
from agent.tool_executor import run_in_sandbox, run_pytest, check_file_existence, run_git_command # ADICIONADO run_git_command

# Importar o novo patch_applicator
from agent.patch_applicator import apply_patches # ADICIONADO

# Configuração do Logging
logger = logging.getLogger(__name__) # ADICIONADO

class HephaestusAgent:
    """Classe principal que encapsula a lógica do agente autônomo."""

    def __init__(self, logger_instance): # MODIFICADO
        """Inicializa o agente com configuração."""
        self.logger = logger_instance # ADICIONADO
        self.config = self.load_config()
        self.api_key = os.getenv("OPENROUTER_API_KEY")
        self.model_list = [
            "deepseek/deepseek-chat-v3-0324:free",
            "deepseek/deepseek-r1-0528:free"
        ]
        self.light_model = "deepseek/deepseek-chat-v3-0324:free"
        self.state = {}
        self.objective_stack = []  # Pilha de objetivos
        self._reset_cycle_state() # Inicializa o estado

    def _initialize_git_repository(self) -> bool:
        """
        Verifica se um repositório Git existe. Se não, inicializa-o,
        configura o usuário e faz um commit inicial com .gitignore.
        Retorna True se o repositório estiver pronto, False em caso de erro crítico.
        """
        git_dir = Path(".git")
        if git_dir.is_dir():
            self.logger.info("Repositório Git já existe.")
            # Verificar se user.name e user.email estão configurados
            check_user_name_success, _ = run_git_command(['git', 'config', 'user.name'])
            check_user_email_success, _ = run_git_command(['git', 'config', 'user.email'])

            if not (check_user_name_success and check_user_email_success):
                self.logger.warning("Git user.name ou user.email não configurados. Tentando configurar localmente.")
                name_success, name_out = run_git_command(['git', 'config', '--local', 'user.name', 'Hephaestus Agent'])
                email_success, email_out = run_git_command(['git', 'config', '--local', 'user.email', 'hephaestus@example.com'])
                if not (name_success and email_success):
                    self.logger.error(f"FALHA CRÍTICA ao configurar git user.name/email localmente. Name: {name_out}, Email: {email_out}")
                    return False
                self.logger.info("Git user.name e user.email configurados localmente com sucesso.")
            return True

        self.logger.info("Repositório Git não encontrado. Inicializando...")

        # 1. git init
        init_success, init_output = run_git_command(['git', 'init'])
        self.logger.debug(f"Resultado 'git init': Success={init_success}, Output:\n{init_output}")
        if not init_success:
            self.logger.error(f"FALHA CRÍTICA: 'git init' falhou. Output:\n{init_output}")
            return False
        self.logger.info("Repositório Git inicializado com sucesso.")

        # 2. Configurar user.name e user.email (localmente para este repo)
        self.logger.info("Configurando user.name e user.email para o repositório local...")
        name_config_cmd = ['git', 'config', '--local', 'user.name', 'Hephaestus Agent']
        email_config_cmd = ['git', 'config', '--local', 'user.email', 'hephaestus@example.com']

        name_success, name_out = run_git_command(name_config_cmd)
        if not name_success:
            self.logger.error(f"FALHA CRÍTICA ao configurar git user.name. Output:\n{name_out}")
            return False

        email_success, email_out = run_git_command(email_config_cmd)
        if not email_success:
            self.logger.error(f"FALHA CRÍTICA ao configurar git user.email. Output:\n{email_out}")
            return False
        self.logger.info("Git user.name e user.email configurados localmente.")

        # 3. Criar .gitignore
        gitignore_content = """
# Byte-compiled / optimized / DLL files
__pycache__/
*.pyc
*.$py.class

# C extensions
*.so

# Distribution / packaging
.Python
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
wheels/
pip-wheel-metadata/
share/python-wheels/
*.egg-info/
.installed.cfg
*.egg
MANIFEST

# PyInstaller
#  Usually these files are written by a python script from a template
#  before PyInstaller builds the exe, so as to inject date/other infos into it.
*.manifest
*.spec

# Installer logs
pip-log.txt
pip-delete-this-directory.txt

# Unit test / coverage reports
htmlcov/
.tox/
.nox/
.coverage
.coverage.*
.cache
nosetests.xml
coverage.xml
*.cover
*.py,cover
.hypothesis/
.pytest_cache/

# Translations
*.mo
*.pot

# Django stuff:
*.log
local_settings.py
db.sqlite3
db.sqlite3-journal

# Flask stuff:
instance/
.webassets-cache

# Scrapy stuff:
.scrapy

# Sphinx documentation
docs/_build/

# PyBuilder
target/

# Jupyter Notebook
.ipynb_checkpoints

# IPython
profile_default/
ipython_config.py

# pyenv
.python-version

# PEP 582; __pypackages__
__pypackages__/

# Celery stuff
celerybeat-schedule
celerybeat.pid

# SageMath parsed files
*.sage.py

# Environments
.env
.venv
env/
venv/
ENV/
env.bak/
venv.bak/

# Spyder project settings
.spyderproject
.spyderworkspace

# Rope project settings
.ropeproject

# mkdocs documentation
/site

# mypy
.mypy_cache/
.dmypy.json
dmypy.json

# Pyre type checker
.pyre/

# Hephaestus specific
hephaestus.log
*.DS_Store
"""
        gitignore_path = Path(".gitignore")
        try:
            with open(gitignore_path, "w", encoding="utf-8") as f:
                f.write(gitignore_content.strip())
            self.logger.info(f"{gitignore_path} criado com sucesso.")
        except IOError as e:
            self.logger.error(f"FALHA CRÍTICA ao criar {gitignore_path}: {e}")
            return False

        # 4. git add .gitignore
        add_success, add_output = run_git_command(['git', 'add', str(gitignore_path)])
        self.logger.debug(f"Resultado 'git add .gitignore': Success={add_success}, Output:\n{add_output}")
        if not add_success:
            self.logger.error(f"FALHA CRÍTICA: 'git add {gitignore_path}' falhou. Output:\n{add_output}")
            # Se o .gitignore já existir e estiver igual, 'git add' pode não fazer nada, mas não deve falhar.
            # Uma falha aqui é provavelmente um problema mais sério.
            return False

        # 5. git commit -m "chore: Initial commit"
        commit_message = "chore: Initial commit by Hephaestus Agent"
        # Usar --allow-empty se o .gitignore for a única coisa e já estiver no HEAD de alguma forma (improvável aqui)
        # ou se quisermos garantir um commit inicial mesmo que vazio.
        # No entanto, o add anterior deve garantir que há algo para commitar se o .gitignore foi criado/modificado.
        commit_success, commit_output = run_git_command(['git', 'commit', '-m', commit_message])
        self.logger.debug(f"Resultado 'git commit': Success={commit_success}, Output:\n{commit_output}")
        if not commit_success:
            # Verificar se o commit falhou porque não há nada para commitar
            if "nothing to commit" in commit_output.lower() or "nada a submeter" in commit_output.lower() or "no changes added to commit" in commit_output.lower():
                self.logger.warning(f"'git commit' informou que não há nada novo para commitar. Output:\n{commit_output}")
                self.logger.info("Considerando a inicialização do Git como bem-sucedida, pois o estado desejado (repo inicializado com commit inicial) foi alcançado ou já existia.")
            else:
                self.logger.error(f"FALHA CRÍTICA: 'git commit' inicial falhou. Output:\n{commit_output}")
                return False

        self.logger.info("Commit inicial realizado com sucesso ou já existente.")
        return True

    def _reset_cycle_state(self):
        """Reseta o estado transitório do ciclo, mantendo apenas o objetivo atual."""
        # Preserva apenas o current_objective entre os ciclos
        current_objective = self.state.get("current_objective")
        self.state = {
            "current_objective": current_objective,
            "manifesto_content": "",
            "action_plan_data": None,
            "in_memory_files": {},
            "model_architect": None,
            "model_code_engineer": None,
            "strategy_key": None,
            "validation_result": (False, "PENDING", "Ciclo não iniciado"),
            "applied_files_report": {}
        }
        # Reseta variáveis de ciclo que não devem persistir
        self.objective_stack = [obj for obj in self.objective_stack if obj != current_objective]

    @staticmethod
    def load_config() -> dict:
        """Carrega o arquivo de configuração do agente."""
        with open("hephaestus_config.json", "r", encoding="utf-8") as f:
            return json.load(f)

    def _generate_manifest(self) -> bool:
        """Gera o manifesto do projeto."""
        self.logger.info("Gerando manifesto do projeto (AGENTS.md)...")
        try:
            target_files = []
            if self.state["current_objective"] and "project_scanner.py" in self.state["current_objective"]:
                target_files.append("agent/project_scanner.py")
            update_project_manifest(root_dir=".", target_files=target_files)
            with open("AGENTS.md", "r", encoding="utf-8") as f:
                self.state["manifesto_content"] = f.read()
            self.logger.info(f"--- MANIFESTO GERADO (Tamanho: {len(self.state['manifesto_content'])} caracteres) ---")
            return True
        except Exception as e:
            self.logger.error(f"ERRO CRÍTICO ao gerar manifesto: {e}", exc_info=True)
            return False

    def _get_file_content_from_memory_or_disk(self, file_path: str) -> list[str] | None: # MODIFICADO Optional para | None
        """Obtém o conteúdo do arquivo da memória, se existir, senão do disco."""
        if file_path in self.state["in_memory_files"]:
            self.logger.debug(f"Lendo {file_path} da memória.")
            return self.state["in_memory_files"][file_path]
        try:
            self.logger.debug(f"Lendo {file_path} do disco.")
            with open(file_path, "r", encoding="utf-8") as f:
                return f.read().splitlines()
        except FileNotFoundError:
            self.logger.warn(f"Arquivo {file_path} não encontrado no disco.")
            return None
        except Exception as e:
            self.logger.error(f"Erro ao ler arquivo {file_path} do disco: {e}", exc_info=True)
            return None

    # _write_files_from_memory_to_disk será substituído pela lógica de apply_patches
    # A função apply_patches (a ser criada em patch_applicator.py) cuidará da escrita.

    # _apply_action_to_in_memory_files será removido pois o novo patch_applicator.py
    # lidará com a aplicação de patches diretamente nos arquivos (ou em cópias temporárias antes da persistência)

    def _run_architect_phase(self) -> bool:
        """Fase 2: Arquiteto gera o plano de ação (patches)."""
        self.logger.info("\nSolicitando plano de ação da IA (Arquiteto)...")
        architect_model = self.config.get("models", {}).get("architect_default", self.model_list[0])
        self.state["model_architect"] = architect_model

        action_plan_data, error_msg = get_action_plan( # Esta função precisará ser ajustada em brain.py para gerar patches
            api_key=self.api_key,
            model=architect_model,
            objective=self.state["current_objective"],
            manifest=self.state["manifesto_content"],
            logger=self.logger # Passando o logger
        )
        if error_msg:
            self.logger.error(f"--- FALHA: Arquiteto não conseguiu gerar um plano de ação. Erro: {error_msg} ---")
            return False
        # A validação do formato do plano (patches_to_apply) será feita após a chamada
        if not action_plan_data or "patches_to_apply" not in action_plan_data: # MODIFICADO para patches_to_apply
            self.logger.error(f"--- FALHA: Arquiteto retornou uma resposta inválida ou sem 'patches_to_apply'. Resposta: {action_plan_data} ---")
            return False

        self.state["action_plan_data"] = action_plan_data # Armazena toda a resposta do arquiteto
        self.logger.info(f"--- PLANO DE AÇÃO (PATCHES) GERADO PELO ARQUITETO ({architect_model}) ---")
        self.logger.debug(f"Análise do Arquiteto: {action_plan_data.get('analysis', 'Nenhuma análise fornecida.')}")
        self.logger.debug(f"Patches: {json.dumps(action_plan_data.get('patches_to_apply', []), indent=2)}")
        return True

    # _run_code_engineer_phase_and_apply será removido. O Arquiteto agora gera os patches diretamente.
    # A aplicação dos patches ocorrerá na fase de _execute_validation_strategy se a estratégia incluir persistência.

    def _run_maestro_phase(self) -> bool:
        """Executa a fase de decisão do maestro."""
        self.logger.info("\nSolicitando decisão do Maestro...")
        if not self.state.get("action_plan_data"): # O plano do arquiteto (com patches)
            self.logger.error("--- FALHA: Nenhum plano de ação (patches) disponível para o Maestro avaliar. ---")
            return False

        maestro_model = self.config.get("models", {}).get("maestro_default", self.model_list[0])

        maestro_logs = get_maestro_decision(
            api_key=self.api_key, model_list=[maestro_model],
            engineer_response=self.state["action_plan_data"], # Passando o plano do arquiteto com patches
            config=self.config
        )
        maestro_attempt = next((a for a in maestro_logs if a.get("success")), None)
        if not maestro_attempt or not maestro_attempt.get("parsed_json"):
            self.logger.error("--- FALHA: Maestro não retornou uma resposta JSON válida. ---")
            raw_resp = maestro_attempt.get("raw_response") if maestro_attempt else "Nenhuma tentativa registrada."
            self.logger.debug(f"Resposta bruta do Maestro: {raw_resp}")
            return False
        
        decision = maestro_attempt["parsed_json"]
        strategy_key = (decision.get("strategy_key") or "").strip()

        valid_strategies = list(self.config.get("validation_strategies", {}).keys())
        valid_strategies.append("CAPACITATION_REQUIRED")

        if strategy_key not in valid_strategies:
            self.logger.error(f"--- FALHA: Maestro escolheu uma estratégia inválida ou desconhecida: '{strategy_key}' ---")
            self.logger.debug(f"Estratégias válidas são: {valid_strategies}")
            return False

        self.logger.info(f"Estratégia escolhida pelo Maestro: {strategy_key}")
        self.state["strategy_key"] = strategy_key
        return True

    def _execute_validation_strategy(self) -> None:
        """Executa os passos de validação conforme a estratégia escolhida, incluindo aplicação de patches."""
        strategy_key = self.state["strategy_key"]
        strategy_config = self.config["validation_strategies"].get(strategy_key, {})
        steps = strategy_config.get("steps", [])
        self.logger.info(f"\nExecutando estratégia '{strategy_key}' com os passos: {steps}")

        self.state["validation_result"] = (False, "STRATEGY_PENDING", f"Iniciando estratégia {strategy_key}")

        # Os patches são obtidos do estado, onde foram colocados pela fase do arquiteto
        patches_to_apply = self.state.get("action_plan_data", {}).get("patches_to_apply", [])

        for step_name in steps:
            self.logger.info(f"--- Passo de Validação/Execução: {step_name} ---")
            
            if step_name == "apply_patches_to_disk": # NOVO PASSO para aplicar patches
                if not patches_to_apply:
                    self.logger.info("Nenhum patch para aplicar. Pulando passo.")
                    continue

                self.logger.info(f"Aplicando {len(patches_to_apply)} patches ao disco...")
                # A função apply_patches (de agent.patch_applicator) fará a escrita.
                # Ela precisa retornar um status e talvez um relatório de arquivos modificados.
                # Por enquanto, vamos supor que ela modifica os arquivos diretamente ou lança exceção.
                try:
                    # `apply_patches` deve ser capaz de lidar com múltiplos patches para diferentes arquivos.
                    # O `base_path` pode ser útil se os file_path nos patches forem relativos a um subdiretório.
                    # Para agora, assumimos que são relativos ao root do projeto.
                    # TODO: Definir o que apply_patches retorna para o relatório.
                    # Por ora, se não lançar exceção, consideramos sucesso parcial.
                    # A validação subsequente (pytest, etc.) confirmará.
                    apply_patches(instructions=patches_to_apply, logger=self.logger, base_path=".") # Chamada ao novo patch_applicator
                    self.logger.info("Patches aplicados com sucesso (tentativa).")
                    # Aqui poderíamos popular self.state["applied_files_report"] se apply_patches retornar info
                    # Por exemplo, applied_files_report = apply_patches(...)
                    # Vamos simular que os arquivos mencionados nos patches foram tentados:
                    self.state["applied_files_report"] = {
                        patch_instr.get("file_path"): {"status": "attempted", "message": "Patch application attempted."}
                        for patch_instr in patches_to_apply if patch_instr.get("file_path")
                    }

                except Exception as e:
                    self.logger.error(f"ERRO CRÍTICO ao aplicar patches: {e}", exc_info=True)
                    self.state["validation_result"] = (False, "PATCH_APPLICATION_FAILED", str(e))
                    return # Interrompe a estratégia

            elif step_name == "validate_syntax": # NOVO PASSO de validação de sintaxe
                if not patches_to_apply:
                    self.logger.info("Nenhum patch aplicado, pulando validação de sintaxe.")
                    continue

                all_syntax_valid = True
                error_details = []
                # Validar apenas os arquivos que foram modificados pelos patches
                # Idealmente, applied_files_report teria os caminhos exatos.
                # Se não, iteramos sobre os patches.
                files_to_validate = {p.get("file_path") for p in patches_to_apply if p.get("file_path")}

                for file_path in files_to_validate:
                    self.logger.debug(f"Validando sintaxe de: {file_path}")
                    if file_path.endswith(".py"):
                        is_valid, msg = validate_python_code(file_path, self.logger) # Passar logger
                        if not is_valid:
                            self.logger.warn(f"Erro de sintaxe Python em {file_path}: {msg}")
                            all_syntax_valid = False
                            error_details.append(f"{file_path}: {msg}")
                    elif file_path.endswith(".json"):
                        is_valid, msg = validate_json_syntax(file_path, self.logger) # Passar logger
                        if not is_valid:
                            self.logger.warn(f"Erro de sintaxe JSON em {file_path}: {msg}")
                            all_syntax_valid = False
                            error_details.append(f"{file_path}: {msg}")
                    else:
                        self.logger.debug(f"Sem validador de sintaxe para: {file_path}")

                if not all_syntax_valid:
                    self.state["validation_result"] = (False, "SYNTAX_VALIDATION_FAILED", "\n".join(error_details))
                    return # Interrompe a estratégia
                self.logger.info("Validação de sintaxe: SUCESSO.")


            elif step_name == "validate_json_syntax": # Este passo específico pode ser redundante se validate_syntax já cobre JSON
                                                      # Mas mantendo por ora se houver lógica diferenciada.
                self.logger.info("Executando validação de sintaxe JSON (se aplicável)...")
                # Esta lógica é similar à de validate_syntax, mas focada em JSON.
                # Se validate_syntax já faz isso, este passo pode ser removido da config.
                # Ou, pode ser usado para validar JSONs específicos que não são código-fonte.
                # Por ora, vamos replicar a lógica de JSON de validate_syntax.
                json_syntax_valid = True
                json_error_details = []
                files_to_validate_json = {p.get("file_path") for p in patches_to_apply if p.get("file_path", "").endswith(".json")}

                for file_path in files_to_validate_json:
                    is_valid, msg = validate_json_syntax(file_path, self.logger)
                    if not is_valid:
                        self.logger.warn(f"Erro de sintaxe JSON em {file_path}: {msg}")
                        json_syntax_valid = False
                        json_error_details.append(f"{file_path}: {msg}")

                if not json_syntax_valid:
                    self.state["validation_result"] = (False, "JSON_SYNTAX_VALIDATION_FAILED", "\n".join(json_error_details))
                    return
                self.logger.info("Validação de sintaxe JSON: SUCESSO (ou nenhum arquivo JSON para validar).")


            elif step_name == "run_pytest_validation":
                self.logger.info("Executando Pytest...")
                success, details = run_pytest(test_dir='tests/')
                if not success:
                    self.logger.warn(f"Falha no Pytest: {details}")
                    self.state["validation_result"] = (False, "PYTEST_FAILURE", details)
                    return
                self.logger.info("Validação Pytest: SUCESSO.")

            elif step_name == "run_benchmark_validation":
                self.logger.info("Passo de Benchmark executado (simulado).")
                # Adicionar lógica real de benchmark aqui se necessário

        # Se todos os passos da estratégia passaram:
        if strategy_key == "DISCARD": # DISCARD significa que os patches não foram aplicados
            self.state["validation_result"] = (True, "DISCARDED", "Estratégia de descarte executada, patches não aplicados.")
        elif "apply_patches_to_disk" in steps:
            # Se apply_patches_to_disk estava nos passos e não falhou E outras validações passaram:
            self.state["validation_result"] = (True, "APPLIED_AND_VALIDATED", f"Estratégia '{strategy_key}' concluída, patches aplicados e validados.")
        else:
            # Se a estratégia não envolvia aplicação de patches (ex: só validação teórica do plano)
            self.state["validation_result"] = (True, "VALIDATED_ONLY", f"Estratégia '{strategy_key}' de validação concluída (sem aplicação de patches).")


    def run(self) -> None:
        """Executa o ciclo de vida completo do agente de forma perpétua."""
        if not self.api_key:
            self.logger.error("Erro: OPENROUTER_API_KEY não encontrada. Encerrando.")
            return

        # Inicializar/Verificar repositório Git ANTES de qualquer outra coisa
        if not self._initialize_git_repository():
            self.logger.error("Falha ao inicializar o repositório Git. O agente não pode continuar sem versionamento.")
            return

        if not self.objective_stack:
            self.logger.info("Gerando objetivo inicial...")
            initial_objective_model = self.config.get("models", {}).get("objective_generator", self.light_model)
            initial_objective = generate_next_objective(self.api_key, initial_objective_model, "", self.logger) # Passar logger
            self.objective_stack.append(initial_objective)
            self.logger.info(f"Objetivo inicial: {initial_objective}")

        while self.objective_stack:
            current_objective = self.objective_stack.pop()
            self.logger.info(f"\n\n{'='*20} NOVO CICLO DE EVOLUÇÃO {'='*20}")
            self.logger.info(f"OBJETIVO ATUAL: {current_objective}\n")

            self._reset_cycle_state()
            self.state["current_objective"] = current_objective

            if not self._generate_manifest():
                self.logger.error("Falha crítica ao gerar manifesto. Encerrando ciclo.")
                break

            if not self._run_architect_phase(): # Arquiteto agora gera patches
                self.logger.warn("Falha na fase do Arquiteto. Tentando próximo objetivo se houver.")
                if not self.objective_stack: break
                continue

            # Fase do Engenheiro de Código foi removida. Patches vêm direto do Arquiteto.

            if not self._run_maestro_phase():
                self.logger.warning("Falha na fase do Maestro. Tentando próximo objetivo se houver.") # CORRIGIDO
                if not self.objective_stack: break
                continue

            if self.state["strategy_key"] == "CAPACITATION_REQUIRED":
                self.logger.info("Maestro identificou a necessidade de uma nova capacidade.")
                self.objective_stack.append(current_objective)

                architect_analysis = self.state.get("action_plan_data", {}).get("analysis",
                                        "Nenhuma análise do arquiteto disponível para gerar objetivo de capacitação.")
                
                capacitation_objective_model = self.config.get("models", {}).get("capacitation_generator", self.light_model)
                capacitation_objective = generate_capacitation_objective(
                    self.api_key,
                    capacitation_objective_model,
                    architect_analysis,
                    self.logger # Passar logger
                )
                self.logger.info(f"Gerado novo objetivo de capacitação: {capacitation_objective}")
                self.objective_stack.append(capacitation_objective)
                continue

            # Executar a estratégia de validação (que agora inclui aplicação de patches)
            self._execute_validation_strategy()

            success, reason, context = self.state.get("validation_result",
                                                      (False, "UNKNOWN_ERROR", "Resultado da validação não encontrado"))

            if success:
                self.logger.info(f"\nSUCESSO NO CICLO! Razão: {reason}")
                if reason == "APPLIED_AND_VALIDATED":
                    self.logger.info("--- INICIANDO CICLO DE VERIFICAÇÃO DE SANIDADE PÓS-APLICAÇÃO ---")
                    current_strategy_key = self.state.get("strategy_key")
                    strategy_config_sanity = self.config["validation_strategies"].get(current_strategy_key, {}) # Renomeada para evitar conflito
                    sanity_check_tool_name = strategy_config_sanity.get("sanity_check_step", "run_pytest")

                    sanity_check_success = True
                    sanity_check_details = "Nenhuma verificação de sanidade executada."

                    if sanity_check_tool_name == "run_pytest":
                        self.logger.info(f"Executando verificação de sanidade com: {sanity_check_tool_name}")
                        sanity_check_success, sanity_check_details = run_pytest(test_dir='tests/')
                    elif sanity_check_tool_name == "check_file_existence":
                        self.logger.info(f"Executando verificação de sanidade com: {sanity_check_tool_name}")
                        files_to_check = list(self.state.get("applied_files_report", {}).keys())
                        if files_to_check:
                            sanity_check_success, sanity_check_details = check_file_existence(files_to_check)
                        else:
                            sanity_check_success = True
                            sanity_check_details = "Nenhum arquivo foi reportado como aplicado para verificação de existência."
                            self.logger.info(sanity_check_details)
                    elif sanity_check_tool_name == "skip_sanity_check":
                        sanity_check_success = True
                        sanity_check_details = "Verificação de sanidade pulada conforme configuração."
                        self.logger.info(sanity_check_details)
                    else:
                        sanity_check_success = False
                        sanity_check_details = f"Ferramenta de verificação de sanidade desconhecida: {sanity_check_tool_name}"
                        self.logger.warn(f"AVISO: {sanity_check_details}")

                    if not sanity_check_success:
                        self.logger.error(f"FALHA NA VERIFICAÇÃO DE SANIDADE PÓS-APLICAÇÃO ({sanity_check_tool_name})!\nDetalhes: {sanity_check_details}")
                        reason = f"REGRESSION_DETECTED_BY_{sanity_check_tool_name.upper()}"
                        context = sanity_check_details
                        success = False
                    else:
                        self.logger.info(f"VERIFICAÇÃO DE SANIDADE PÓS-APLICAÇÃO ({sanity_check_tool_name}): SUCESSO!")
                        if sanity_check_tool_name != "skip_sanity_check":
                            self.logger.info("Ressincronizando manifesto (após sucesso e sanidade)...")
                            update_project_manifest(root_dir=".", target_files=[]) # Escaneia tudo
                            with open("AGENTS.md", "r", encoding="utf-8") as f:
                                self.state["manifesto_content"] = f.read()

                            # --- INÍCIO DO BLOCO DE AUTO-COMMIT ---
                            self.logger.info("Iniciando processo de auto-commit das alterações validadas...")

                            # 1. Gerar mensagem de commit
                            analysis_summary = self.state.get("action_plan_data", {}).get("analysis", "N/A")
                            commit_model = self.config.get("models", {}).get("commit_message_generator", self.light_model)

                            self.logger.debug(f"Dados para msg de commit: Objetivo='{self.state['current_objective']}', Análise='{analysis_summary[:100]}...'")

                            commit_message = generate_commit_message(
                                api_key=self.api_key,
                                model=commit_model,
                                analysis_summary=analysis_summary,
                                objective=self.state["current_objective"],
                                logger=self.logger
                            )
                            self.logger.info(f"Mensagem de commit gerada: '{commit_message}'")

                            # 2. Executar git add .
                            self.logger.info("Adicionando todas as alterações ao staging (git add .)...")
                            add_success, add_output = run_git_command(['git', 'add', '.'])
                            self.logger.debug(f"Resultado 'git add .': Success={add_success}, Output:\n{add_output}")
                            if not add_success:
                                self.logger.error(f"FALHA CRÍTICA: 'git add .' falhou. Output:\n{add_output}")
                                self.logger.error("ENCERRANDO O AGENTE devido à falha no versionamento.")
                                return # Encerra o método run()

                            # 3. Executar git commit
                            self.logger.info(f"Realizando commit com a mensagem: '{commit_message}'...")
                            commit_success, commit_output = run_git_command(['git', 'commit', '-m', commit_message])
                            self.logger.debug(f"Resultado 'git commit': Success={commit_success}, Output:\n{commit_output}")
                            if not commit_success:
                                self.logger.error(f"FALHA CRÍTICA: 'git commit' falhou. Output:\n{commit_output}")
                                self.logger.error("ENCERRANDO O AGENTE devido à falha no versionamento.")
                                # Poderia tentar um 'git reset --hard HEAD' aqui, mas por ora é mais seguro parar.
                                return # Encerra o método run()

                            self.logger.info("--- AUTO-COMMIT REALIZADO COM SUCESSO ---")
                            # --- FIM DO BLOCO DE AUTO-COMMIT ---

                        self.logger.info("Gerando próximo objetivo evolutivo...")
                        objective_model = self.config.get("models", {}).get("objective_generator", self.light_model)
                        next_obj = generate_next_objective(self.api_key, objective_model, self.state["manifesto_content"], self.logger) # Passar logger
                        self.objective_stack.append(next_obj)
                        self.logger.info(f"Próximo objetivo: {next_obj}")

                elif reason == "DISCARDED" or reason == "VALIDATED_ONLY":
                    self.logger.info(f"Alterações {reason}. Gerando próximo objetivo evolutivo...")
                    objective_model = self.config.get("models", {}).get("objective_generator", self.light_model)
                    next_obj = generate_next_objective(self.api_key, objective_model, self.state["manifesto_content"], self.logger) # Passar logger
                    self.objective_stack.append(next_obj)
                    self.logger.info(f"Próximo objetivo: {next_obj}")

            correctable_failure_reasons = {
                "PATCH_APPLICATION_FAILED", "SYNTAX_VALIDATION_FAILED", "JSON_SYNTAX_VALIDATION_FAILED",
                "PYTEST_FAILURE"
            }
            if 'sanity_check_tool_name' in locals() and sanity_check_tool_name: # locals() pode ser problemático, melhor passar explicitamente
                 correctable_failure_reasons.add(f"REGRESSION_DETECTED_BY_{sanity_check_tool_name.upper()}")


            if not success and reason in correctable_failure_reasons:
                self.logger.warn(f"\nFALHA CORRIGÍVEL NO CICLO! Razão: {reason}\nContexto: {context}")
                self.objective_stack.append(current_objective)
                
                # Usar os patches_to_apply do arquiteto em vez do action_plan para o objetivo de correção
                original_patches = self.state.get("action_plan_data", {}).get("patches_to_apply", "N/A")

                correction_obj_text = f"""
[TAREFA DE CORREÇÃO AUTOMÁTICA]
A tentativa anterior de alcançar o objetivo falhou.
OBJETIVO ORIGINAL:
{current_objective}
FALHA ENCONTRADA: {reason}
DETALHES DO ERRO/CONTEXTO:
{context}
PATCHES ORIGINAIS PROPOSTOS PELO ARQUITETO:
{json.dumps(original_patches, indent=2)}
Sua nova missão é analisar o erro e os patches originais, e então gerar um NOVO conjunto de patches para corrigir o problema e alcançar o objetivo original.
Se a falha foi na aplicação de um patch ou validação de sintaxe, revise a operação do patch, o conteúdo ou os seletores/linhas.
Se a falha foi numa validação funcional (ex: Pytest), os novos patches devem visar corrigir o código que causou a falha.
"""
                self.objective_stack.append(correction_obj_text)
                self.logger.info(f"Gerado novo objetivo de correção e adicionado à pilha.")

            elif not success:
                self.logger.error(f"\nFALHA NÃO RECUPERÁVEL OU DESCONHECIDA. Razão: {reason}. Contexto: {context}. Encerrando.")
                break

            self.logger.info(f"{'='*20} FIM DO CICLO {'='*20}")
            time.sleep(self.config.get("cycle_delay_seconds", 1)) # Reduzido para testes mais rápidos


if __name__ == "__main__":
    # Configuração do logging
    log_formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

    # Handler para o console
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(log_formatter)
    console_handler.setLevel(logging.INFO)

    # Handler para o arquivo
    file_handler = logging.FileHandler("hephaestus.log", mode='w') # mode='w' para sobrescrever a cada execução
    file_handler.setFormatter(log_formatter)
    file_handler.setLevel(logging.DEBUG)

    # Configurar o logger raiz ou o logger específico
    # logging.basicConfig(level=logging.DEBUG, handlers=[console_handler, file_handler])
    # Ou configurar o logger que estamos usando no HephaestusAgent
    root_logger = logging.getLogger() # Pega o logger raiz
    root_logger.setLevel(logging.DEBUG) # Define o nível mais baixo no logger raiz
    root_logger.addHandler(console_handler)
    root_logger.addHandler(file_handler)

    # Obter uma instância do logger configurado para passar para o agente
    agent_logger = logging.getLogger("HephaestusAgent") # Pode ser o mesmo que __name__ em main.py, mas mais explícito

    load_dotenv() # Carrega variáveis de ambiente do .env
    agent = HephaestusAgent(logger_instance=agent_logger) # Passa a instância do logger
    agent.run()
