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
from agent.git_utils import initialize_git_repository
from agent.cycle_runner import run_cycles

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
        """Load configuration from ``hephaestus_config.json`` with fallbacks.

        Returns an empty dictionary if both the main and fallback configuration
        files are missing or malformed. Errors are logged for visibility.
        """
        config_logger = logging.getLogger(__name__)

        try:
            with open("hephaestus_config.json", "r", encoding="utf-8") as f:
                return json.load(f)
        except FileNotFoundError:
            config_logger.error(
                "Configuration file 'hephaestus_config.json' not found. "
                "Falling back to defaults."
            )
        except json.JSONDecodeError as e:
            config_logger.error(
                f"Error parsing 'hephaestus_config.json': {e}. "
                "Falling back to defaults."
            )

        # Try fallback configuration
        try:
            with open("example_config.json", "r", encoding="utf-8") as f:
                config_logger.info(
                    "Loaded default configuration from 'example_config.json'."
                )
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError) as e:
            config_logger.error(
                "Fallback configuration 'example_config.json' could not be "
                f"loaded: {e}. Using empty defaults."
            )

        return {}

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
        if not initialize_git_repository(self.logger):
            self.logger.error("Falha ao inicializar o repositório Git. O agente não pode continuar sem versionamento.")
            return
        run_cycles(self)


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
