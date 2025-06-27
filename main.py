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
            # Determine target files for manifest generation based on objective
            # This logic can be expanded or made more sophisticated
            target_files_for_manifest: List[str] = []
            if self.state.current_objective:
                # Example: if objective mentions a specific file, target it.
                # This is a placeholder for more advanced logic.
                potential_file_target = self.state.current_objective.split(" ")[-1] # very naive
                if Path(potential_file_target).is_file():
                    target_files_for_manifest.append(potential_file_target)
                elif "project_scanner.py" in self.state.current_objective: # existing logic
                     target_files_for_manifest.append("agent/project_scanner.py")

            update_project_manifest(root_dir=".", target_files=target_files_for_manifest)
            with open("AGENTS.md", "r", encoding="utf-8") as f:
                self.state.manifesto_content = f.read()
            self.logger.info(f"--- MANIFESTO GERADO (Tamanho: {len(self.state.manifesto_content)} caracteres) ---")
            return True
        except Exception as e:
            self.logger.error(f"ERRO CRÍTICO ao gerar manifesto: {e}", exc_info=True)
            return False

    def _run_architect_phase(self) -> bool:
        self.logger.info("\nSolicitando plano de ação do ArchitectAgent...")
        action_plan_data, error_msg = self.architect.plan_action(
            objective=self.state.current_objective,
            manifest=self.state.manifesto_content # manifesto_content is already a string
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

        # Find the first successful attempt from Maestro
        maestro_attempt = next((log for log in maestro_logs if log.get("success") and log.get("parsed_json")), None)

        if not maestro_attempt: # Covers no success or no parsed_json in successful attempts
            self.logger.error("--- FALHA: MaestroAgent não retornou uma resposta JSON válida e bem-sucedida após todas as tentativas. ---")
            raw_resp_list = [log.get('raw_response', 'No raw response') for log in maestro_logs]
            self.logger.debug(f"Respostas brutas do MaestroAgent: {raw_resp_list}")
            # Log specific errors from attempts if available
            for i, log_attempt in enumerate(maestro_logs):
                self.logger.debug(f"Maestro Tentativa {i+1} (Modelo: {log_attempt.get('model', 'N/A')}): Sucesso={log_attempt.get('success')}, Resposta/Erro='{log_attempt.get('raw_response', '')}'")
            return False

        decision = maestro_attempt["parsed_json"] # Known to exist due to next() condition
        strategy_key = (decision.get("strategy_key") or "").strip()

        # Validate strategy_key (already done inside MaestroAgent.choose_strategy, but can be double-checked)
        valid_strategies = list(self.config.get("validation_strategies", {}).keys())
        valid_strategies.append("CAPACITATION_REQUIRED") # Also a valid choice

        if strategy_key not in valid_strategies:
            self.logger.error(f"--- FALHA: MaestroAgent escolheu uma estratégia inválida ou desconhecida: '{strategy_key}' ---")
            self.logger.debug(f"Estratégias válidas são: {valid_strategies}. Decisão do Maestro: {decision}")
            return False

        self.logger.info(f"Estratégia escolhida pelo MaestroAgent ({maestro_attempt.get('model', 'N/A')}): {strategy_key}")
        self.state.strategy_key = strategy_key
        return True

    def _execute_validation_strategy(self) -> None:
        strategy_key = self.state.strategy_key
        if not strategy_key: # Should not happen if _run_maestro_phase succeeded
            self.logger.error("CRITICAL: _execute_validation_strategy called with no strategy_key set.")
            self.state.validation_result = (False, "NO_STRATEGY_KEY", "Strategy key was not set before execution.")
            return

        strategy_config = self.config.get("validation_strategies", {}).get(strategy_key, {})
        steps = strategy_config.get("steps", [])
        self.logger.info(f"\nExecuting strategy '{strategy_key}' with steps: {steps}")
        self.state.validation_result = (False, "STRATEGY_PENDING", f"Starting strategy {strategy_key}")

        patches_to_apply = self.state.get_patches_to_apply()
        sandbox_dir_obj = None # type: Optional[tempfile.TemporaryDirectory]
        current_base_path_str = "." # Default to current directory

        try:
            # Determine if sandbox is needed (any step that modifies disk and there are patches)
            # "discard" step does not use sandbox.
            # "run_pytest_validation" alone (without apply_patches_to_disk) might run on current code or sandbox if other steps need it.
            # For simplicity, if "apply_patches_to_disk" is present with patches, use sandbox.
            # Or if steps like "validate_syntax" or "run_pytest_validation" are present with patches, they imply sandbox usage for safety.
            needs_disk_modification = "apply_patches_to_disk" in steps
            has_validation_steps_on_files = any(s in ["validate_syntax", "validate_json_syntax", "run_pytest_validation"] for s in steps)

            use_sandbox = (needs_disk_modification or has_validation_steps_on_files) and bool(patches_to_apply) and strategy_key != "DISCARD"


            if use_sandbox:
                sandbox_dir_obj = tempfile.TemporaryDirectory(prefix="hephaestus_sandbox_")
                current_base_path_str = sandbox_dir_obj.name
                self.logger.info(f"Created temporary sandbox at: {current_base_path_str}")
                self.logger.info(f"Copying project to sandbox: {current_base_path_str}...")
                # Ensure .git is not copied, or handle .git operations carefully if needed in sandbox
                shutil.copytree(".", current_base_path_str, dirs_exist_ok=True, ignore=shutil.ignore_patterns('.git'))
                self.logger.info("Copy to sandbox complete.")

            # Execute each step in the strategy
            all_steps_succeeded = True
            for step_name in steps:
                self.logger.info(f"--- Validation/Execution Step: {step_name} ---")
                try:
                    validation_step_class = get_validation_step(step_name) # Factory function
                    step_instance = validation_step_class(
                        logger=self.logger,
                        base_path=Path(current_base_path_str), # Pass as Path object
                        patches_to_apply=patches_to_apply, # type: ignore
                        # use_sandbox=use_sandbox, # This info is implicit in base_path
                        # config=self.config # Pass full config if steps need it
                    )
                    step_success, reason, details = step_instance.execute()

                    if not step_success:
                        self.state.validation_result = (False, reason, details)
                        self.logger.error(f"Step '{step_name}' failed. Stopping strategy '{strategy_key}'. Details: {details}")
                        all_steps_succeeded = False
                        break # Stop executing further steps in this strategy
                except ValueError as e: # Raised by get_validation_step for unknown step
                    self.logger.error(f"Unknown validation step: {step_name}. Error: {e}. Treating as FAILURE.")
                    self.state.validation_result = (False, "UNKNOWN_VALIDATION_STEP", f"Unknown step: {step_name}")
                    all_steps_succeeded = False
                    break
                except Exception as e: # Catch unexpected errors during step execution
                    self.logger.error(f"An unexpected error occurred during step '{step_name}': {e}", exc_info=True)
                    reason_code = f"{step_name.upper()}_UNEXPECTED_ERROR"
                    self.state.validation_result = (False, reason_code, str(e))
                    all_steps_succeeded = False
                    break

            # After all steps (or early exit due to failure)
            if all_steps_succeeded:
                # If all steps ran and none explicitly set validation_result to False,
                # it means the strategy's sequence of operations was successful.
                # The final status of validation_result might still be "STRATEGY_PENDING"
                # if no step explicitly set it to (True, ...).
                # We need to determine the final outcome.
                if self.state.validation_result[1] == "STRATEGY_PENDING":
                    if strategy_key == "DISCARD": # discard is a success type
                         self.state.validation_result = (True, "DISCARDED", "Patches discarded as per strategy.")
                    elif needs_disk_modification and patches_to_apply : # If patches were meant to be applied
                        # This implies apply_patches_to_disk was successful.
                        # If sandbox was used, promotion is next. If not, it's already applied.
                        if not use_sandbox:
                             self.state.validation_result = (True, "APPLIED_AND_VALIDATED_NO_SANDBOX", f"Strategy '{strategy_key}' completed, patches applied directly.")
                        # else: Sandbox promotion logic will set the final state
                    else: # Strategy involved no disk modification or no patches
                        self.state.validation_result = (True, "VALIDATION_SUCCESS_NO_CHANGES", f"Strategy '{strategy_key}' completed successfully without disk changes or no patches to apply.")


            # Sandbox promotion or cleanup
            current_validation_succeeded, current_reason, current_details = self.state.validation_result

            if use_sandbox:
                if current_validation_succeeded and needs_disk_modification and patches_to_apply:
                    self.logger.info("Validations in sandbox passed. Promoting changes to the real project.")
                    try:
                        copied_files_count = 0
                        # Determine which files were actually changed/created by patches
                        # This could be more precise if apply_patches_to_disk step returned a list of affected files.
                        # For now, assume all files mentioned in patches *could* have been affected.
                        affected_files_relative = {instr.get("file_path") for instr in patches_to_apply if instr.get("file_path")}

                        for rel_path_str in affected_files_relative:
                            if not rel_path_str: continue # Should not happen with valid patches

                            sandbox_file = Path(current_base_path_str) / rel_path_str
                            real_project_file = Path(".") / rel_path_str

                            real_project_file.parent.mkdir(parents=True, exist_ok=True)

                            if sandbox_file.exists():
                                shutil.copy2(sandbox_file, real_project_file)
                                copied_files_count += 1
                                self.logger.debug(f"Copied from sandbox: {sandbox_file} to {real_project_file}")
                            elif real_project_file.exists():
                                # File was deleted by a patch in sandbox, so delete from real project
                                real_project_file.unlink()
                                copied_files_count += 1 # Count as a change
                                self.logger.info(f"Deleted from real project (as deleted in sandbox): {real_project_file}")

                        self.logger.info(f"{copied_files_count} files/directories synchronized from sandbox to real project.")
                        self.state.validation_result = (True, "APPLIED_AND_VALIDATED_SANDBOX", f"Strategy '{strategy_key}' completed, patches applied and validated via sandbox.")
                    except Exception as e:
                        self.logger.error(f"CRITICAL ERROR promoting changes from sandbox to real project: {e}", exc_info=True)
                        self.state.validation_result = (False, "PROMOTION_FAILED", str(e))
                elif not current_validation_succeeded:
                    self.logger.warn(f"Validation in sandbox failed (Reason: {current_reason}). Patches will not be promoted. Details: {current_details}")
                    # The validation_result is already set to the failure.

            # Final check if state is still pending (should be resolved by now)
            if self.state.validation_result[1] == "STRATEGY_PENDING":
                 self.logger.warning(f"Strategy '{strategy_key}' ended with a PENDING state. This should be resolved. Defaulting to success if no explicit failure.")
                 self.state.validation_result = (True, "STRATEGY_COMPLETED_NO_EXPLICIT_FAILURE", f"Strategy '{strategy_key}' completed its steps without explicit failure.")

        finally:
            if sandbox_dir_obj:
                self.logger.info(f"Cleaning up temporary sandbox: {sandbox_dir_obj.name}")
                sandbox_dir_obj.cleanup()
                self.logger.info("Sandbox cleaned.")
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
            initial_objective = generate_next_objective(
                api_key=self.api_key,
                model=initial_objective_model,
                current_manifest="", # Manifesto vazio para o primeiro objetivo
                logger=self.logger,
                project_root_dir=".",
                config=self.config, # Pass config for thresholds
                memory_summary=self.memory.get_full_history_for_prompt()
            )
            self.objective_stack.append(initial_objective)
            self.logger.info(f"Objetivo inicial: {initial_objective}")

        cycle_count = 0
        self.logger.info(f"Iniciando HephaestusAgent. Modo Contínuo: {'ATIVADO' if self.continuous_mode else 'DESATIVADO'}.")
        if self.objective_stack_depth_for_testing is not None:
            self.logger.info(f"Limite máximo de ciclos de execução definido para: {self.objective_stack_depth_for_testing}.")


        while True:
            timestamp_inicio_ciclo = datetime.now()
            ciclo_status_final = "falha"
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
                        current_manifest=self.state.manifesto_content if self.state.manifesto_content else "",
                        logger=self.logger,
                        project_root_dir=".",
                        config=self.config, # Pass config
                        memory_summary=self.memory.get_full_history_for_prompt()
                    )
                    self.objective_stack.append(new_objective)
                    self.logger.info(f"Novo objetivo gerado para modo contínuo: {new_objective}")

                    continuous_delay = self.config.get("continuous_mode_delay_seconds", 5)
                    self.logger.info(f"Aguardando {continuous_delay} segundos antes do próximo ciclo contínuo...")
                    time.sleep(continuous_delay)
                else:
                    self.logger.info("Pilha de objetivos vazia e modo contínuo desativado. Encerrando agente.")
                    break

            if self.objective_stack_depth_for_testing is not None and \
               cycle_count >= self.objective_stack_depth_for_testing:
                self.logger.info(
                    f"Limite de ciclos de execução ({self.objective_stack_depth_for_testing}) atingido. Encerrando."
                )
                break

            cycle_count += 1
            current_objective = self.objective_stack.pop()
            self.logger.info(f"\n\n{'='*20} INÍCIO DO CICLO DE EVOLUÇÃO (Ciclo #{cycle_count}) {'='*20}")
            self.logger.info(f"OBJETIVO ATUAL: {current_objective}\n")

            failure_count = 0
            for log_entry in reversed(self.memory.recent_objectives_log):
                if log_entry["objective"] == current_objective and log_entry["status"] == "failure":
                    failure_count += 1
                elif log_entry["objective"] == current_objective and log_entry["status"] == "success":
                    break
                if failure_count >= self.config.get("degenerative_loop_threshold", 3): # Use config
                    break

            if failure_count >= self.config.get("degenerative_loop_threshold", 3):
                self.logger.error(f"Loop degenerativo detectado para o objetivo: \"{current_objective}\". Ocorreram {failure_count} falhas consecutivas.")
                self.memory.add_failed_objective(
                    objective=current_objective,
                    reason="DEGENERATIVE_LOOP_DETECTED",
                    details=f"O objetivo falhou {failure_count} vezes consecutivas. Pausando processamento deste objetivo."
                )
                self.logger.warn(f"O objetivo \"{current_objective}\" será descartado devido a loop degenerativo.")
                continue


            try:
                self._reset_cycle_state()
                self.state.current_objective = current_objective

                if not self._generate_manifest():
                    self.logger.error("Falha crítica ao gerar manifesto. Encerrando ciclo.")
                    # Potentially add failed objective to memory here
                    break
                if not self._run_architect_phase():
                    self.logger.warn("Falha na fase do Arquiteto. Pulando para o próximo objetivo se houver.")
                    # Add failed objective to memory with reason "ARCHITECT_PHASE_FAILED"
                    self.memory.add_failed_objective(current_objective, "ARCHITECT_PHASE_FAILED", "ArchitectAgent could not generate a plan.")
                    if not self.objective_stack and not self.continuous_mode : break
                    continue
                if not self._run_maestro_phase():
                    self.logger.warning("Falha na fase do Maestro. Pulando para o próximo objetivo se houver.")
                    # Add failed objective to memory with reason "MAESTRO_PHASE_FAILED"
                    self.memory.add_failed_objective(current_objective, "MAESTRO_PHASE_FAILED", "MaestroAgent could not decide on a strategy.")
                    if not self.objective_stack and not self.continuous_mode : break
                    continue

                if self.state.strategy_key == "CAPACITATION_REQUIRED":
                    self.logger.info("Maestro identificou a necessidade de uma nova capacidade.")
                    self.objective_stack.append(current_objective) # Re-add current objective to try later
                    architect_analysis = self.state.get_architect_analysis()
                    capacitation_objective_model = self.config.get("models", {}).get("capacitation_generator", self.light_model)
                    capacitation_objective = generate_capacitation_objective(
                        api_key=self.api_key,
                        model=capacitation_objective_model,
                        engineer_analysis=architect_analysis or "Analysis not available",
                        logger=self.logger,
                        memory_summary=self.memory.get_full_history_for_prompt()
                    )
                    self.logger.info(f"Gerado novo objetivo de capacitação: {capacitation_objective}")
                    self.objective_stack.append(capacitation_objective)
                    continue # Proceed to the capacitation objective

                self._execute_validation_strategy()
                success, reason, context = self.state.validation_result

                if success:
                    self.logger.info(f"\nSUCESSO NA VALIDAÇÃO/APLICAÇÃO! Razão: {reason}")
                    # APPLIED_AND_VALIDATED_SANDBOX or APPLIED_AND_VALIDATED_NO_SANDBOX
                    if reason.startswith("APPLIED_AND_VALIDATED"):
                        self.logger.info("--- INICIANDO VERIFICAÇÃO DE SANIDADE PÓS-APLICAÇÃO ---")
                        current_strategy_key_for_sanity = self.state.strategy_key
                        strategy_config_sanity = self.config.get("validation_strategies",{}).get(current_strategy_key_for_sanity, {})
                        sanity_check_tool_name = strategy_config_sanity.get("sanity_check_step", "run_pytest")

                        sanity_check_success = True
                        sanity_check_details = "Nenhuma verificação de sanidade configurada ou executada."

                        if sanity_check_tool_name == "run_pytest":
                            self.logger.info(f"Executando sanidade ({sanity_check_tool_name}) no projeto real.")
                            sanity_check_success, sanity_check_details = run_pytest(test_dir='tests/', cwd=".")
                        elif sanity_check_tool_name == "check_file_existence":
                            self.logger.info(f"Executando sanidade ({sanity_check_tool_name}) no projeto real.")
                            # We need a list of files that were supposed to be affected by patches.
                            # This could come from action_plan_data or be inferred.
                            # For now, using a placeholder or assuming it's handled by the step.
                            # A better approach: applied_files_report from the validation step.
                            files_to_check = list(self.state.applied_files_report.keys()) if self.state.applied_files_report else []
                            if files_to_check:
                                sanity_check_success, sanity_check_details = check_file_existence(files_to_check)
                            else:
                                sanity_check_success = True; sanity_check_details = "Nenhum arquivo aplicado para verificar na sanidade."
                        elif sanity_check_tool_name == "skip_sanity_check":
                            sanity_check_success = True; sanity_check_details = "Verificação de sanidade pulada conforme configuração."
                        else:
                            sanity_check_success = False; sanity_check_details = f"Ferramenta de sanidade desconhecida: {sanity_check_tool_name}"

                        if not sanity_check_success:
                            self.logger.error(f"FALHA NA SANIDADE PÓS-APLICAÇÃO ({sanity_check_tool_name})! Detalhes: {sanity_check_details}")
                            self.logger.info("Tentando reverter o último commit devido à falha na sanidade...")
                            # This assumes changes were committed before sanity check, which might not be the case.
                            # If not committed, `git reset --hard` might be more appropriate if uncommitted changes exist.
                            # For now, let's assume a commit was made *before* this specific sanity check.
                            # A better flow: apply -> sanity check -> commit.
                            # Current flow seems to be: apply (sandbox) -> promote -> (implicit commit by user?) -> then this.
                            # Let's adjust: only commit if sanity passes.
                            # So, if sanity fails, we need to revert the *applied patches* not a commit.
                            # This implies `git reset --hard` to discard working directory changes from patch application.

                            # If patches were applied directly (no sandbox), this is riskier.
                            # If sandbox was used and changes promoted, then `git reset --hard` on main repo is okay.
                            self.logger.info("Revertendo alterações aplicadas no diretório de trabalho...")
                            revert_cmd = ['git', 'reset', '--hard']
                            # If a specific commit was made just before sanity, one could do HEAD~1.
                            # But if changes are just in working dir, `git reset --hard` is fine.
                            # For safety, let's ensure all files are reset:
                            run_git_command(['git', 'checkout', '--', '.']) # Discard all changes in tracked files
                            # For untracked files created by patches:
                            # `git clean -fdx` is too aggressive. We need to know which files were created.
                            # This part needs more robust handling of reverting applied patches.
                            # For now, a simple reset.
                            rollback_success, rollback_output = run_git_command(revert_cmd)

                            if rollback_success:
                                self.logger.info(f"Rollback das alterações no diretório de trabalho bem-sucedido. Output: {rollback_output}")
                            else:
                                self.logger.error(f"FALHA AO TENTAR REVERTER ALTERAÇÕES NO DIRETÓRIO DE TRABALHO! Output: {rollback_output}")

                            reason = f"REGRESSION_DETECTED_BY_{sanity_check_tool_name.upper()}_AND_ROLLED_BACK"
                            context = f"Sanity check failed: {sanity_check_details}. Rollback of working directory changes attempted (Success: {rollback_success})."
                            success = False # Mark the overall cycle as failed due to sanity failure
                        else: # Sanity check passed
                            self.logger.info(f"SANIDADE PÓS-APLICAÇÃO ({sanity_check_tool_name}): SUCESSO!")
                            if sanity_check_tool_name != "skip_sanity_check": # Only commit if sanity was run and passed
                                self.logger.info("Ressincronizando manifesto e iniciando auto-commit...")
                                update_project_manifest(root_dir=".", target_files=[]) # Update manifest with new state
                                with open("AGENTS.md", "r", encoding="utf-8") as f: self.state.manifesto_content = f.read()

                                analysis_summary_for_commit = self.state.get_architect_analysis() or "N/A"
                                commit_model_for_msg = self.config.get("models", {}).get("commit_message_generator", self.light_model)
                                commit_message = generate_commit_message(self.api_key, commit_model_for_msg, analysis_summary_for_commit, self.state.current_objective or "N/A", self.logger)

                                run_git_command(['git', 'add', '.']) # Stage all changes
                                commit_success_git, commit_output_git = run_git_command(['git', 'commit', '-m', commit_message])
                                if not commit_success_git:
                                    self.logger.error(f"FALHA CRÍTICA no git commit: {commit_output_git}. Alterações podem não ter sido salvas permanentemente.")
                                    # This is a critical failure. The cycle technically succeeded in applying patches and passing sanity,
                                    # but the state couldn't be saved.
                                    reason = "COMMIT_FAILED_POST_SANITY"
                                    context = f"Commit failed: {commit_output_git}"
                                    success = False # Override success to False due to commit failure
                                else:
                                    self.logger.info("--- AUTO-COMMIT REALIZADO COM SUCESSO ---")
                            # Whether committed or not (due to skip_sanity_check), if we reached here and success is true, proceed to next objective.
                            if success: # Check if commit failure overrode success
                                self.logger.info("Gerando próximo objetivo evolutivo...")
                                obj_gen_model = self.config.get("models", {}).get("objective_generator", self.light_model)
                                next_obj = generate_next_objective(
                                    api_key=self.api_key, model=obj_gen_model,
                                    current_manifest=self.state.manifesto_content or "",
                                    logger=self.logger, project_root_dir=".",
                                    config=self.config, # Pass config
                                    memory_summary=self.memory.get_full_history_for_prompt()
                                )
                                self.objective_stack.append(next_obj)
                                self.logger.info(f"Próximo objetivo: {next_obj}")

                        # Add to memory after sanity check and potential commit
                        if success: # Check again as commit failure might have changed it
                             self.memory.add_completed_objective(
                                objective=self.state.current_objective or "N/A",
                                strategy=self.state.strategy_key or "N/A",
                                details=f"Applied. Sanity ({sanity_check_tool_name}): OK. Details: {sanity_check_details}"
                            )
                             if self.state.current_objective and self.state.current_objective.startswith("[TAREFA DE CAPACITAÇÃO]"):
                                self.memory.add_capability(
                                    capability_description=f"Capacitation task completed and validated: {self.state.current_objective}",
                                    related_objective=self.state.current_objective
                                )
                        # If success is False here (due to sanity fail or commit fail), it will be handled by the `if not success:` block later

                    elif reason in ["DISCARDED", "VALIDATION_SUCCESS_NO_CHANGES", "STRATEGY_COMPLETED_NO_EXPLICIT_FAILURE"]: # No changes applied or patches discarded
                        self.logger.info(f"Ciclo concluído com status: {reason}. Nenhuma alteração no código foi promovida. Gerando próximo objetivo evolutivo...")
                        if reason != "DISCARDED": # DISCARDED is a form of completion, but not a "successful application"
                             self.memory.add_completed_objective(
                                objective=self.state.current_objective or "N/A",
                                strategy=self.state.strategy_key or "N/A",
                                details=f"Strategy '{self.state.strategy_key}' completed. Status: {reason}."
                            )
                        # else for DISCARDED, it's a neutral outcome, not a failure, but not a direct success for the objective itself.
                        # Memory for DISCARDED could be handled differently if needed. For now, it's not added as "completed".

                        obj_gen_model = self.config.get("models", {}).get("objective_generator", self.light_model)
                        next_obj = generate_next_objective(
                            api_key=self.api_key, model=obj_gen_model,
                            current_manifest=self.state.manifesto_content or "",
                            logger=self.logger, project_root_dir=".",
                            config=self.config, # Pass config
                            memory_summary=self.memory.get_full_history_for_prompt()
                        )
                        self.objective_stack.append(next_obj)
                        self.logger.info(f"Próximo objetivo: {next_obj}")

                # This block handles all failures from validation, sanity, or commit.
                if not success:
                    self.logger.warn(f"\nFALHA NO CICLO! Razão Final: {reason}\nContexto Final: {context}")
                    self.memory.add_failed_objective(objective=self.state.current_objective or "N/A", reason=reason, details=context)

                    # Check if failure is correctable
                    correctable_failure_reasons = {
                        "PATCH_APPLICATION_FAILED", # Generic patch failure
                        "SYNTAX_VALIDATION_FAILED", "JSON_SYNTAX_VALIDATION_FAILED",
                        "PYTEST_VALIDATION_FAILED", "BENCHMARK_VALIDATION_FAILED",
                        "PROMOTION_FAILED", # From sandbox
                        # Failures from sandbox steps (more specific)
                        "APPLY_PATCHES_TO_DISK_FAILED_IN_SANDBOX",
                        "VALIDATE_SYNTAX_FAILED_IN_SANDBOX",
                        "VALIDATE_JSON_SYNTAX_FAILED_IN_SANDBOX",
                        "RUN_PYTEST_VALIDATION_FAILED_IN_SANDBOX",
                        "RUN_BENCHMARK_VALIDATION_FAILED_IN_SANDBOX",
                        "COMMIT_FAILED_POST_SANITY" # New correctable failure
                    }
                    # Add sanity check failures if they are correctable by new patches
                    if 'sanity_check_tool_name' in locals() and sanity_check_tool_name != "skip_sanity_check" and reason.startswith("REGRESSION_DETECTED_BY_"):
                        correctable_failure_reasons.add(reason)


                    if reason in correctable_failure_reasons:
                        self.logger.warn(f"Falha corrigível ({reason}). Gerando objetivo de correção.")
                        self.objective_stack.append(current_objective) # Re-add original objective to try again after correction
                        
                        original_patches_json = json.dumps(self.state.get_patches_to_apply(), indent=2) if self.state.action_plan_data else "N/A"
                        correction_details = f"FAILURE REASON: {reason}\nFAILURE DETAILS: {context}"
                        is_test_failure_flag = "PYTEST_FAILURE" in reason.upper() or "REGRESSION_DETECTED_BY_RUN_PYTEST" in reason.upper()

                        correction_prompt = f"""[AUTOMATIC CORRECTION TASK]
ORIGINAL OBJECTIVE THAT FAILED: {current_objective}
{correction_details}
ORIGINAL PATCHES INVOLVED: {original_patches_json}
Your mission is to analyze the failure and generate NEW patches to CORRECT the problem and achieve the ORIGINAL OBJECTIVE.
If the problem was in the patches, correct them. If it was in validation or sanity checks, adjust the patches to pass.
"""
                        if is_test_failure_flag:
                            correction_prompt += "\n[CONTEXT_FLAG] TEST_FIX_IN_PROGRESS"
                        
                        self.objective_stack.append(correction_prompt)
                        self.logger.info(f"Gerado novo objetivo de correção e adicionado à pilha. {'(TEST_FIX_IN_PROGRESS)' if is_test_failure_flag else ''}")
                    else:
                        self.logger.error(f"Falha não listada como corrigível ou desconhecida ({reason}). Não será gerado objetivo de correção automático. Verifique os logs.")
                        # Depending on config, could stop or try to generate a generic next objective.
                        # For now, if not correctable, the loop will pick next from stack or generate new if continuous.
                        # If stack is empty and not continuous, it will end. This seems reasonable.

            finally:
                self.memory.save()
                self.logger.info(f"Memória salva em {self.memory.filepath} ({len(self.memory.completed_objectives)} completed, {len(self.memory.failed_objectives)} failed)")

                timestamp_fim_ciclo = datetime.now()
                tempo_gasto_segundos = (timestamp_fim_ciclo - timestamp_inicio_ciclo).total_seconds()

                # Update final status vars for logging
                # 'success' is defined in the try block. If an exception occurs before, it won't be.
                # Default 'ciclo_status_final' is 'falha'.
                if 'success' in locals() and isinstance(success, bool):
                    ciclo_status_final = "sucesso" if success else "falha"

                # 'reason' and 'context' from self.state.validation_result
                if self.state.validation_result: # Ensure it's not None
                    _, razao_final_state, contexto_final_state = self.state.validation_result
                    if razao_final_state: razao_final = razao_final_state
                    if contexto_final_state: contexto_final = contexto_final_state

                if self.state.strategy_key: estrategia_final = self.state.strategy_key
                objetivo_do_ciclo = self.state.current_objective or current_objective # current_objective is from stack pop

                log_entry_evolution = [
                    cycle_count, objetivo_do_ciclo, ciclo_status_final,
                    round(tempo_gasto_segundos, 2),
                    "", # score_qualidade (placeholder)
                    estrategia_final, timestamp_inicio_ciclo.isoformat(),
                    timestamp_fim_ciclo.isoformat(), razao_final, contexto_final
                ]
                try:
                    with open(self.evolution_log_file, 'a', newline='', encoding='utf-8') as f:
                        writer = csv.writer(f)
                        writer.writerow(log_entry_evolution)
                except IOError as e:
                    self.logger.error(f"Não foi possível escrever no arquivo de log de evolução {self.evolution_log_file}: {e}")
                except Exception as e:
                    self.logger.error(f"Erro inesperado ao tentar escrever no log de evolução: {e}", exc_info=True)

                self.logger.info(f"{'='*20} FIM DO CICLO DE EVOLUÇÃO {'='*20}")
                time.sleep(self.config.get("cycle_delay_seconds", 1))

if __name__ == "__main__":
    log_formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(log_formatter)
    console_handler.setLevel(logging.INFO) # Console shows INFO and above

    # Ensure log file is created/opened in write mode to overwrite old logs, or append mode 'a' if desired
    file_handler = logging.FileHandler("hephaestus.log", mode='w')
    file_handler.setFormatter(log_formatter)
    file_handler.setLevel(logging.DEBUG) # File logs DEBUG and above

    root_logger = logging.getLogger() # Get the root logger
    root_logger.setLevel(logging.DEBUG) # Set root logger level to DEBUG
    root_logger.addHandler(console_handler)
    root_logger.addHandler(file_handler)

    agent_logger = logging.getLogger("HephaestusAgent") # Get specific logger for the agent
    # agent_logger will inherit level from root_logger unless set otherwise.
    # If you want agent_logger to have a different level than root for its handlers, set it here.
    # e.g., agent_logger.setLevel(logging.INFO) if you want agent's own messages to be at least INFO.
    # But typically, handlers control the final output level.

    load_dotenv()

    parser = argparse.ArgumentParser(description="Hephaestus Agent: Autonomous AI for code evolution.")
    parser.add_argument(
        "-c", "--continuous-mode",
        action="store_true",
        help="Enable continuous mode, where the agent generates new objectives indefinitely."
    )
    parser.add_argument(
        "--max-cycles",
        type=int,
        default=None, # Changed from 0 to None, implies infinite if not set
        help="Maximum number of evolution cycles to run (for testing or controlled runs). Default: None (runs indefinitely or until stack empty if not continuous)."
    )
    args = parser.parse_args()

    # Load main config for the agent
    try:
        with open("hephaestus_config.json", "r", encoding="utf-8") as f:
            main_config = json.load(f)
    except FileNotFoundError:
        agent_logger.error("CRITICAL: hephaestus_config.json not found. Exiting.")
        sys.exit(1)
    except json.JSONDecodeError as e:
        agent_logger.error(f"CRITICAL: Error decoding hephaestus_config.json: {e}. Exiting.")
        sys.exit(1)

    agent = HephaestusAgent(
        logger_instance=agent_logger,
        continuous_mode=args.continuous_mode,
        objective_stack_depth_for_testing=args.max_cycles,
        # config=main_config # Pass the loaded config to HephaestusAgent constructor
    ) # Config is loaded inside __init__ now.
    agent.run()
