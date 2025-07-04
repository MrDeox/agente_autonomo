import json
import os
import shutil
import tempfile
import time
import logging
import csv
from datetime import datetime
from pathlib import Path
from typing import Optional, Dict, Any, List, Tuple

from agent.project_scanner import update_project_manifest
from agent.brain import (
    generate_next_objective,
    generate_capacitation_objective,
    generate_commit_message
)
from agent.agents import ArchitectAgent, MaestroAgent
from agent.tool_executor import run_pytest, check_file_existence, run_git_command
from agent.git_utils import initialize_git_repository
from agent.cycle_runner import run_cycles
from agent.memory import Memory
from agent.state import AgentState
from agent.validation_steps import get_validation_step
from agent.queue_manager import QueueManager
from agent.config_loader import load_config # Import the new load_config

# Configuração do Logging
logger = logging.getLogger(__name__)

class HephaestusAgent:
    """Classe principal que encapsula a lógica do agente autônomo."""

    def __init__(self,
                 logger_instance,
                 config: dict, # Now receives config as a parameter
                 continuous_mode: bool = False,
                 objective_stack_depth_for_testing: Optional[int] = None):
        """
        Inicializa o agente com configuração.

        Args:
            logger_instance: Instância do logger a ser usada.
            config: Dicionário de configuração para o agente.
            continuous_mode: Se True, o agente opera em modo contínuo.
            objective_stack_depth_for_testing: Limite opcional para o número de ciclos de execução.
        """
        self.logger = logger_instance
        self.config = config # Use the passed config
        self.continuous_mode = continuous_mode
        self.objective_stack_depth_for_testing = objective_stack_depth_for_testing
        self.state: AgentState = AgentState()
        self.queue_manager = QueueManager()
        self.objective_stack: list = []

        # Inicialização da Memória Persistente
        memory_file_path = self.config.get("memory_file_path", "HEPHAESTUS_MEMORY.json")
        self.memory = Memory(filepath=memory_file_path)
        self.logger.info(f"Carregando memória de {memory_file_path}...")
        self.memory.load()
        self.logger.info(f"Memória carregada. {len(self.memory.completed_objectives)} objetivos concluídos, {len(self.memory.failed_objectives)} falharam.")

        # Inicialização dos Agentes Especializados
        architect_model_config = self.config.get("models", {}).get("architect_default")
        self.architect = ArchitectAgent(
            model_config=architect_model_config,
            logger=self.logger.getChild("ArchitectAgent")
        )
        self.logger.info(f"ArchitectAgent inicializado com a configuração: {architect_model_config}")

        maestro_model_config = self.config.get("models", {}).get("maestro_default")
        self.maestro = MaestroAgent(
            model_config=maestro_model_config,
            config=self.config,
            logger=self.logger.getChild("MaestroAgent")
        )
        self.logger.info(f"MaestroAgent inicializado com a configuração: {maestro_model_config}")

        self.evolution_log_file = "evolution_log.csv"
        self._initialize_evolution_log()

        self._reset_cycle_state()

    def _initialize_evolution_log(self):
        """Verifica e inicializa o arquivo de log de evolução com cabeçalho, se necessário."""
        log_file_path = Path(self.evolution_log_file)
        if not log_file_path.exists():
            self.logger.info(f"Criando arquivo de log de evolução: {self.evolution_log_file}")
            try:
                with open(log_file_path, 'w', newline='', encoding="utf-8") as f:
                    writer = csv.writer(f)
                    writer.writerow([
                        "ciclo", "objetivo", "status", "tempo_gasto_segundos",
                        "score_qualidade", "estrategia_usada", "timestamp_inicio",
                        "timestamp_fim", "razao_status", "contexto_status"
                    ])
            except IOError as e:
                self.logger.error(f"Não foi possível criar o arquivo de log de evolução {self.evolution_log_file}: {e}")

    def _reset_cycle_state(self):
        current_objective = self.state.current_objective
        self.state.reset_for_new_cycle(current_objective)

    def _generate_manifest(self) -> bool:
        self.logger.info("Gerando manifesto do projeto (AGENTS.md)...")
        try:
            target_files_for_manifest: List[str] = []
            if self.state.current_objective:
                potential_file_target = self.state.current_objective.split(" ")[-1]
                if Path(potential_file_target).is_file():
                    target_files_for_manifest.append(potential_file_target)
                elif "project_scanner.py" in self.state.current_objective:
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
            manifest=self.state.manifesto_content
        )
        if error_msg or not action_plan_data or "patches_to_apply" not in action_plan_data:
            self.logger.error(
                f"--- FALHA: ArchitectAgent não conseguiu gerar um plano de ação válido. Erro: {error_msg} ---"
            )
            action_plan_data = {"analysis": "", "patches_to_apply": []}

        self.state.action_plan_data = action_plan_data
        self.logger.info(f"--- PLANO DE AÇÃO (PATCHES) GERADO PELO ARCHITECTAGENT ({self.architect.model_config}) ---")
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

        maestro_attempt = next((log for log in maestro_logs if log.get("success") and log.get("parsed_json")), None)

        if not maestro_attempt:
            self.logger.error("--- FALHA: MaestroAgent não retornou uma resposta JSON válida e bem-sucedida após todas as tentativas. ---")
            raw_resp_list = [log.get('raw_response', 'No raw response') for log in maestro_logs]
            self.logger.debug(f"Respostas brutas do MaestroAgent: {raw_resp_list}")
            fallback_strategy = self.config.get("validation_strategies", {}).get("NO_OP_STRATEGY")
            if fallback_strategy is None:
                return False
            self.logger.info("Usando estratégia padrão NO_OP_STRATEGY por falta de decisão válida do MaestroAgent.")
            self.state.strategy_key = "NO_OP_STRATEGY"
            return True

        decision = maestro_attempt["parsed_json"]
        strategy_key = (decision.get("strategy_key") or "").strip()

        valid_strategies = list(self.config.get("validation_strategies", {}).keys())
        valid_strategies.append("CAPACITATION_REQUIRED")

        if strategy_key not in valid_strategies:
            self.logger.error(f"--- FALHA: MaestroAgent escolheu uma estratégia inválida ou desconhecida: '{strategy_key}' ---")
            self.logger.debug(f"Estratégias válidas são: {valid_strategies}. Decisão do Maestro: {decision}")
            return False

        self.logger.info(f"Estratégia escolhida pelo MaestroAgent ({maestro_attempt.get('model', 'N/A')}): {strategy_key}")
        self.state.strategy_key = strategy_key
        return True

    def _execute_validation_strategy(self) -> None:
        strategy_key = self.state.strategy_key
        if not strategy_key:
            self.logger.error("CRITICAL: _execute_validation_strategy called with no strategy_key set.")
            self.state.validation_result = (False, "NO_STRATEGY_KEY", "Strategy key was not set before execution.")
            return

        strategy_config = self.config.get("validation_strategies", {}).get(strategy_key, {})
        steps = strategy_config.get("steps", [])
        self.logger.info(f"\nExecuting strategy '{strategy_key}' with steps: {steps}")
        self.state.validation_result = (False, "STRATEGY_PENDING", f"Starting strategy {strategy_key}")

        patches_to_apply = self.state.get_patches_to_apply()
        sandbox_dir_obj = None
        current_base_path_str = "."

        try:
            needs_disk_modification = "apply_patches_to_disk" in steps or "PatchApplicatorStep" in steps
            has_validation_steps_on_files = any(s in ["validate_syntax", "validate_json_syntax", "run_pytest_validation"] for s in steps)

            use_sandbox = (needs_disk_modification or has_validation_steps_on_files) and bool(patches_to_apply) and strategy_key != "DISCARD"


            if use_sandbox:
                sandbox_dir_obj = tempfile.TemporaryDirectory(prefix="hephaestus_sandbox_")
                current_base_path_str = sandbox_dir_obj.name
                self.logger.info(f"Created temporary sandbox at: {current_base_path_str}")
                self.logger.info(f"Copying project to sandbox: {current_base_path_str}...")
                shutil.copytree(".", current_base_path_str, dirs_exist_ok=True, ignore=shutil.ignore_patterns('.git'))
                self.logger.info("Copy to sandbox complete.")

            all_steps_succeeded = True
            for step_name in steps:
                self.logger.info(f"--- Validation/Execution Step: {step_name} ---")
                try:
                    validation_step_class = get_validation_step(step_name)
                    step_instance = validation_step_class(
                        logger=self.logger,
                        base_path=Path(current_base_path_str),
                        patches_to_apply=patches_to_apply,
                        use_sandbox=use_sandbox,
                    )
                    step_success, reason, details = step_instance.execute()

                    if not step_success:
                        self.state.validation_result = (False, reason, details)
                        self.logger.error(f"Step '{step_name}' failed. Stopping strategy '{strategy_key}'. Details: {details}")
                        all_steps_succeeded = False
                        break
                except ValueError as e:
                    self.logger.error(f"Unknown validation step: {step_name}. Error: {e}. Treating as FAILURE.")
                    self.state.validation_result = (False, "UNKNOWN_VALIDATION_STEP", f"Unknown step: {step_name}")
                    all_steps_succeeded = False
                    break
                except Exception as e:
                    self.logger.error(f"An unexpected error occurred during step '{step_name}': {e}", exc_info=True)
                    reason_code = f"{step_name.upper()}_UNEXPECTED_ERROR"
                    self.state.validation_result = (False, reason_code, str(e))
                    all_steps_succeeded = False
                    break

            if all_steps_succeeded:
                if self.state.validation_result[1] == "STRATEGY_PENDING":
                    if strategy_key == "DISCARD":
                         self.state.validation_result = (True, "DISCARDED", "Patches discarded as per strategy.")
                    elif needs_disk_modification and patches_to_apply:
                        # Marcar como sucesso para qualquer modificação de disco (resolve o problema de STRATEGY_PENDING)
                        self.state.validation_result = (True, "STRATEGY_SUCCEEDED", f"Strategy '{strategy_key}' completed successfully.")
                    else:
                        self.state.validation_result = (True, "VALIDATION_SUCCESS_NO_CHANGES", f"Strategy '{strategy_key}' completed successfully without disk changes or no patches to apply.")


            current_validation_succeeded, current_reason, current_details = self.state.validation_result

            if use_sandbox:
                if current_validation_succeeded and needs_disk_modification and patches_to_apply:
                    self.logger.info("Validations in sandbox passed. Promoting changes to the real project.")
                    try:
                        copied_files_count = 0
                        affected_files_relative = {instr.get("file_path") for instr in patches_to_apply if instr.get("file_path")}

                        for rel_path_str in affected_files_relative:
                            if not rel_path_str: continue

                            sandbox_file = Path(current_base_path_str) / rel_path_str
                            real_project_file = Path(".") / rel_path_str

                            real_project_file.parent.mkdir(parents=True, exist_ok=True)

                            if sandbox_file.exists():
                                shutil.copy2(sandbox_file, real_project_file)
                                copied_files_count += 1
                                self.logger.debug(f"Copied from sandbox: {sandbox_file} to {real_project_file}")
                            elif real_project_file.exists():
                                real_project_file.unlink()
                                copied_files_count += 1
                                self.logger.info(f"Deleted from real project (as deleted in sandbox): {real_project_file}")

                        self.logger.info(f"{copied_files_count} files/directories synchronized from sandbox to real project.")
                        self.state.validation_result = (True, "APPLIED_AND_VALIDATED_SANDBOX", f"Strategy '{strategy_key}' completed, patches applied and validated via sandbox.")
                    except Exception as e:
                        self.logger.error(f"CRITICAL ERROR promoting changes from sandbox to real project: {e}", exc_info=True)
                        self.state.validation_result = (False, "PROMOTION_FAILED", str(e))
                elif not current_validation_succeeded:
                    self.logger.warning(
                        f"Validation in sandbox failed (Reason: {current_reason}). Patches will not be promoted. Details: {current_details}"
                    )

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
        if not initialize_git_repository(self.logger):
            self.logger.error("Falha ao inicializar o repositório Git. O agente não pode continuar sem versionamento.")
            return

        self.logger.info("Gerando objetivo inicial...")
        model_config = self.config.get("models", {}).get("objective_generator")
        initial_objective = generate_next_objective(
            model_config=model_config,
            current_manifest="",
            logger=self.logger,
            project_root_dir=".",
            config=self.config,
            memory_summary=self.memory.get_full_history_for_prompt(),
        )
        self.queue_manager.put_objective(initial_objective)
        self.logger.info(f"Objetivo inicial adicionado à fila: {initial_objective}")

        run_cycles(self, self.queue_manager)


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
        help="Maximum number of evolution cycles to run (for testing or controlled runs). Default: None (runs indefinitely or until stack empty if not continuous)."
    )
    args = parser.parse_args()

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
    )
    agent.run()
