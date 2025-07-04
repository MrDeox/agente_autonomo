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
import re
import asyncio

from agent.project_scanner import update_project_manifest
from agent.brain import (
    generate_next_objective,
    generate_capacitation_objective,
    generate_commit_message
)
from agent.agents import ArchitectAgent, MaestroAgent, CodeReviewAgent
from agent.tool_executor import run_pytest, check_file_existence, run_git_command, read_file
from agent.git_utils import initialize_git_repository
from agent.cycle_runner import CycleRunner
from agent.memory import Memory
from agent.state import AgentState
from agent.validation_steps import get_validation_step
from agent.queue_manager import QueueManager
from agent.cognitive_evolution_manager import get_evolution_manager, start_cognitive_evolution
from agent.async_orchestrator import AsyncAgentOrchestrator, AgentTask, AgentType
from agent.model_optimizer import ModelOptimizer, get_model_optimizer
from agent.advanced_knowledge_system import AdvancedKnowledgeSystem, get_knowledge_system
from agent.root_cause_analyzer import RootCauseAnalyzer, get_root_cause_analyzer
from agent.self_awareness_core import SelfAwarenessCore, get_self_awareness_core
from agent.utils.infrastructure_manager import InfrastructureManager, get_infrastructure_manager
from .hot_reload_manager import HotReloadManager, SelfEvolutionEngine

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

        # Inicializar componentes de meta-inteligência
        self.evolution_manager = get_evolution_manager(self.config, self.logger)
        
        # Usar model_config para compatibilidade
        model_config = self.config.get("models", {}).get("architect_default", "gpt-4")
        
        self.model_optimizer = get_model_optimizer(model_config, self.logger)
        
        self.knowledge_system = get_knowledge_system(model_config, self.logger)
        
        self.root_cause_analyzer = get_root_cause_analyzer(model_config, self.logger)
        
        self.self_awareness_core = get_self_awareness_core(model_config, self.logger)
        
        self.infrastructure_manager = get_infrastructure_manager(self.logger)
        
        # Inicializar orquestrador assíncrono
        self.async_orchestrator = AsyncAgentOrchestrator(self.config, self.logger)
        
        # Estado de meta-inteligência
        self.meta_intelligence_active = False

        # Inicialização dos Agentes Especializados COM INTEGRAÇÃO DE META-INTELIGÊNCIA
        self.architect = ArchitectAgent(
            model_config=self.config.get("models", {}).get("architect_default"),
            logger=self.logger.getChild("ArchitectAgent")
        )
        self.logger.info(f"ArchitectAgent inicializado com a configuração: {self.config.get('models', {}).get('architect_default')}")

        maestro_model_config = self.config.get("models", {}).get("maestro_default")
        self.maestro = MaestroAgent(
            model_config=maestro_model_config,
            config=self.config,
            logger=self.logger.getChild("MaestroAgent")
        )
        self.logger.info(f"MaestroAgent inicializado com a configuração: {maestro_model_config}")

        code_review_model_config = self.config.get("models", {}).get("code_reviewer", self.config.get("models", {}).get("architect_default")) # Fallback to architect model
        self.code_reviewer = CodeReviewAgent(
            model_config=code_review_model_config,
            logger=self.logger.getChild("CodeReviewAgent")
        )
        self.logger.info(f"CodeReviewAgent inicializado com a configuração: {code_review_model_config}")

        self.evolution_log_file = "logs/evolution_log.csv"
        self._initialize_evolution_log()

        self._reset_cycle_state()
        
        # Ensure infrastructure is ready
        if not self.infrastructure_manager.ensure_infrastructure():
            self.logger.warning("⚠️ Infrastructure issues detected - system may not function optimally")
        
        self.logger.info("🧠 Hephaestus initialized with FULL Meta-Intelligence Integration!")
        self.logger.info("🚀 Performance data will be automatically captured for all LLM calls")
        self.logger.info("🔍 Knowledge system ready for intelligent search")
        self.logger.info("⚡ Root cause analysis will detect failure patterns")
        self.logger.info("🧬 Self-awareness core monitoring cognitive state")

        # Hot Reload Manager - Auto-atualização em tempo real
        self.hot_reload_manager = HotReloadManager(self.logger)
        self.self_evolution_engine = SelfEvolutionEngine(self.hot_reload_manager)
        self.real_time_evolution_enabled = False
        
        # Registrar callbacks para hot reload
        self._register_hot_reload_callbacks()
        
        self.logger.info("🔄 Hot Reload capabilities initialized!")

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

    def _gather_information_phase(self) -> bool:
        """
        Analyzes the objective to find file paths and reads their content to provide context.
        """
        self.logger.info("\nAnalisando objetivo para coletar informações...")
        objective = self.state.current_objective
        if not objective:
            return True # No objective, nothing to gather

        # Regex to find potential file paths in the objective string
        # This looks for patterns like `path/to/file.py` or `path/to/file_with_underscores.ext`
        file_paths = re.findall(r'[\w/._-]+\.[\w]+', objective)
        
        if not file_paths:
            self.logger.info("Nenhum caminho de arquivo encontrado no objetivo. Pulando leitura de arquivo.")
            self.state.file_content_context = "No files were read for this objective."
            return True

        # For simplicity, read the first valid file path found
        file_to_read = file_paths[0]
        self.logger.info(f"Arquivo '{file_to_read}' identificado no objetivo para leitura de contexto.")
        
        file_content = read_file(file_to_read)
        if file_content is None:
            self.logger.warning(f"Não foi possível ler o arquivo '{file_to_read}'. Pode não existir.")
            self.state.file_content_context = f"Attempted to read '{file_to_read}' from objective, but it could not be read."
        else:
            self.logger.info(f"Arquivo '{file_to_read}' lido com sucesso para o contexto do Arquiteto.")
            self.state.file_content_context = f"Content of '{file_to_read}':\\n\\n{file_content}"
            
        return True

    def _capture_agent_performance(self, agent_type: str, prompt: str, response: str, 
                                  success: bool, execution_time: float, 
                                  context_metadata: Optional[Dict[str, Any]] = None) -> float:
        """
        Captura automaticamente dados de performance dos agentes para meta-inteligência.
        
        Returns:
            Quality score calculado pelo ModelOptimizer
        """
        try:
            quality_score = self.model_optimizer.capture_performance_data(
                agent_type=agent_type,
                prompt=prompt,
                response=response,
                success=success,
                execution_time=execution_time,
                context_metadata=context_metadata or {"objective": self.state.current_objective}
            )
            
            self.logger.debug(f"📊 Performance captured for {agent_type}: quality={quality_score:.3f}, success={success}")
            return quality_score
            
        except Exception as e:
            self.logger.warning(f"Failed to capture performance data for {agent_type}: {e}")
            return 0.5  # Default score

    def _record_failure_for_analysis(self, agent_type: str, objective: str, error_message: str, 
                                   failure_type: str = "unknown", severity: float = 0.5):
        """
        Registra falhas para análise de causa raiz automática.
        """
        try:
            from agent.root_cause_analyzer import FailureType
            
            # Map string to FailureType enum
            failure_type_map = {
                "validation": FailureType.VALIDATION_FAILURE,
                "syntax": FailureType.SYNTAX_ERROR,
                "timeout": FailureType.TIMEOUT,
                "unknown": FailureType.UNKNOWN
            }
            
            failure_type_enum = failure_type_map.get(failure_type, FailureType.UNKNOWN)
            
            failure_id = self.root_cause_analyzer.record_failure(
                agent_type=agent_type,
                objective=objective,
                error_message=error_message,
                failure_type=failure_type_enum,
                severity=severity
            )
            
            self.logger.debug(f"🔍 Failure recorded for analysis: {failure_id}")
            
            # Trigger analysis if enough failures accumulated
            analysis = self.root_cause_analyzer.analyze_failure_patterns("surface")
            if analysis and analysis.primary_root_causes:
                self.logger.info(f"⚡ Root cause analysis identified {len(analysis.primary_root_causes)} root causes")
                
        except Exception as e:
            self.logger.warning(f"Failed to record failure for analysis: {e}")

    def _run_architect_phase(self) -> bool:
        self.logger.info("\nSolicitando plano de ação do ArchitectAgent...")
        if not self.state.current_objective:
            self.logger.error("--- FALHA: _run_architect_phase chamado sem um objetivo atual definido no estado. ---")
            return False

        start_time = time.time()

        action_plan_data, error_msg = self.architect.plan_action(
            objective=self.state.current_objective,
            manifest=self.state.manifesto_content,
            file_content_context=getattr(self.state, 'file_content_context', '')
        )
        
        execution_time = time.time() - start_time
        success = bool(not error_msg and action_plan_data and "patches_to_apply" in action_plan_data)

        # Capturar dados de performance automaticamente
        self._capture_agent_performance(
            agent_type="architect",
            prompt=f"Objective: {self.state.current_objective[:200]}...",  # Truncated for storage
            response=str(action_plan_data) if action_plan_data else str(error_msg),
            success=success,
            execution_time=execution_time,
            context_metadata={
                "objective": self.state.current_objective,
                "manifest_size": len(self.state.manifesto_content) if self.state.manifesto_content else 0,
                "has_file_context": bool(getattr(self.state, 'file_content_context', ''))
            }
        )

        if error_msg or not action_plan_data or "patches_to_apply" not in action_plan_data:
            self.logger.error(
                f"--- FALHA: ArchitectAgent não conseguiu gerar um plano de ação válido. Erro: {error_msg} ---"
            )
            
            # Registrar falha para análise
            self._record_failure_for_analysis(
                agent_type="architect",
                objective=self.state.current_objective,
                error_message=error_msg or "No action plan generated",
                failure_type="validation",
                severity=0.8
            )
            
            self.state.action_plan_data = {"analysis": "", "patches_to_apply": []}
        else:
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

        start_time = time.time()

        maestro_logs = self.maestro.choose_strategy(
            action_plan_data=self.state.action_plan_data,
            memory_summary=self.memory.get_full_history_for_prompt(),
            failed_strategy_context=failed_strategy_context
        )

        execution_time = time.time() - start_time
        maestro_attempt = next((log for log in maestro_logs if log.get("success") and log.get("parsed_json")), None)

        # Capturar dados de performance
        success = bool(maestro_attempt)
        response_content = str(maestro_attempt.get("parsed_json", {})) if maestro_attempt else "No valid response"
        
        self._capture_agent_performance(
            agent_type="maestro",
            prompt=f"Action Plan Analysis: {str(self.state.action_plan_data)[:200]}...",
            response=response_content,
            success=success,
            execution_time=execution_time,
            context_metadata={
                "objective": self.state.current_objective,
                "has_failed_strategy_context": bool(failed_strategy_context),
                "available_strategies": len(self.config.get("validation_strategies", {}))
            }
        )

        if not maestro_attempt:
            self.logger.error("--- FALHA: MaestroAgent não retornou uma resposta JSON válida e bem-sucedida após todas as tentativas. ---")
            raw_resp_list = [log.get('raw_response', 'No raw response') for log in maestro_logs]
            self.logger.debug(f"Respostas brutas do MaestroAgent: {raw_resp_list}")
            
            # Registrar falha para análise
            self._record_failure_for_analysis(
                agent_type="maestro",
                objective=self.state.current_objective or "Unknown objective",
                error_message="No valid JSON response from MaestroAgent",
                failure_type="validation",
                severity=0.7
            )
            
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
            
            # Registrar falha para análise
            self._record_failure_for_analysis(
                agent_type="maestro",
                objective=self.state.current_objective or "Unknown objective",
                error_message=f"Invalid strategy chosen: {strategy_key}",
                failure_type="validation",
                severity=0.6
            )
            
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
            
            # Activate automatic performance logging for all LLM calls
            self._setup_automatic_performance_logging()
            
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
            self.logger.info("   • Automatically capture performance data from all LLM calls")
            self.logger.info("   • Analyze failure patterns with root cause analysis")
            self.logger.info("   • Acquire new knowledge intelligently when needed")
            self.logger.info("=" * 60)
            
            # Iniciar hot reload para evolução em tempo real
            if self.hot_reload_manager.start_hot_reload():
                self.real_time_evolution_enabled = True
                self.logger.info("🚀 Real-time evolution enabled!")
            else:
                self.logger.warning("⚠️ Hot reload not available - install watchdog for real-time evolution")
    
    def _setup_automatic_performance_logging(self):
        """Setup automatic performance logging for all agent LLM calls"""
        try:
            # Monkey patch the LLM client to automatically capture performance
            from agent.utils import llm_client
            original_call = llm_client.call_llm_api
            
            def captured_call_llm_api(model_config, prompt, temperature, logger_instance, **kwargs):
                start_time = time.time()
                response, error = original_call(model_config, prompt, temperature, logger_instance, **kwargs)
                execution_time = time.time() - start_time
                
                # Extract agent type from logger name if possible
                agent_type = "unknown"
                if hasattr(logger_instance, 'name'):
                    logger_name = logger_instance.name
                    if 'ArchitectAgent' in logger_name:
                        agent_type = "architect"
                    elif 'MaestroAgent' in logger_name:
                        agent_type = "maestro"
                    elif 'CodeReviewAgent' in logger_name:
                        agent_type = "code_review"
                
                # Capture performance data
                try:
                    self.model_optimizer.capture_performance_data(
                        agent_type=agent_type,
                        prompt=prompt[:500],  # Truncate for storage
                        response=response[:1000] if response else "",
                        success=not bool(error),
                        execution_time=execution_time,
                        context_metadata={
                            "model_config": str(model_config),
                            "temperature": temperature,
                            "has_error": bool(error)
                        }
                    )
                except Exception as e:
                    # Don't fail the original call if performance capture fails
                    self.logger.debug(f"Performance capture failed: {e}")
                
                return response, error
            
            # Apply the monkey patch
            llm_client.call_llm_api = captured_call_llm_api
            self.logger.info("🔗 Automatic performance logging activated for all LLM calls")
            
        except Exception as e:
            self.logger.warning(f"Failed to setup automatic performance logging: {e}")
    
    def get_comprehensive_meta_intelligence_status(self) -> Dict[str, Any]:
        """Get comprehensive status including all meta-intelligence systems"""
        if not self.meta_intelligence_active:
            return {"status": "inactive", "message": "Meta-intelligence not activated"}
        
        try:
            return {
                "evolution_manager": self.evolution_manager.get_evolution_report(),
                "model_optimizer": self.model_optimizer.get_optimization_report(),
                "knowledge_system": self.knowledge_system.get_knowledge_report(),
                "root_cause_analyzer": self.root_cause_analyzer.get_analysis_report(),
                "self_awareness": self.self_awareness_core.get_self_awareness_report(),
                "integration_status": {
                    "automatic_performance_capture": True,
                    "failure_analysis": True,
                    "knowledge_acquisition": True,
                    "self_monitoring": True,
                    "infrastructure_ready": self.infrastructure_manager.ensure_infrastructure()
                }
            }
        except Exception as e:
            self.logger.error(f"Failed to get comprehensive status: {e}")
            return {"status": "error", "message": str(e)}
    
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
        status = self.get_comprehensive_meta_intelligence_status()
        maturity = status.get("evolution_manager", {}).get("cognitive_status", {}).get("maturity_level", 0.1)
        
        # More mature AI can work faster
        base_sleep = 30.0
        maturity_factor = 1.0 - (maturity * 0.5)  # Up to 50% faster
        
        # Recent activity affects sleep
        recent_activity = status.get("evolution_manager", {}).get("cognitive_status", {}).get("recent_activity", 0)
        activity_factor = 1.0 + (recent_activity * 0.1)  # Slow down if very active
        
        intelligent_sleep = base_sleep * maturity_factor * activity_factor
        return max(10.0, min(120.0, intelligent_sleep))  # Between 10s and 2min

    async def run_async_evolution_cycle(self, objective: str) -> Dict[str, Any]:
        """
        Executa um ciclo de evolução assíncrono com múltiplos agentes em paralelo.
        
        Esta é a nova funcionalidade que acelera DRASTICAMENTE o processo evolutivo!
        """
        self.logger.info(f"🚀 Starting ASYNC EVOLUTION CYCLE for: {objective}")
        
        # Preparar contexto para os agentes usando dados disponíveis
        context = {
            'current_files': [],  # Lista vazia por enquanto - pode ser expandida later
            'memory_summary': self.memory.get_full_history_for_prompt(),
            'config': self.config,
            'current_objective': objective,
            'manifesto_content': self.state.manifesto_content,
            'file_content_context': getattr(self.state, 'file_content_context', '')
        }
        
        # Criar ciclo de evolução paralelo
        tasks = await self.async_orchestrator.create_parallel_evolution_cycle(objective, context)
        
        self.logger.info(f"📋 Created {len(tasks)} parallel tasks - Maximum evolutionary speed!")
        
        # Executar todas as tarefas em paralelo
        start_time = time.time()
        task_ids = await self.async_orchestrator.submit_parallel_tasks(tasks)
        
        # Aguardar conclusão de todas as tarefas
        results = {}
        for task_id in task_ids:
            if task_id in self.async_orchestrator.completed_tasks:
                results[task_id] = self.async_orchestrator.completed_tasks[task_id]
            elif task_id in self.async_orchestrator.failed_tasks:
                results[task_id] = self.async_orchestrator.failed_tasks[task_id]
        
        total_time = time.time() - start_time
        
        self.logger.info(f"⚡ ASYNC EVOLUTION COMPLETE in {total_time:.2f}s!")
        self.logger.info(f"   • {len([r for r in results.values() if r.success])} tasks succeeded")
        self.logger.info(f"   • {len([r for r in results.values() if not r.success])} tasks failed")
        
        # Processar resultados
        evolution_results = {
            "objective": objective,
            "execution_time": total_time,
            "tasks_executed": len(tasks),
            "successful_tasks": len([r for r in results.values() if r.success]),
            "failed_tasks": len([r for r in results.values() if not r.success]),
            "parallel_efficiency": self._calculate_parallel_efficiency(results, total_time),
            "results": results,
            "orchestration_status": self.async_orchestrator.get_orchestration_status()
        }
        
        return evolution_results
    
    def _calculate_parallel_efficiency(self, results: Dict[str, Any], total_time: float) -> float:
        """Calcula eficiência da execução paralela"""
        if not results:
            return 0.0
        
        # Tempo total se fosse sequencial
        sequential_time = sum(r.execution_time for r in results.values())
        
        # Eficiência paralela
        efficiency = sequential_time / total_time if total_time > 0 else 0.0
        
        return min(efficiency, len(results))  # Máximo teórico é o número de tarefas
    
    def enable_turbo_evolution_mode(self):
        """Ativa o modo turbo de evolução com máximo paralelismo"""
        self.logger.info("🔥 TURBO EVOLUTION MODE ACTIVATED!")
        
        # Configurar orquestrador para máximo paralelismo
        self.async_orchestrator.max_concurrent_agents = 8
        
        # Recriar semáforos com maior concorrência
        for agent_type in self.async_orchestrator.semaphores:
            self.async_orchestrator.semaphores[agent_type] = asyncio.Semaphore(8)
        
        # Reduzir timeouts para execução mais rápida
        self.async_orchestrator.default_timeout = 180  # 3 minutos
        
        self.logger.info("⚡ TURBO MODE: 8 concurrent agents, reduced timeouts!")
        self.logger.info("🚀 Evolution speed increased by 4-8x!")
    
    def get_async_orchestration_status(self) -> Dict[str, Any]:
        """Retorna status detalhado da orquestração assíncrona"""
        return {
            "orchestrator_status": self.async_orchestrator.get_orchestration_status(),
            "turbo_mode": self.async_orchestrator.max_concurrent_agents > 4,
            "evolution_capability": "parallel_multi_agent",
            "performance_multiplier": f"{self.async_orchestrator.max_concurrent_agents}x",
            "active_systems": [
                "async_orchestrator",
                "parallel_evolution",
                "concurrent_agents",
                "dependency_management",
                "performance_optimization"
            ]
        }

    def stop_meta_intelligence(self):
        """Stop the meta-intelligence system"""
        if self.meta_intelligence_active:
            self.logger.info("🛑 DEACTIVATING META-INTELLIGENCE - AI will no longer evolve itself!")
            
            # Stop cognitive evolution
            self.evolution_manager.stop_cognitive_evolution()
            self.meta_intelligence_active = False
            
            # Stop self-awareness monitoring
            self.self_awareness_core.stop_continuous_self_monitoring()
            
            # Deactivate automatic performance logging for all LLM calls
            self._teardown_automatic_performance_logging()
            
            self.logger.info("🧬 Meta-Intelligence DEACTIVATED - The AI is now static!")
            
            # Log this historic moment
            self.logger.info("=" * 60)
            self.logger.info("🎯 HISTORIC MOMENT: AI LOSES SELF-MODIFICATION CAPABILITY")
            self.logger.info("🔥 The system can no longer:")
            self.logger.info("   • Evolve its own prompts using genetic algorithms")
            self.logger.info("   • Create new agents when needed")
            self.logger.info("   • Modify its own cognitive architecture")
            self.logger.info("   • Develop meta-cognitive awareness")
            self.logger.info("   • Adapt and improve autonomously")
            self.logger.info("   • Continuously monitor its own consciousness")
            self.logger.info("   • Perform deep introspection and self-reflection")
            self.logger.info("   • Automatically capture performance data from all LLM calls")
            self.logger.info("   • Analyze failure patterns with root cause analysis")
            self.logger.info("   • Acquire new knowledge intelligently when needed")
            self.logger.info("=" * 60)
            
            # Parar hot reload
            if self.hot_reload_manager:
                self.hot_reload_manager.stop_hot_reload()
                self.real_time_evolution_enabled = False
                self.logger.info("🛑 Real-time evolution stopped")
    
    def _teardown_automatic_performance_logging(self):
        """Teardown automatic performance logging for all agent LLM calls"""
        try:
            # Monkey patch the LLM client to automatically capture performance
            from agent.utils import llm_client
            original_call = llm_client.call_llm_api
            
            def captured_call_llm_api(model_config, prompt, temperature, logger_instance, **kwargs):
                start_time = time.time()
                response, error = original_call(model_config, prompt, temperature, logger_instance, **kwargs)
                execution_time = time.time() - start_time
                
                # Extract agent type from logger name if possible
                agent_type = "unknown"
                if hasattr(logger_instance, 'name'):
                    logger_name = logger_instance.name
                    if 'ArchitectAgent' in logger_name:
                        agent_type = "architect"
                    elif 'MaestroAgent' in logger_name:
                        agent_type = "maestro"
                    elif 'CodeReviewAgent' in logger_name:
                        agent_type = "code_review"
                
                # Capture performance data
                try:
                    self.model_optimizer.capture_performance_data(
                        agent_type=agent_type,
                        prompt=prompt[:500],  # Truncate for storage
                        response=response[:1000] if response else "",
                        success=not bool(error),
                        execution_time=execution_time,
                        context_metadata={
                            "model_config": str(model_config),
                            "temperature": temperature,
                            "has_error": bool(error)
                        }
                    )
                except Exception as e:
                    # Don't fail the original call if performance capture fails
                    self.logger.debug(f"Performance capture failed: {e}")
                
                return response, error
            
            # Apply the monkey patch
            llm_client.call_llm_api = original_call
            self.logger.info("🔗 Automatic performance logging deactivated for all LLM calls")
            
        except Exception as e:
            self.logger.warning(f"Failed to teardown automatic performance logging: {e}")
    
    def enable_real_time_evolution(self):
        """Habilitar evolução em tempo real"""
        if not self.real_time_evolution_enabled:
            if self.hot_reload_manager.start_hot_reload():
                self.real_time_evolution_enabled = True
                self.logger.info("🚀 Real-time evolution enabled!")
                return True
        return False
    
    def disable_real_time_evolution(self):
        """Desabilitar evolução em tempo real"""
        if self.real_time_evolution_enabled:
            self.hot_reload_manager.stop_hot_reload()
            self.real_time_evolution_enabled = False
            self.logger.info("⏸️ Real-time evolution disabled")
            return True
        return False
    
    def self_modify_code(self, module_name: str, new_code: str):
        """Permitir que o agente modifique seu próprio código"""
        try:
            self.logger.info(f"🧬 Self-modifying code for module: {module_name}")
            
            # Usar o hot reload manager para modificar código
            success = self.hot_reload_manager.self_modify_code(module_name, new_code)
            
            if success:
                self.logger.info("✅ Self-modification successful!")
                
                # Registrar na evolução
                self.evolution_manager.register_evolution_event({
                    "type": "self_modification",
                    "module": module_name,
                    "timestamp": time.time(),
                    "success": True
                })
            else:
                self.logger.error("❌ Self-modification failed!")
            
            return success
            
        except Exception as e:
            self.logger.error(f"❌ Error in self-modification: {e}")
            return False
    
    def dynamic_import_code(self, code: str, module_name: str = None):
        """Importar código dinamicamente"""
        try:
            self.logger.info(f"🔧 Dynamic import: {module_name or 'anonymous'}")
            
            # Usar hot reload manager para importação dinâmica
            module = self.hot_reload_manager.dynamic_import(code, module_name)
            
            if module:
                self.logger.info("✅ Dynamic import successful!")
                return module
            else:
                self.logger.error("❌ Dynamic import failed!")
                return None
                
        except Exception as e:
            self.logger.error(f"❌ Error in dynamic import: {e}")
            return None
    
    def trigger_self_evolution(self):
        """Disparar auto-evolução baseada em performance"""
        try:
            self.logger.info("🧬 Triggering self-evolution...")
            
            # Usar self evolution engine
            success = self.self_evolution_engine.analyze_performance_and_evolve()
            
            if success:
                self.logger.info("✅ Self-evolution completed successfully!")
                
                # Registrar evolução
                self.evolution_manager.register_evolution_event({
                    "type": "self_evolution",
                    "timestamp": time.time(),
                    "success": True
                })
            
            return success
            
        except Exception as e:
            self.logger.error(f"❌ Error in self-evolution: {e}")
            return False
    
    def get_real_time_evolution_status(self):
        """Obter status da evolução em tempo real"""
        return {
            "real_time_evolution_enabled": self.real_time_evolution_enabled,
            "hot_reload_status": self.hot_reload_manager.get_evolution_status(),
            "self_modification_capability": True,
            "dynamic_import_capability": True,
            "auto_evolution_enabled": self.hot_reload_manager.auto_evolution_enabled
        }
    
    def _register_hot_reload_callbacks(self):
        """Registrar callbacks para quando módulos forem recarregados"""
        try:
            # Callback para quando este próprio agente for recarregado
            def on_agent_reload(new_module, old_module):
                self.logger.info("🔄 HephaestusAgent module reloaded!")
                # Aqui poderia recarregar configurações, reconectar componentes, etc.
            
            self.hot_reload_manager.register_reload_callback(
                "agent.hephaestus_agent", 
                on_agent_reload
            )
            
            # Callback para módulos de agentes
            def on_agents_reload(new_module, old_module):
                self.logger.info("🤖 Agents module reloaded!")
                # Recarregar agentes específicos se necessário
            
            self.hot_reload_manager.register_reload_callback(
                "agent.agents", 
                on_agents_reload
            )
            
            # Callback para configurações
            def on_config_reload(new_module, old_module):
                self.logger.info("⚙️ Config module reloaded!")
                # Recarregar configurações
                try:
                    from .config_loader import load_config
                    new_config = load_config()
                    # Atualizar configurações sem quebrar o estado atual
                    self.logger.info("✅ Configuration updated!")
                except Exception as e:
                    self.logger.error(f"❌ Error reloading config: {e}")
            
            self.hot_reload_manager.register_reload_callback(
                "agent.config_loader", 
                on_config_reload
            )
            
        except Exception as e:
            self.logger.error(f"❌ Error registering hot reload callbacks: {e}")
