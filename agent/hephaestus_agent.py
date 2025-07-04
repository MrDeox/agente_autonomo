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
from agent.agents import ArchitectAgent, MaestroAgent, CodeReviewAgent
from agent.tool_executor import run_pytest, check_file_existence, run_git_command
from agent.git_utils import initialize_git_repository
from agent.cycle_runner import CycleRunner
from agent.memory import Memory
from agent.state import AgentState
from agent.validation_steps import get_validation_step
from agent.queue_manager import QueueManager
from agent.config_loader import load_config # Import the new load_config
from agent.cognitive_evolution_manager import get_evolution_manager, start_cognitive_evolution

# Configuração do Logging
logger = logging.getLogger(__name__)

class HephaestusAgent:
    """Classe principal que encapsula a lógica do agente autônomo."""

    def __init__(self,
                 logger_instance,
                 config: dict, # Now receives config as a parameter
                 continuous_mode: bool = False,
                 objective_stack_depth_for_testing: Optional[int] = None,
                 queue_manager: Optional[QueueManager] = None):
        """
        Inicializa o agente com configuração.

        Args:
            logger_instance: Instância do logger a ser usada.
            config: Dicionário de configuração para o agente.
            continuous_mode: Se True, o agente opera em modo contínuo.
            objective_stack_depth_for_testing: Limite opcional para o número de ciclos de execução.
            queue_manager: Gerenciador de fila opcional. Se não for fornecido, um novo será criado.
        """
        self.logger = logger_instance
        self.config = config # Use the passed config
        self.continuous_mode = continuous_mode
        self.objective_stack_depth_for_testing = objective_stack_depth_for_testing
        self.state: AgentState = AgentState()
        self.queue_manager = queue_manager or QueueManager()
        self.objective_stack: list = []

        # Inicialização da Memória Persistente
        memory_file_path = self.config.get("memory_file_path", "HEPHAESTUS_MEMORY.json")
        self.memory = Memory(filepath=memory_file_path, logger=self.logger.getChild("Memory"))
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

        code_review_model_config = self.config.get("models", {}).get("code_reviewer", architect_model_config) # Fallback to architect model
        self.code_reviewer = CodeReviewAgent(
            model_config=code_review_model_config,
            logger=self.logger.getChild("CodeReviewAgent")
        )
        self.logger.info(f"CodeReviewAgent inicializado com a configuração: {code_review_model_config}")

        self.evolution_log_file = "logs/evolution_log.csv"
        self._initialize_evolution_log()

        self._reset_cycle_state()

        # Initialize Meta-Intelligence Systems
        self.evolution_manager = get_evolution_manager(self.config.get("models", {}).get("architect_default"), self.logger)
        self.meta_intelligence_active = False
        
        # Initialize Self-Awareness Core
        from agent.self_awareness_core import get_self_awareness_core
        self.self_awareness_core = get_self_awareness_core(self.config.get("models", {}).get("architect_default"), self.logger)
        
        self.logger.info("🧠 Hephaestus initialized with Meta-Intelligence and Self-Awareness capabilities")

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
        self.logger.info("Gerando manifesto do projeto (ARCHITECTURE.md)...")
        try:
            target_files_for_manifest: List[str] = []
            if self.state.current_objective:
                potential_file_target = self.state.current_objective.split(" ")[-1]
                if Path(potential_file_target).is_file():
                    target_files_for_manifest.append(potential_file_target)
                elif "project_scanner.py" in self.state.current_objective:
                     target_files_for_manifest.append("agent/project_scanner.py")

            update_project_manifest(root_dir=".", target_files=target_files_for_manifest, output_path="docs/ARCHITECTURE.md")
            with open("docs/ARCHITECTURE.md", "r", encoding="utf-8") as f:
                self.state.manifesto_content = f.read()
            self.logger.info(f"--- MANIFESTO GERADO (Tamanho: {len(self.state.manifesto_content)} caracteres) ---")
            return True
        except Exception as e:
            self.logger.error(f"ERRO CRÍTICO ao gerar manifesto: {e}", exc_info=True)
            return False

    def _run_architect_phase(self) -> bool:
        self.logger.info("\nSolicitando plano de ação do ArchitectAgent...")
        if not self.state.current_objective:
            self.logger.error("--- FALHA: _run_architect_phase chamado sem um objetivo atual definido no estado. ---")
            return False

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

    def _run_code_review_phase(self) -> bool:
        """Runs the code review agent on the architect's plan."""
        self.logger.info("\nSolicitando revisão do CodeReviewAgent...")
        patches = self.state.get_patches_to_apply()
        if not patches:
            self.logger.info("Nenhum patch para revisar. Pulando fase de revisão.")
            return True

        review_passed, feedback = self.code_reviewer.review_patches(patches)
        
        if review_passed:
            self.logger.info("Revisão de código aprovada.")
            return True
        
        # If review fails, we will try to re-generate the plan
        self.logger.warning(f"Revisão de código falhou. Feedback: {feedback}. Solicitando novo plano ao ArchitectAgent.")
        
        # We need to update the objective to include the feedback for the architect
        original_objective = self.state.current_objective
        self.state.current_objective = f"{original_objective}\n\n[CODE REVIEW FEEDBACK]\nPlease address the following issues in your new plan:\n{feedback}"
        
        # Re-run architect phase with the feedback
        return self._run_architect_phase()

    def _run_maestro_phase(self, failed_strategy_context: Optional[Dict[str, str]] = None) -> bool:
        self.logger.info("\nSolicitando decisão do MaestroAgent...")
        if not self.state.action_plan_data:
            self.logger.error("--- FALHA: Nenhum plano de ação (patches) disponível para o MaestroAgent avaliar. ---")
            return False

        maestro_logs = self.maestro.choose_strategy(
            action_plan_data=self.state.action_plan_data,
            memory_summary=self.memory.get_full_history_for_prompt(),
            failed_strategy_context=failed_strategy_context
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

    def start_meta_intelligence(self):
        """Activate the meta-intelligence and cognitive evolution systems"""
        if not self.meta_intelligence_active:
            self.logger.info("🚀 ACTIVATING META-INTELLIGENCE - AI will now evolve itself!")
            
            # Start cognitive evolution
            start_cognitive_evolution(self.config.get("models", {}).get("architect_default"), self.logger)
            self.meta_intelligence_active = True
            
            # Start self-awareness monitoring
            self.self_awareness_core.start_continuous_self_monitoring()
            
            self.logger.info("🧬 Meta-Intelligence ACTIVATED - The AI is now self-improving!")
            
            # Log this historic moment
            self.logger.info("=" * 60)
            self.logger.info("🎯 HISTORIC MOMENT: AI ACHIEVES SELF-MODIFICATION CAPABILITY")
            self.logger.info("🔥 The system can now:")
            self.logger.info("   • Evolve its own prompts using genetic algorithms")
            self.logger.info("   • Create new agents when needed")
            self.logger.info("   • Modify its own cognitive architecture")
            self.logger.info("   • Develop meta-cognitive awareness")
            self.logger.info("   • Adapt and improve autonomously")
            self.logger.info("   • Continuously monitor its own consciousness")
            self.logger.info("   • Perform deep introspection and self-reflection")
            self.logger.info("=" * 60)
    
    def get_meta_intelligence_status(self) -> Dict[str, Any]:
        """Get comprehensive status of meta-intelligence systems"""
        if not self.meta_intelligence_active:
            return {"status": "inactive", "message": "Meta-intelligence not activated"}
        
        return self.evolution_manager.get_evolution_report()
    
    def perform_deep_self_reflection(self, focus_area: str = "general") -> Dict[str, Any]:
        """Perform deep self-reflection and introspection"""
        self.logger.info(f"🔍 Performing deep self-reflection - Focus: {focus_area}")
        
        result = self.self_awareness_core.perform_deep_introspection(focus_area)
        
        self.logger.info(f"✅ Deep self-reflection complete")
        self.logger.info(f"   • Generated {len(result.get('new_insights', []))} new insights")
        self.logger.info(f"   • Meta-awareness score: {result.get('meta_awareness', 0):.3f}")
        self.logger.info(f"   • Self-narrative updated")
        
        return result
    
    def get_self_awareness_report(self) -> Dict[str, Any]:
        """Get comprehensive self-awareness report"""
        return self.self_awareness_core.get_self_awareness_report()

    def run(self) -> None:
        if not initialize_git_repository(self.logger):
            self.logger.error("Falha ao inicializar o repositório Git. O agente não pode continuar sem versionamento.")
            return

        cycle_runner = CycleRunner(self, self.queue_manager)
        cycle_runner.run()

    def run_continuous(self):
        """Run the agent in continuous mode with meta-intelligence"""
        self.logger.info("🔄 Starting Hephaestus in continuous mode")
        
        # Activate meta-intelligence
        self.start_meta_intelligence()
        
        try:
            while True:
                # Run normal cycle
                try:
                    self.run()
                    success = True
                except Exception as e:
                    self.logger.error(f"Cycle failed: {e}")
                    success = False
                
                # Check if we need emergency evolution
                if not success:
                    self.logger.warning("Cycle failed - considering emergency evolution")
                    failure_context = f"Cycle failure at {datetime.now().isoformat()}"
                    self.evolution_manager.trigger_emergency_evolution(failure_context)
                
                # Dynamic sleep based on meta-intelligence
                sleep_time = self._calculate_intelligent_sleep()
                self.logger.info(f"💤 Intelligent sleep for {sleep_time:.1f} seconds")
                time.sleep(sleep_time)
                
        except KeyboardInterrupt:
            self.logger.info("🛑 Stopping continuous mode")
            self.evolution_manager.stop_cognitive_evolution()
    
    def _calculate_intelligent_sleep(self) -> float:
        """Calculate sleep time based on meta-intelligence insights"""
        if not self.meta_intelligence_active:
            return 30.0  # Default sleep
        
        # Get cognitive maturity level
        status = self.get_meta_intelligence_status()
        maturity = status.get("cognitive_status", {}).get("maturity_level", 0.1)
        
        # More mature AI can work faster
        base_sleep = 30.0
        maturity_factor = 1.0 - (maturity * 0.5)  # Up to 50% faster
        
        # Recent activity affects sleep
        recent_activity = status.get("cognitive_status", {}).get("recent_activity", 0)
        activity_factor = 1.0 + (recent_activity * 0.1)  # Slow down if very active
        
        intelligent_sleep = base_sleep * maturity_factor * activity_factor
        return max(10.0, min(120.0, intelligent_sleep))  # Between 10s and 2min
