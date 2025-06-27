import json
import os
import shutil
import tempfile
import time
import logging # ADICIONADO
import argparse # ADICIONADO PARA ARGUMENTOS DE LINHA DE COMANDO
import csv # ADICIONADO PARA LOG DE EVOLUÇÃO
from datetime import datetime # ADICIONADO PARA LOG DE EVOLUÇÃO
from pathlib import Path
from dotenv import load_dotenv
from typing import Optional, Dict, Any, List, Tuple # ADICIONADO PARA TYPE HINTS

from agent.project_scanner import update_project_manifest
# Removida a duplicata de import project_scanner
# from agent.patch_applicator import apply_patches # Será substituído por manipulação em memória # REMOVIDO - DUPLICADO E OBSOLETO
from agent.brain import (
    # get_action_plan, # Removido - agora em ArchitectAgent
    # get_maestro_decision, # Removido - agora em MaestroAgent
    generate_next_objective,
    generate_capacitation_objective,
    generate_commit_message # ADICIONADO para auto-versionamento
)
from agent.agents import ArchitectAgent, MaestroAgent # NOVAS CLASSES DE AGENTE
# from agent.patch_applicator import apply_patches # Será substituído por manipulação em memória
# AGORA: from agent.patch_applicator import apply_patches # Será usado com o novo patch_applicator

from agent.tool_executor import run_pytest, check_file_existence, run_git_command # ADICIONADO run_git_command

# Importar o novo patch_applicator

from agent.memory import Memory # ADICIONADO PARA MEMÓRIA PERSISTENTE
from agent.state import AgentState # ADICIONADO PARA ESTADO ESTRUTURADO
from agent.validation_steps import get_validation_step

# Configuração do Logging
logger = logging.getLogger(__name__) # ADICIONADO

class HephaestusAgent:
    """Classe principal que encapsula a lógica do agente autônomo."""

    def __init__(self,
                 logger_instance,
                 continuous_mode: bool = False, # ADICIONADO
                 objective_stack_depth_for_testing: Optional[int] = None): # MODIFICADO
        """
        Inicializa o agente com configuração.

        Args:
            logger_instance: Instância do logger a ser usada.
            continuous_mode: Se True, o agente opera em modo contínuo. # ADICIONADO
            objective_stack_depth_for_testing: Limite opcional para o número de ciclos de execução,
                                                  usado principalmente para testes. Se None, o agente
                                                  executa continuamente (se continuous_mode não estiver ativo e a pilha estiver vazia).
        """
        self.logger = logger_instance # ADICIONADO
        self.config = self.load_config()
        self.continuous_mode = continuous_mode # ADICIONADO
        self.objective_stack_depth_for_testing = objective_stack_depth_for_testing
        self.api_key = os.getenv("OPENROUTER_API_KEY")
        self.model_list = [
            "deepseek/deepseek-chat-v3-0324:free",
            "deepseek/deepseek-r1-0528:free"
        ]
        self.light_model = "deepseek/deepseek-chat-v3-0324:free"
        self.state: AgentState = AgentState() # Modificado para usar a dataclass
        self.objective_stack: List[str] = []  # Pilha de objetivos com tipo
        # Adicionar import List from typing se não estiver lá em cima
        # from typing import List # Já deve estar em Optional, Dict, Any, List, Tuple

        # Inicialização da Memória Persistente
        memory_file_path = self.config.get("memory_file_path", "HEPHAESTUS_MEMORY.json")
        self.memory = Memory(filepath=memory_file_path)
        self.logger.info(f"Carregando memória de {memory_file_path}...")
        self.memory.load()
        self.logger.info(f"Memória carregada. {len(self.memory.completed_objectives)} objetivos concluídos, {len(self.memory.failed_objectives)} falharam.")

        # Inicialização dos Agentes Especializados
        architect_model = self.config.get("models", {}).get("architect_default", self.model_list[0])
        self.architect = ArchitectAgent(
            api_key=self.api_key,
            model=architect_model,
            logger=self.logger.getChild("ArchitectAgent") # Logger específico
        )
        self.logger.info(f"ArchitectAgent inicializado com modelo: {architect_model}")

        maestro_model_list = self.config.get("models", {}).get("maestro_default_list", self.model_list) # Permite lista no config
        self.maestro = MaestroAgent(
            api_key=self.api_key,
            model_list=maestro_model_list,
            config=self.config, # Maestro pode precisar de acesso a outras partes da config
            logger=self.logger.getChild("MaestroAgent") # Logger específico
        )
        self.logger.info(f"MaestroAgent inicializado com modelos: {maestro_model_list}")

        self.evolution_log_file = "evolution_log.csv" # ADICIONADO
        self._initialize_evolution_log() # ADICIONADO

        self._reset_cycle_state() # Inicializa o estado do ciclo

    def _initialize_evolution_log(self): # ADICIONADO
        """Verifica e inicializa o arquivo de log de evolução com cabeçalho, se necessário."""
        log_file_path = Path(self.evolution_log_file)
        if not log_file_path.exists():
            self.logger.info(f"Criando arquivo de log de evolução: {self.evolution_log_file}")
            try:
                with open(log_file_path, 'w', newline='', encoding='utf-8') as f:
                    writer = csv.writer(f)
                    writer.writerow([
                        "ciclo", "objetivo", "status", "tempo_gasto_segundos",
                        "score_qualidade", "estrategia_usada", "timestamp_inicio",
                        "timestamp_fim", "razao_status", "contexto_status"
                    ])
            except IOError as e:
                self.logger.error(f"Não foi possível criar o arquivo de log de evolução {self.evolution_log_file}: {e}")

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
            return False

        # 5. git commit -m "chore: Initial commit"
        commit_message = "chore: Initial commit by Hephaestus Agent"
        commit_success, commit_output = run_git_command(['git', 'commit', '-m', commit_message])
        self.logger.debug(f"Resultado 'git commit': Success={commit_success}, Output:\n{commit_output}")
        if not commit_success:
            if "nothing to commit" in commit_output.lower() or "nada a submeter" in commit_output.lower() or "no changes added to commit" in commit_output.lower():
                self.logger.warning(f"'git commit' informou que não há nada novo para commitar. Output:\n{commit_output}")
                self.logger.info("Considerando a inicialização do Git como bem-sucedida.")
            else:
                self.logger.error(f"FALHA CRÍTICA: 'git commit' inicial falhou. Output:\n{commit_output}")
                return False

        self.logger.info("Commit inicial realizado com sucesso ou já existente.")
        return True

    def _reset_cycle_state(self):
        current_objective = self.state.get("current_objective")
    def _reset_cycle_state(self):
        # current_objective = self.state.get("current_objective") # Antes da dataclass
        current_objective = self.state.current_objective # Com dataclass

        # O dicionário self.state foi substituído pela dataclass AgentState.
        # A inicialização dos campos é feita pela dataclass ou pelo método reset_for_new_cycle.
        # A linha self.state = { ... } foi removida na refatoração anterior para usar AgentState.
        # Agora, chamamos o método da instância de AgentState.
        self.state.reset_for_new_cycle(current_objective)

        # A remoção do objetivo atual da pilha é feita para evitar reprocessamento imediato
        # se ele for re-adicionado por alguma lógica de falha/correção durante o ciclo.
        self.objective_stack = [obj for obj in self.objective_stack if obj != current_objective]

    @staticmethod
    def load_config() -> dict:
        with open("hephaestus_config.json", "r", encoding="utf-8") as f:
            return json.load(f)

    def _generate_manifest(self) -> bool:
        self.logger.info("Gerando manifesto do projeto (AGENTS.md)...")
        try:
            target_files = []
            if self.state.current_objective and "project_scanner.py" in self.state.current_objective:
                target_files.append("agent/project_scanner.py")
            update_project_manifest(root_dir=".", target_files=target_files)
            with open("AGENTS.md", "r", encoding="utf-8") as f:
                self.state.manifesto_content = f.read()
            self.logger.info(f"--- MANIFESTO GERADO (Tamanho: {len(self.state.manifesto_content)} caracteres) ---")
            return True
        except Exception as e:
            self.logger.error(f"ERRO CRÍTICO ao gerar manifesto: {e}", exc_info=True)
            return False

    # Removido _get_file_content_from_memory_or_disk pois não era utilizado
    # def _get_file_content_from_memory_or_disk(self, file_path: str) -> list[str] | None:
    #     if file_path in self.state["in_memory_files"]:
    #         self.logger.debug(f"Lendo {file_path} da memória.")
    #         return self.state["in_memory_files"][file_path]
    #     try:
    #         self.logger.debug(f"Lendo {file_path} do disco.")
    #         with open(file_path, "r", encoding="utf-8") as f:
    #             return f.read().splitlines()
    #     except FileNotFoundError:
    #         self.logger.warn(f"Arquivo {file_path} não encontrado no disco.")
    #         return None
    #     except Exception as e:
    #         self.logger.error(f"Erro ao ler arquivo {file_path} do disco: {e}", exc_info=True)
    #         return None

    def _run_architect_phase(self) -> bool:
        self.logger.info("\nSolicitando plano de ação do ArchitectAgent...")
        action_plan_data, error_msg = self.architect.plan_action(
            objective=self.state.current_objective,
            manifest=self.state.manifesto_content
        )
        if error_msg:
            self.logger.error(f"--- FALHA: ArchitectAgent não conseguiu gerar um plano de ação. Erro: {error_msg} ---")
            return False
        if not action_plan_data or "patches_to_apply" not in action_plan_data:
            self.logger.error(f"--- FALHA: ArchitectAgent retornou uma resposta inválida ou sem 'patches_to_apply'. Resposta: {action_plan_data} ---")
            return False

        self.state.action_plan_data = action_plan_data
        self.logger.info(f"--- PLANO DE AÇÃO (PATCHES) GERADO PELO ARCHITECTAGENT ({self.architect.model}) ---")
        self.logger.debug(f"Análise do Arquiteto: {self.state.get_architect_analysis()}")
        self.logger.debug(f"Patches: {json.dumps(self.state.get_patches_to_apply(), indent=2)}")
        return True

    def _run_maestro_phase(self) -> bool:
        self.logger.info("\nSolicitando decisão do MaestroAgent...")
        if not self.state.action_plan_data:
            self.logger.error("--- FALHA: Nenhum plano de ação (patches) disponível para o MaestroAgent avaliar. ---")
            return False

        maestro_logs = self.maestro.choose_strategy(
            action_plan_data=self.state.action_plan_data,
            memory_summary=self.memory.get_full_history_for_prompt()
        )

        maestro_attempt = next((log for log in maestro_logs if log.get("success")), None)

        if not maestro_attempt or not maestro_attempt.get("parsed_json"):
            self.logger.error("--- FALHA: MaestroAgent não retornou uma resposta JSON válida. ---")
            raw_resp_list = [log.get('raw_response', 'No raw response') for log in maestro_logs]
            self.logger.debug(f"Respostas brutas do MaestroAgent: {raw_resp_list}")
            return False

        decision = maestro_attempt["parsed_json"]
        strategy_key = (decision.get("strategy_key") or "").strip()

        valid_strategies = list(self.config.get("validation_strategies", {}).keys())
        valid_strategies.append("CAPACITATION_REQUIRED")

        if strategy_key not in valid_strategies:
            self.logger.error(f"--- FALHA: MaestroAgent escolheu uma estratégia inválida ou desconhecida: '{strategy_key}' ---")
            self.logger.debug(f"Estratégias válidas são: {valid_strategies}. Resposta do Maestro: {decision}")
            return False

        self.logger.info(f"Estratégia escolhida pelo MaestroAgent ({maestro_attempt.get('model', 'N/A')}): {strategy_key}")
        self.state.strategy_key = strategy_key
        return True

    def _execute_validation_strategy(self) -> None:
        strategy_key = self.state.strategy_key
        strategy_config = self.config["validation_strategies"].get(strategy_key, {})
        steps = strategy_config.get("steps", [])
        self.logger.info(f"\nExecuting strategy '{strategy_key}' with steps: {steps}")
        self.state.validation_result = (False, "STRATEGY_PENDING", f"Starting strategy {strategy_key}")

        patches_to_apply = self.state.get_patches_to_apply()
        sandbox_dir_obj = None
        try:
            use_sandbox = any(step in ["apply_patches_to_disk", "validate_syntax", "run_pytest_validation"] for step in steps) and patches_to_apply
            current_base_path = "."
            if use_sandbox:
                sandbox_dir_obj = tempfile.TemporaryDirectory(prefix="hephaestus_sandbox_")
                current_base_path = sandbox_dir_obj.name
                self.logger.info(f"Created temporary sandbox at: {current_base_path}")
                self.logger.info(f"Copying project to sandbox: {current_base_path}...")
                shutil.copytree(".", current_base_path, dirs_exist_ok=True)
                self.logger.info("Copy to sandbox complete.")

            for step_name in steps:
                self.logger.info(f"--- Validation/Execution Step: {step_name} ---")
                try:
                    validation_step_class = get_validation_step(step_name)
                    step_instance = validation_step_class(
                        logger=self.logger,
                        base_path=current_base_path,
                        patches_to_apply=patches_to_apply,
                        use_sandbox=use_sandbox,
                    )
                    step_success, reason, details = step_instance.execute()
                    if not step_success:
                        self.state.validation_result = (False, reason, details)
                        self.logger.error(f"Step '{step_name}' failed. Stopping strategy '{strategy_key}'. Details: {details}")
                        break
                except ValueError as e:
                    self.logger.error(f"Unknown validation step: {step_name}. Treating as FAILURE.")
                    self.state.validation_result = (False, "UNKNOWN_VALIDATION_STEP", f"Unknown step: {step_name}")
                    break
                except Exception as e:
                    self.logger.error(f"An unexpected error occurred during step '{step_name}': {e}", exc_info=True)
                    reason_code = f"{step_name.upper()}_UNEXPECTED_ERROR"
                    self.state.validation_result = (False, reason_code, str(e))
                    break

            validation_succeeded, reason, details = self.state.validation_result

            if use_sandbox:
                if not validation_succeeded and "_IN_SANDBOX" in reason:
                    self.logger.warn(f"Validation in sandbox failed ({reason}). Discarding patches. Details: {details}")
                elif validation_succeeded:
                    self.logger.info("Validations in sandbox passed. Promoting changes to the real project.")
                    try:
                        copied_files_count = 0
                        files_mentioned_in_patches = {instr.get("file_path") for instr in patches_to_apply if instr.get("file_path")}
                        for file_path_relative_str in files_mentioned_in_patches:
                            sandbox_file = Path(current_base_path) / file_path_relative_str
                            real_project_file = Path(".") / file_path_relative_str
                            if sandbox_file.exists():
                                real_project_file.parent.mkdir(parents=True, exist_ok=True)
                                shutil.copy2(sandbox_file, real_project_file)
                                copied_files_count += 1
                            elif real_project_file.exists():
                                real_project_file.unlink(missing_ok=True)
                                self.logger.info(f"File {real_project_file} removed from real project as it no longer exists in the sandbox.")
                                copied_files_count += 1
                        self.logger.info(f"{copied_files_count} files/directories synchronized from sandbox to real project.")
                        self.state.validation_result = (True, "APPLIED_AND_VALIDATED", f"Strategy '{strategy_key}' completed, patches applied and validated via sandbox.")
                    except Exception as e:
                        self.logger.error(f"CRITICAL ERROR promoting changes from sandbox to real project: {e}", exc_info=True)
                        self.state.validation_result = (False, "PROMOTION_FAILED", str(e))

            if strategy_key == "DISCARD":
                self.state.validation_result = (True, "DISCARDED", "Discard strategy executed.")
            elif validation_succeeded and self.state.validation_result[1] == "STRATEGY_PENDING":
                self.state.validation_result = (True, "NO_ACTION_SUCCESS", f"Strategy '{strategy_key}' completed without modification actions or explicit failure, all steps OK.")
        finally:
            if sandbox_dir_obj:
                self.logger.info(f"Cleaning up temporary sandbox: {sandbox_dir_obj.name}")
                sandbox_dir_obj.cleanup()
                self.logger.info("Sandbox cleaned.")
        return

    def _execute_validation_strategy(self) -> None:
        strategy_key = self.state.strategy_key # Acesso direto
        strategy_config = self.config["validation_strategies"].get(strategy_key, {}) # strategy_key não será None aqui
        steps = strategy_config.get("steps", [])
        self.logger.info(f"\nExecutando estratégia '{strategy_key}' com os passos: {steps}")
        self.state.validation_result = (False, "STRATEGY_PENDING", f"Iniciando estratégia {strategy_key}") # Acesso direto

        patches_to_apply = self.state.get_patches_to_apply() # Usar helper
        sandbox_dir_obj = None
        try:
            use_sandbox = any(step in ["apply_patches_to_disk", "validate_syntax", "run_pytest_validation"] for step in steps) and patches_to_apply
            current_base_path = "."
            if use_sandbox:
                sandbox_dir_obj = tempfile.TemporaryDirectory(prefix="hephaestus_sandbox_")
                current_base_path = sandbox_dir_obj.name
                self.logger.info(f"Criado sandbox temporário em: {current_base_path}")
                self.logger.info(f"Copiando projeto para o sandbox: {current_base_path}...")
                shutil.copytree(".", current_base_path, dirs_exist_ok=True)
                self.logger.info("Cópia para o sandbox concluída.")

            for step_name in steps:
                self.logger.info(f"--- Passo de Validação/Execução: {step_name} ---")
                step_success = False
                if step_name == "apply_patches_to_disk":
                    step_success = self._execute_step_apply_patches(patches_to_apply, current_base_path, use_sandbox)
                elif step_name == "validate_syntax":
                    step_success = self._execute_step_validate_syntax(patches_to_apply, current_base_path, use_sandbox)
                elif step_name == "validate_json_syntax":
                    step_success = self._execute_step_validate_json_syntax(patches_to_apply, current_base_path, use_sandbox)
                elif step_name == "run_pytest_validation":
                    step_success = self._execute_step_run_pytest(current_base_path, use_sandbox)
                elif step_name == "run_benchmark_validation":
                    step_success = self._execute_step_run_benchmark(current_base_path, use_sandbox)
                elif step_name == "check_file_existence":
                    # Este passo normalmente seria usado para verificar se arquivos esperados existem
                    # após uma operação, como a criação de documentação ou arquivos de configuração.
                    # Como é um passo de verificação, ele não falha a menos que a verificação em si falhe.
                    # A lógica de `check_file_existence` em `tool_executor.py` já retorna True/False.
                    # Aqui, vamos assumir que os arquivos a serem verificados são os que foram aplicados.
                    files_to_check = [patch.get("file_path") for patch in patches_to_apply if patch.get("file_path")]
                    if files_to_check:
                        step_success, details = check_file_existence(files_to_check, base_path=current_base_path)
                        if not step_success:
                            self.logger.warn(f"Falha no passo 'check_file_existence': {details}")
                            # A falha aqui é uma falha de validação, então atualizamos o validation_result
                            reason_code = "FILE_EXISTENCE_CHECK_FAILED_IN_SANDBOX" if use_sandbox else "FILE_EXISTENCE_CHECK_FAILED"
                            self.state.validation_result = (False, reason_code, details)
                        else:
                            self.logger.info(f"Passo 'check_file_existence' concluído com sucesso em '{current_base_path}'.")
                    else:
                        self.logger.info("Nenhum arquivo para verificar em 'check_file_existence'. Passo considerado bem-sucedido.")
                        step_success = True
                else:
                    self.logger.error(f"Passo de validação desconhecido: {step_name}. Tratando como FALHA.")
                    self.state.validation_result = (False, "UNKNOWN_VALIDATION_STEP", f"Passo desconhecido: {step_name}")
                    step_success = False

                if not step_success:
                    # Se o validation_result já foi definido por uma falha interna no passo (ex: check_file_existence),
                    # não sobrescreva com uma mensagem genérica.
                    if self.state.validation_result[0] is not False or self.state.validation_result[1] == "STRATEGY_PENDING":
                         reason_code = f"{step_name.upper()}_FAILED_IN_SANDBOX" if use_sandbox else f"{step_name.upper()}_FAILED"
                         self.state.validation_result = (False, reason_code, f"Falha no passo '{step_name}' durante a execução da estratégia '{strategy_key}'.")
                    self.logger.error(f"Falha no passo '{step_name}'. Interrompendo estratégia '{strategy_key}'. Detalhes: {self.state.validation_result[2]}")
                    break # Sai do loop de passos

            # A lógica de promoção do sandbox e finalização da estratégia permanece aqui,
            # mas agora depende do self.state.validation_result que foi atualizado pelos métodos _execute_step_*
            # ou pela lógica de tratamento de passo desconhecido.
            validation_succeeded, reason, details = self.state.validation_result

            # Se nenhum passo falhou e o resultado ainda é "STRATEGY_PENDING", significa que todos os passos
            # foram bem-sucedidos (ou não houve passos que pudessem falhar ativamente o validation_result).
            if validation_succeeded is False and reason == "STRATEGY_PENDING": # Caso onde nenhum passo falhou explicitamente
                self.logger.info(f"Todos os passos da estratégia '{strategy_key}' completados, mas o resultado final da validação ainda está pendente. Verificando...")
                # Isso pode acontecer se a estratégia não tiver passos que modifiquem o validation_result para True.
                # Se chegamos aqui sem um 'break' no loop de passos, consideramos sucesso se não houve falha.
                # No entanto, o estado `validation_result` já deve ter sido definido para (False, "UNKNOWN_VALIDATION_STEP", ...)
                # ou similar se um passo desconhecido foi encontrado e `step_success` tornou-se `False`.
                # A lógica abaixo garante que o estado final seja consistente.

            if use_sandbox: # Esta lógica de promoção/descarte do sandbox permanece centralizada
                if not validation_succeeded and "_IN_SANDBOX" in reason: # Se um passo no sandbox falhou
                    self.logger.warn(f"Validação no sandbox falhou ({reason}). Descartando patches. Detalhes: {details}")
                    # O validation_result já deve estar definido para a falha específica. Apenas logamos.
                elif validation_succeeded and "apply_patches_to_disk" in steps and patches_to_apply:
                    self.logger.info("Validações no sandbox aprovadas. Promovendo mudanças para o projeto real.")
                    
                # Lógica final para definir estado de sucesso quando nenhum erro ocorreu
                if validation_succeeded is False and reason == "STRATEGY_PENDING":
                    if strategy_key == "DISCARD":
                        self.state.validation_result = (True, "DISCARDED", "Estratégia de descarte executada.")
                    elif "apply_patches_to_disk" in steps:
                        self.state.validation_result = (True, "APPLIED_AND_VALIDATED", "Estratégia concluída e patches aplicados.")
                    else:
                        self.state.validation_result = (True, "VALIDATED_ONLY", "Estratégia de validação concluída sem aplicação.")
                    try:
                        copied_files_count = 0
                        files_mentioned_in_patches = {instr.get("file_path") for instr in patches_to_apply if instr.get("file_path")}
                        for file_path_relative_str in files_mentioned_in_patches:
                            sandbox_file = Path(current_base_path) / file_path_relative_str
                            real_project_file = Path(".") / file_path_relative_str
                            if sandbox_file.exists():
                                real_project_file.parent.mkdir(parents=True, exist_ok=True)
                                shutil.copy2(sandbox_file, real_project_file)
                                copied_files_count += 1
                            elif real_project_file.exists(): # Se o arquivo não existe mais no sandbox (foi removido por um patch)
                                real_project_file.unlink(missing_ok=True) # Garante que ele seja removido do projeto real também
                                self.logger.info(f"Arquivo {real_project_file} removido do projeto real pois não existe mais no sandbox.")
                                copied_files_count +=1 # Considera uma "sincronização"
                        self.logger.info(f"{copied_files_count} arquivos/diretórios sincronizados do sandbox para o projeto real.")
                        self.state.validation_result = (True, "APPLIED_AND_VALIDATED", f"Estratégia '{strategy_key}' concluída, patches aplicados e validados via sandbox.")
                    except Exception as e:
                        self.logger.error(f"ERRO CRÍTICO ao promover mudanças do sandbox para o projeto real: {e}", exc_info=True)
                        self.state.validation_result = (False, "PROMOTION_FAILED", str(e))
                elif validation_succeeded and (not patches_to_apply and strategy_key != "DISCARD"): # Sucesso, mas sem patches para aplicar (ex: estratégia só de validação)
                     self.logger.info("Nenhum patch foi fornecido ou aplicado, mas a estratégia (possivelmente de validação) foi bem-sucedida no sandbox.")
                     # Se a estratégia era só de validação (sem apply_patches_to_disk) e passou, é um sucesso.
                     if reason == "STRATEGY_PENDING": # Se nenhum passo modificou o resultado, mas todos passaram
                        self.state.validation_result = (True, "VALIDATED_IN_SANDBOX", f"Estratégia '{strategy_key}' concluída com sucesso no sandbox (sem patches para aplicar).")


            # Lógica para quando não se usa sandbox ou após promoção bem-sucedida
            if not use_sandbox or (use_sandbox and validation_succeeded and reason == "APPLIED_AND_VALIDATED"):
                if validation_succeeded and "apply_patches_to_disk" in steps and patches_to_apply:
                    # Se usou sandbox, já foi definido como APPLIED_AND_VALIDATED. Se não usou, define agora.
                    if reason != "APPLIED_AND_VALIDATED": # Evita sobrescrever se já veio do sandbox
                         self.state.validation_result = (True, "APPLIED_AND_VALIDATED", f"Estratégia '{strategy_key}' concluída, patches aplicados e validados (sem sandbox ou após promoção).")
                elif validation_succeeded and (not patches_to_apply or "apply_patches_to_disk" not in steps) and strategy_key != "DISCARD":
                    if reason == "STRATEGY_PENDING": # Se nenhum passo modificou o resultado, mas todos passaram
                        self.state.validation_result = (True, "VALIDATED_ONLY", f"Estratégia '{strategy_key}' de validação concluída (sem aplicação de patches no disco).")
                    # Se já era VALIDATED_IN_SANDBOX, mantém.

            if strategy_key == "DISCARD":
                self.state.validation_result = (True, "DISCARDED", "Estratégia de descarte executada.")
            elif validation_succeeded and self.state.validation_result[1] == "STRATEGY_PENDING": # Se ainda está pendente e não falhou
                self.state.validation_result = (True, "NO_ACTION_SUCCESS", f"Estratégia '{strategy_key}' concluída sem ações de modificação ou falha explícita, todos os passos OK.")
        finally:
            if sandbox_dir_obj:
                self.logger.info(f"Limpando sandbox temporário: {sandbox_dir_obj.name}")
                sandbox_dir_obj.cleanup()
                self.logger.info("Sandbox limpo.")
        return

    def run(self) -> None:
        if not self.api_key:
            self.logger.error("Erro: OPENROUTER_API_KEY não encontrada. Encerrando.")
            return
        if not self._initialize_git_repository():
            self.logger.error("Falha ao inicializar o repositório Git. O agente não pode continuar sem versionamento.")
            return
        if not self.objective_stack:
            self.logger.info("Gerando objetivo inicial...")
            initial_objective_model = self.config.get("models", {}).get("objective_generator", self.light_model)
            # Passar resumo da memória para o primeiro objetivo também
            initial_objective = generate_next_objective(
                api_key=self.api_key,
                model=initial_objective_model,
                current_manifest="", # Manifesto vazio para o primeiro objetivo
                logger=self.logger,
                project_root_dir=".", # Adicionado project_root_dir
                memory_summary=self.memory.get_full_history_for_prompt()
            )
            self.objective_stack.append(initial_objective)
            self.logger.info(f"Objetivo inicial: {initial_objective}")

        cycle_count = 0 # Contador de ciclos
        # Nota: Em ambiente de teste, self.objective_stack_depth_for_testing pode ser usado
        # para limitar o número de ciclos e evitar loops infinitos.
        # Em produção, deixe como None para execução contínua.

        self.logger.info(f"Iniciando HephaestusAgent. Modo Contínuo: {'ATIVADO' if self.continuous_mode else 'DESATIVADO'}.")
        if self.objective_stack_depth_for_testing is not None:
            self.logger.info(f"Limite máximo de ciclos de execução definido para: {self.objective_stack_depth_for_testing}.") # Ponto final adicionado


        # Loop principal de execução
        while True: # Modificado para suportar modo contínuo
            timestamp_inicio_ciclo = datetime.now() # ADICIONADO PARA LOG DE EVOLUÇÃO
            ciclo_status_final = "falha" # Default para o caso de exceções antes da definição de `success`
            razao_final = "ciclo_interrompido_prematuramente"
            contexto_final = "N/A"
            estrategia_final = ""
            objetivo_do_ciclo = ""

            if not self.objective_stack:
                if self.continuous_mode:
                    self.logger.info(f"\n{'='*20} MODO CONTÍNUO {'='*20}\nPilha de objetivos vazia. Gerando novo objetivo...")
                    continuous_objective_model = self.config.get("models", {}).get("objective_generator", self.light_model)
                    new_objective = generate_next_objective(
                        api_key=self.api_key,
                        model=continuous_objective_model,
                        current_manifest=self.state.manifesto_content if hasattr(self.state, 'manifesto_content') else "", # Usar manifesto mais recente se disponível
                        logger=self.logger,
                        project_root_dir=".", # Adicionado project_root_dir
                        memory_summary=self.memory.get_full_history_for_prompt()
                    )
                    self.objective_stack.append(new_objective)
                    self.logger.info(f"Novo objetivo gerado para modo contínuo: {new_objective}")

                    continuous_delay = self.config.get("continuous_mode_delay_seconds", 5)
                    self.logger.info(f"Aguardando {continuous_delay} segundos antes do próximo ciclo contínuo...")
                    time.sleep(continuous_delay)
                else:
                    self.logger.info("Pilha de objetivos vazia e modo contínuo desativado. Encerrando agente.")
                    break # Sai do loop principal se não houver objetivos e o modo contínuo estiver desativado

            if self.objective_stack_depth_for_testing is not None and \
               cycle_count >= self.objective_stack_depth_for_testing:
                self.logger.info(
                    f"Limite de ciclos de execução ({self.objective_stack_depth_for_testing}) atingido. Encerrando."
                )
                break # Sai do loop principal se o limite de ciclos for atingido

            cycle_count += 1
            current_objective = self.objective_stack.pop()
            self.logger.info(f"\n\n{'='*20} INÍCIO DO CICLO DE EVOLUÇÃO (Ciclo #{cycle_count}) {'='*20}")
            self.logger.info(f"OBJETIVO ATUAL: {current_objective}\n")

            # Verificar loop degenerativo
            failure_count = 0
            for log_entry in reversed(self.memory.recent_objectives_log):
                if log_entry["objective"] == current_objective and log_entry["status"] == "failure":
                    failure_count += 1
                # Parar de contar se encontrarmos um sucesso para este objetivo ou se já contamos o suficiente
                elif log_entry["objective"] == current_objective and log_entry["status"] == "success":
                    break
                if failure_count >= 3:
                    break

            if failure_count >= 3:
                self.logger.error(f"Loop degenerativo detectado para o objetivo: \"{current_objective}\". Ocorreram {failure_count} falhas consecutivas.")
                self.memory.add_failed_objective(
                    objective=current_objective,
                    reason="DEGENERATIVE_LOOP_DETECTED",
                    details=f"O objetivo falhou {failure_count} vezes consecutivas. Pausando processamento deste objetivo."
                )
                # Em vez de desativar o continuous_mode, vamos apenas pular este objetivo e continuar
                # para o próximo, se houver. Se a pilha estiver vazia, o comportamento normal do loop (gerar novo ou parar) ocorrerá.
                self.logger.warn(f"O objetivo \"{current_objective}\" será descartado devido a loop degenerativo.")
                # Não adicionamos de volta à pilha, efetivamente o descartando.
                # Se o modo contínuo estiver ativo e a pilha ficar vazia, um novo objetivo será gerado.
                # Se não, e a pilha estiver vazia, o agente encerrará.
                continue # Pula para a próxima iteração do while True, pegando o próximo objetivo ou encerrando.


            try:
                self._reset_cycle_state() # Usa self.state.current_objective internamente
                self.state.current_objective = current_objective # Define o objetivo para o novo ciclo

                if not self._generate_manifest(): # Usa self.state.current_objective, self.state.manifesto_content
                    self.logger.error("Falha crítica ao gerar manifesto. Encerrando ciclo.")
                    break
                if not self._run_architect_phase(): # Usa self.state.current_objective, self.state.manifesto_content; define self.state.action_plan_data
                    self.logger.warn("Falha na fase do Arquiteto. Pulando para o próximo objetivo se houver.")
                    if not self.objective_stack: break
                    continue
                if not self._run_maestro_phase(): # Usa self.state.action_plan_data; define self.state.strategy_key
                    self.logger.warning("Falha na fase do Maestro. Pulando para o próximo objetivo se houver.")
                    if not self.objective_stack: break
                    continue

                if self.state.strategy_key == "CAPACITATION_REQUIRED": # Acesso direto
                    self.logger.info("Maestro identificou a necessidade de uma nova capacidade.")
                    self.objective_stack.append(current_objective)
                    architect_analysis = self.state.get_architect_analysis() # Usar helper
                    capacitation_objective_model = self.config.get("models", {}).get("capacitation_generator", self.light_model)
                    capacitation_objective = generate_capacitation_objective(
                        api_key=self.api_key,
                        model=capacitation_objective_model,
                        engineer_analysis=architect_analysis,
                        logger=self.logger,
                        memory_summary=self.memory.get_full_history_for_prompt()
                    )
                    self.logger.info(f"Gerado novo objetivo de capacitação: {capacitation_objective}")
                    self.objective_stack.append(capacitation_objective)
                    continue

                self._execute_validation_strategy() # Usa self.state.strategy_key, self.state.action_plan_data; define self.state.validation_result, self.state.applied_files_report
                success, reason, context = self.state.validation_result # Acesso direto

                if success:
                    self.logger.info(f"\nSUCESSO NA VALIDAÇÃO/APLICAÇÃO! Razão: {reason}")
                    if reason == "APPLIED_AND_VALIDATED":
                        self.logger.info("--- INICIANDO VERIFICAÇÃO DE SANIDADE PÓS-APLICAÇÃO ---")
                        current_strategy_key = self.state.strategy_key # Acesso direto
                        strategy_config_sanity = self.config["validation_strategies"].get(current_strategy_key, {})
                        sanity_check_tool_name = strategy_config_sanity.get("sanity_check_step", "run_pytest")
                        sanity_check_success = True
                        sanity_check_details = "Nenhuma verificação de sanidade executada."

                        if sanity_check_tool_name == "run_pytest":
                            self.logger.info(f"Executando sanidade ({sanity_check_tool_name}) no projeto real.")
                            sanity_check_success, sanity_check_details = run_pytest(test_dir='tests/', cwd=".")
                        elif sanity_check_tool_name == "check_file_existence":
                            self.logger.info(f"Executando sanidade ({sanity_check_tool_name}) no projeto real.")
                            files_to_check = list(self.state.applied_files_report.keys()) # Acesso direto
                            if files_to_check:
                                sanity_check_success, sanity_check_details = check_file_existence(files_to_check)
                            else:
                                sanity_check_success = True; sanity_check_details = "Nenhum arquivo aplicado para verificar."
                        elif sanity_check_tool_name == "skip_sanity_check":
                            sanity_check_success = True; sanity_check_details = "Verificação de sanidade pulada."
                        else:
                            sanity_check_success = False; sanity_check_details = f"Ferramenta de sanidade desconhecida: {sanity_check_tool_name}"

                        if not sanity_check_success:
                            self.logger.error(f"FALHA NA SANIDADE PÓS-APLICAÇÃO ({sanity_check_tool_name})! Detalhes: {sanity_check_details}")
                            self.logger.info("Tentando reverter o último commit devido à falha na sanidade...")
                            rollback_success, rollback_output = run_git_command(['git', 'reset', '--hard', 'HEAD~1'])
                            if rollback_success:
                                self.logger.info(f"Rollback para HEAD~1 bem-sucedido. Output: {rollback_output}")
                            else:
                                self.logger.error(f"FALHA AO TENTAR REVERTER O COMMIT! Output: {rollback_output}")
                                # Considerar o que fazer neste caso. Por enquanto, apenas logar.

                            reason = f"REGRESSION_DETECTED_BY_{sanity_check_tool_name.upper()}_AND_ROLLED_BACK"
                            context = f"Sanity check failed: {sanity_check_details}. Rollback to HEAD~1 attempted (Success: {rollback_success})."
                            success = False
                        else:
                            self.logger.info(f"SANIDADE PÓS-APLICAÇÃO ({sanity_check_tool_name}): SUCESSO!")
                            if sanity_check_tool_name != "skip_sanity_check":
                                self.logger.info("Ressincronizando manifesto e iniciando auto-commit...")
                                update_project_manifest(root_dir=".", target_files=[])
                                # Atualizar manifesto no estado
                                with open("AGENTS.md", "r", encoding="utf-8") as f: self.state.manifesto_content = f.read()
                                analysis_summary = self.state.get_architect_analysis() # Usar helper
                                commit_model = self.config.get("models", {}).get("commit_message_generator", self.light_model)
                                commit_message = generate_commit_message(self.api_key, commit_model, analysis_summary, self.state.current_objective, self.logger) # Acesso direto
                                run_git_command(['git', 'add', '.'])
                                commit_success_git, commit_output_git = run_git_command(['git', 'commit', '-m', commit_message])
                                if not commit_success_git:
                                    self.logger.error(f"FALHA CRÍTICA no git commit: {commit_output_git}. Alterações podem não ter sido salvas.")
                                else:
                                    self.logger.info("--- AUTO-COMMIT REALIZADO COM SUCESSO ---")

                            self.logger.info("Gerando próximo objetivo evolutivo...")
                            obj_model = self.config.get("models", {}).get("objective_generator", self.light_model)
                            next_obj = generate_next_objective(
                                api_key=self.api_key,
                                model=obj_model,
                                current_manifest=self.state.manifesto_content,
                                logger=self.logger,
                                project_root_dir=".", # Adicionado project_root_dir
                                memory_summary=self.memory.get_full_history_for_prompt()
                            ) # Acesso direto
                            self.objective_stack.append(next_obj)
                            self.logger.info(f"Próximo objetivo: {next_obj}")

                        if success:
                             self.memory.add_completed_objective(
                                objective=self.state.current_objective, # Acesso direto
                                strategy=self.state.strategy_key,        # Acesso direto
                                details=f"Applied. Sanity ({sanity_check_tool_name}): OK. Details: {sanity_check_details}"
                            )
                             if self.state.current_objective.startswith("[TAREFA DE CAPACITAÇÃO]"): # Acesso direto
                                self.memory.add_capability(
                                    capability_description=f"Capacitation task completed and validated: {self.state.current_objective}", # Acesso direto
                                    related_objective=self.state.current_objective # Acesso direto
                                )

                    elif reason in ["DISCARDED", "VALIDATED_ONLY", "NO_PATCHES_APPLIED", "NO_ACTION_TAKEN"]:
                        self.logger.info(f"Ciclo concluído com status: {reason}. Gerando próximo objetivo evolutivo...")
                        if reason == "VALIDATED_ONLY":
                             self.memory.add_completed_objective(
                                objective=self.state.current_objective, # Acesso direto
                                strategy=self.state.strategy_key,        # Acesso direto
                                details=f"Validation successful as per strategy '{self.state.strategy_key}'." # Acesso direto
                            )
                        obj_model = self.config.get("models", {}).get("objective_generator", self.light_model)
                        next_obj = generate_next_objective(
                            api_key=self.api_key,
                            model=obj_model,
                            current_manifest=self.state.manifesto_content,
                            logger=self.logger,
                            project_root_dir=".", # Adicionado project_root_dir
                            memory_summary=self.memory.get_full_history_for_prompt()
                        ) # Acesso direto
                        self.objective_stack.append(next_obj)
                        self.logger.info(f"Próximo objetivo: {next_obj}")

                if not success:
                    self.logger.warn(f"\nFALHA NO CICLO! Razão Final: {reason}\nContexto Final: {context}")
                    self.memory.add_failed_objective(objective=self.state.current_objective, reason=reason, details=context) # Acesso direto

                    correctable_failure_reasons = {
                        "PATCH_APPLICATION_FAILED_IN_SANDBOX", "SYNTAX_VALIDATION_FAILED_IN_SANDBOX",
                        "JSON_SYNTAX_VALIDATION_FAILED_IN_SANDBOX", "PYTEST_FAILURE_IN_SANDBOX",
                        "PROMOTION_FAILED", "PATCH_DISCARDED"
                    }
                    if 'sanity_check_tool_name' in locals() and sanity_check_tool_name != "skip_sanity_check" and reason.startswith("REGRESSION_DETECTED_BY_"):
                        correctable_failure_reasons.add(reason)

                    if reason in correctable_failure_reasons:
                        self.logger.warn(f"Falha corrigível ({reason}). Gerando objetivo de correção.")
                        self.objective_stack.append(current_objective)
                        original_patches_str = json.dumps(self.state.get_patches_to_apply(), indent=2) # Usar helper
                        correction_details_str = f"FALHA ENCONTRADA: {reason}\nDETALHES DA FALHA: {context}"

                        # Verificar se é uma falha de teste pytest
                        is_test_failure = "PYTEST_FAILURE" in reason or "REGRESSION_DETECTED_BY_RUN_PYTEST" in reason
                        
                        correction_obj_text = f"""[TAREFA DE CORREÇÃO AUTOMÁTICA]
OBJETIVO ORIGINAL QUE FALHOU: {current_objective}
{correction_details_str}
PATCHES ORIGINAIS ENVOLVIDOS: {original_patches_str}
Sua missão é analisar a falha e gerar NOVOS patches para CORRIGIR o problema e alcançar o OBJETIVO ORIGINAL.
Se o problema foi nos patches, corrija-os. Se foi na validação ou sanidade, ajuste os patches para passar.
"""
                        if is_test_failure:
                            # Adicionar flag especial para correção de testes
                            correction_obj_text += "\n[CONTEXT_FLAG] TEST_FIX_IN_PROGRESS"
                        
                        self.objective_stack.append(correction_obj_text)
                        self.logger.info(f"Gerado novo objetivo de correção e adicionado à pilha. {'(TEST_FIX_IN_PROGRESS)' if is_test_failure else ''}")
                    else:
                        self.logger.error(f"Falha não listada como corrigível ou desconhecida ({reason}). Encerrando processamento de objetivos.")
                        break

            finally:
                # Salvar memória ao final de cada ciclo, independentemente do resultado do ciclo.
                self.memory.save()
                self.logger.info(f"Memória salva em {self.memory.filepath} ({len(self.memory.completed_objectives)} completed, {len(self.memory.failed_objectives)} failed)")

                # Coletar dados para o log de evolução
                timestamp_fim_ciclo = datetime.now()
                tempo_gasto_segundos = (timestamp_fim_ciclo - timestamp_inicio_ciclo).total_seconds()

                # `success` é definida dentro do try, mas pode não ser se uma exceção ocorrer antes.
                # Usamos ciclo_status_final, que tem um default.
                if 'success' in locals() and success is not None: # Verifica se success foi definida
                    ciclo_status_final = "sucesso" if success else "falha"

                # `reason` e `context` vêm de self.state.validation_result
                # Se self.state.validation_result não foi definido (ciclo quebrou antes), usamos os defaults.
                if hasattr(self.state, 'validation_result') and self.state.validation_result:
                    _, razao_final, contexto_final = self.state.validation_result

                if hasattr(self.state, 'strategy_key') and self.state.strategy_key:
                    estrategia_final = self.state.strategy_key

                if hasattr(self.state, 'current_objective') and self.state.current_objective:
                    objetivo_do_ciclo = self.state.current_objective
                elif 'current_objective' in locals() and current_objective: # Se self.state.current_objective não foi setado
                    objetivo_do_ciclo = current_objective


                log_entry_evolution = [
                    cycle_count,
                    objetivo_do_ciclo,
                    ciclo_status_final,
                    round(tempo_gasto_segundos, 2),
                    "", # score_qualidade (vazio por enquanto)
                    estrategia_final,
                    timestamp_inicio_ciclo.isoformat(),
                    timestamp_fim_ciclo.isoformat(),
                    razao_final,
                    contexto_final
                ]
                try:
                    with open(self.evolution_log_file, 'a', newline='', encoding='utf-8') as f:
                        writer = csv.writer(f)
                        writer.writerow(log_entry_evolution)
                except IOError as e:
                    self.logger.error(f"Não foi possível escrever no arquivo de log de evolução {self.evolution_log_file}: {e}")
                except Exception as e: # Captura outras exceções potenciais ao tentar logar
                    self.logger.error(f"Erro inesperado ao tentar escrever no log de evolução: {e}", exc_info=True)


                self.logger.info(f"{'='*20} FIM DO CICLO DE EVOLUÇÃO {'='*20}")
                time.sleep(self.config.get("cycle_delay_seconds", 1))

if __name__ == "__main__":
    log_formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(log_formatter)
    console_handler.setLevel(logging.INFO)
    file_handler = logging.FileHandler("hephaestus.log", mode='w')
    file_handler.setFormatter(log_formatter)
    file_handler.setLevel(logging.DEBUG)
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.DEBUG)
    root_logger.addHandler(console_handler)
    root_logger.addHandler(file_handler)
    agent_logger = logging.getLogger("HephaestusAgent")
    load_dotenv()
    # Exemplo de como definir o limite de ciclos ao instanciar, se necessário:
    # agent = HephaestusAgent(logger_instance=agent_logger, objective_stack_depth_for_testing=3)

    parser = argparse.ArgumentParser(description="Hephaestus Agent: Autonomous AI for code evolution.")
    parser.add_argument(
        "-c", "--continuous-mode",
        action="store_true",
        help="Enable continuous mode, where the agent generates new objectives indefinitely."
    )
    parser.add_argument(
        "--max-cycles",
        type=int,
        default=None,
        help="Maximum number of evolution cycles to run (for testing or controlled runs)."
    )
    args = parser.parse_args()

    agent = HephaestusAgent(
        logger_instance=agent_logger,
        continuous_mode=args.continuous_mode,
        objective_stack_depth_for_testing=args.max_cycles
    )
    agent.run()
