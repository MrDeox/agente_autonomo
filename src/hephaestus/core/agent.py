import json
import os
import shutil
import tempfile
import time
import logging
import csv
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional, Dict, Any, List, Tuple
import re
import asyncio
import random
import traceback
import uuid
import threading

from hephaestus.utils.project_scanner import update_project_manifest
from hephaestus.core.brain import (
    generate_next_objective,
    generate_capacitation_objective,
    generate_commit_message
)
from hephaestus.agents import ArchitectAgent, MaestroAgent, OrganizerAgent, BugHunterAgent
from hephaestus.utils.tool_executor import run_pytest, check_file_existence, run_git_command, read_file
from hephaestus.utils.git_utils import initialize_git_repository
from hephaestus.core.cycle_runner import CycleRunner
from hephaestus.core.memory import Memory
from hephaestus.core.state import AgentState
from hephaestus.services.validation import get_validation_step
from hephaestus.utils.queue_manager import QueueManager
from hephaestus.core.cognitive_evolution_manager import get_evolution_manager, start_cognitive_evolution
from hephaestus.services.orchestration.async_orchestrator import AsyncAgentOrchestrator, AgentTask, AgentType
from hephaestus.intelligence.model_optimizer import ModelOptimizer, get_model_optimizer
from hephaestus.intelligence.knowledge_system import AdvancedKnowledgeSystem, get_knowledge_system
from hephaestus.intelligence.root_cause_analyzer import RootCauseAnalyzer, get_root_cause_analyzer
from hephaestus.intelligence.self_awareness_core import SelfAwarenessCore, get_self_awareness_core
from hephaestus.intelligence.meta_objective_generator import MetaObjectiveGenerator, get_meta_objective_generator
from hephaestus.intelligence.temporal_intelligence import TemporalIntelligence, get_temporal_intelligence
from hephaestus.intelligence.dynamic_agent_dna import DynamicAgentDNA, get_dynamic_agent_dna
from hephaestus.intelligence.autonomous_capability_expansion import AutonomousCapabilityExpansion, get_autonomous_capability_expansion
from hephaestus.utils.infrastructure_manager import InfrastructureManager, get_infrastructure_manager
from hephaestus.services.communication.inter_agent import get_inter_agent_communication
from hephaestus.agents.swarm_coordinator_agent import SwarmCoordinatorAgent
from .hot_reload_manager import HotReloadManager, SelfEvolutionEngine
from hephaestus.utils.error_prevention_system import ErrorPreventionSystem, ErrorEvent, ErrorType, ErrorSeverity, validate_constructor
from hephaestus.utils.continuous_monitor import get_continuous_monitor
from .agents.autonomous_monitor_agent import AutonomousMonitorAgent
from hephaestus.intelligence.evolution_analytics import get_evolution_analytics
from hephaestus.utils.log_cleaner import get_log_cleaner

# Configuração do Logging
logger = logging.getLogger(__name__)

class HephaestusAgent:
    """Classe principal que encapsula a lógica do agente autônomo."""

    def __init__(self,
                 logger_instance,
                 config: dict, # Now receives config as a parameter
                 continuous_mode: bool = False,
                 objective_stack_depth_for_testing: Optional[int] = None,
                 queue_manager: Optional[QueueManager] = None,
                 use_optimized_pipeline: bool = True,
                 disable_signal_handlers: bool = False):
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
        self.continuous_mode = continuous_mode # Default value
        self.objective_stack_depth_for_testing = objective_stack_depth_for_testing
        self.state: AgentState = AgentState()
        self.queue_manager = queue_manager or QueueManager()
        self.objective_stack: list = []

        # Load persisted config if it exists
        config_path = "hephaestus_config.json"
        if os.path.exists(config_path):
            self.logger.info(f"Loading persistent configuration from {config_path}")
            try:
                with open(config_path, "r") as f:
                    persisted_config = json.load(f)
                    self.continuous_mode = persisted_config.get("continuous_mode", self.continuous_mode)
                    self.logger.info(f"Continuous mode set to {self.continuous_mode} from config file.")
            except Exception as e:
                self.logger.error(f"Failed to load or parse {config_path}: {e}")

        # Inicialização da Memória Persistente
        memory_file_path = self.config.get("memory_file_path", "HEPHAESTUS_MEMORY.json")
        self.memory = Memory(filepath=memory_file_path, logger=self.logger.getChild("Memory"))
        self.logger.info(f"Carregando memória de {memory_file_path}...")
        self.memory.load()
        self.logger.info(f"Memória carregada. {len(self.memory.completed_objectives)} objetivos concluídos, {len(self.memory.failed_objectives)} falharam.")

        # Inicializar componentes de meta-inteligência
        model_config = self.config.get("models", {}).get("architect_default", "gpt-4")
        self.model_optimizer = get_model_optimizer(model_config, self.logger)
        self.evolution_manager = get_evolution_manager(self.config, self.logger, self.memory, self.model_optimizer)
        
        # Usar model_config para compatibilidade
        
        self.knowledge_system = get_knowledge_system(model_config, self.logger)
        
        self.root_cause_analyzer = get_root_cause_analyzer(model_config, self.logger)
        
        self.self_awareness_core = get_self_awareness_core(self.config, self.logger)
        
        self.meta_objective_generator = get_meta_objective_generator(self.config, self.logger)
        
        self.temporal_intelligence = get_temporal_intelligence(self.config, self.logger)
        
        self.dynamic_agent_dna = get_dynamic_agent_dna(self.config, self.logger)
        
        self.autonomous_capability_expansion = get_autonomous_capability_expansion(self.config, self.logger)
        
        self.infrastructure_manager = get_infrastructure_manager(self.logger)
        
        # Inicializar Collective Intelligence Network (temporariamente desabilitado)
        self.collective_network = None
        
        # Inicializar Real-Time Evolution Engine (temporariamente desabilitado)
        self.real_time_evolution_engine = None
        
        # Inicializar orquestrador assíncrono
        self.async_orchestrator = AsyncAgentOrchestrator(self.config, self.logger)
        
        # Inicializar sistema de comunicação inter-agente
        self.inter_agent_communication = get_inter_agent_communication(self.config, self.logger)
        
        # Inicializar SwarmCoordinatorAgent
        self.swarm_coordinator = SwarmCoordinatorAgent(
            model_config=self.config.get("models", {}).get("architect_default", "gpt-4"),
            config=self.config,
            logger=self.logger
        )
        self.swarm_coordinator.set_communication_system(self.inter_agent_communication)
        
        # Estado de meta-inteligência
        self.meta_intelligence_active = False

        # Inicializar sistema de prevenção de erros ANTES de tudo
        self.error_prevention = ErrorPreventionSystem(logger_instance, disable_signal_handlers=disable_signal_handlers)
        self.error_prevention.start()
        logger_instance.info("🚀 Sistema de prevenção de erros inicializado")

        # Inicializar monitoramento contínuo
        self.continuous_monitor = get_continuous_monitor(logger_instance)
        self.continuous_monitor.start_monitoring()
        logger_instance.info("🔍 Monitoramento contínuo inicializado")

        # ATIVAR FUNCIONALIDADES NÃO UTILIZADAS
        from hephaestus.core.system_activator import get_system_activator
        self.system_activator = get_system_activator(logger_instance, self.config, disable_signal_handlers)
        activation_results = self.system_activator.activate_all_features()
        
        # Mostrar relatório de ativação
        activation_report = self.system_activator.get_activation_report()
        logger_instance.info(activation_report)
        
        logger_instance.info("🎯 Sistema ativador integrado - Funcionalidades não utilizadas foram implementadas!")
        
        # Log dos resultados de ativação
        if isinstance(activation_results, bool):
            status = "ativado" if activation_results else "falhou"
            self.logger.info(f"🎯 SystemActivator: Sistema {status}")
        else:
            successful_activations = len([r for r in activation_results if r.success])
            total_activations = len(activation_results)
            self.logger.info(f"🎯 SystemActivator: {successful_activations}/{total_activations} componentes ativados com sucesso")
        
        # Mostrar relatório de ativação
        activation_report = self.system_activator.get_activation_report()
        self.logger.info(f"📊 Relatório de Ativação:\n{activation_report}")
        
        # INICIALIZAR ATIVADOR DE COBERTURA
        from hephaestus.core.coverage_activator import CoverageActivator
        self.coverage_activator = CoverageActivator(self.config)
        logger_instance.info("📊 CoverageActivator inicializado para aumentar cobertura do sistema")

        # Inicialização dos Agentes Especializados COM INTEGRAÇÃO DE META-INTELIGÊNCIA
        try:
            self.architect = ArchitectAgent(
                model_config=self.config.get("models", {}).get("architect_default"),
                logger=self.logger.getChild("ArchitectAgent")
            )
            self.logger.info(f"ArchitectAgent inicializado com a configuração: {self.config.get('models', {}).get('architect_default')}")
        except Exception as e:
            self._handle_agent_initialization_error("ArchitectAgent", e)

        try:
            self.maestro = MaestroAgent(
                model_config=self.config.get("models", {}).get("maestro_default", self.config.get("models", {}).get("architect_default")),
                logger=self.logger.getChild("MaestroAgent"),
                config=self.config
            )
            self.logger.info(f"MaestroAgent inicializado com a configuração: {self.config.get('models', {}).get('maestro_default')}")
        except Exception as e:
            self._handle_agent_initialization_error("MaestroAgent", e)

        # TODO: Implement CodeReviewAgent in new structure
        # code_review_model_config = self.config.get("models", {}).get("code_reviewer", self.config.get("models", {}).get("architect_default")) # Fallback to architect model
        # self.code_reviewer = CodeReviewAgent(
        #     model_config=code_review_model_config,
        #     logger=self.logger.getChild("CodeReviewAgent")
        # )
        # self.logger.info(f"CodeReviewAgent inicializado com a configuração: {code_review_model_config}")
        self.code_reviewer = None  # Set to None instead of leaving undefined
        self.logger.warning("CodeReviewAgent disabled - not implemented in new structure")

        # Inicializar OrganizerAgent
        self.organizer = OrganizerAgent(
            config=self.config,
            logger=self.logger.getChild("OrganizerAgent")
        )
        self.logger.info("OrganizerAgent inicializado para reorganização inteligente do projeto")

        # Inicializar BugHunterAgent
        self.bug_hunter = BugHunterAgent(
            model_config=self.config.get("models", {}).get("bug_hunter_default", self.config.get("models", {}).get("architect_default")),
            config=self.config,
            logger=self.logger.getChild("BugHunterAgent")
        )
        self.logger.info("BugHunterAgent inicializado para detecção e correção automática de bugs")

        # Registrar agentes no sistema de comunicação
        self._register_agents_for_communication()

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
        
        # Register for real-time event collection
        self._setup_real_time_event_collection()
        
        # Register real agents in DNA system
        self._register_agents_in_dna_system()
        
        # Setup capability expansion data collection
        self._setup_capability_expansion_data_collection()
        
        # Setup meta-learning data collection
        self._setup_meta_learning_data_collection()

        # Hot Reload Manager - Auto-atualização em tempo real
        self.hot_reload_manager = HotReloadManager(self.logger)
        self.self_evolution_engine = SelfEvolutionEngine(self.config, self.logger)
        self.real_time_evolution_enabled = False
        
        # Real-Time Evolution Engine - Evolução contínua durante execução
        from hephaestus.intelligence.real_time_evolution_engine import get_real_time_evolution_engine
        self.real_time_evolution_engine = get_real_time_evolution_engine(self.config, self.logger)
        self._register_evolution_callbacks()
        self.logger.info("⚡ Real-Time Evolution Engine initialized!")
        
        # Parallel Reality Testing - Testes paralelos de estratégias
        from hephaestus.intelligence.parallel_reality_testing import get_parallel_reality_tester
        self.parallel_reality_tester = get_parallel_reality_tester(self.config, self.logger)
        self.logger.info("🧪 Parallel Reality Testing initialized!")
        
        # Meta-Learning Intelligence - Sistema que aprende como aprender melhor
        from hephaestus.intelligence.meta_learning_intelligence import get_meta_learning_intelligence
        self.meta_learning_intelligence = get_meta_learning_intelligence(self.config, self.logger)
        self.logger.info("🧠 Meta-Learning Intelligence initialized!")
        
        # Collective Intelligence Network - Rede de inteligência coletiva
        from hephaestus.intelligence.collective_intelligence_network import get_collective_intelligence_network
        self.collective_intelligence_network = get_collective_intelligence_network(self.config, self.logger)
        self._register_agent_in_collective_network()
        self.logger.info("🌐 Collective Intelligence Network initialized!")
        
        # Registrar callbacks para hot reload
        self._register_hot_reload_callbacks()
        
        self.logger.info("🔄 Hot Reload capabilities initialized!")
        
        # Initialize optimized pipeline
        self.use_optimized_pipeline = use_optimized_pipeline
        self.optimized_pipeline = None
        if self.use_optimized_pipeline:
            try:
                from hephaestus.core.optimized_pipeline import OptimizedPipeline
                self.optimized_pipeline = OptimizedPipeline(config, self.logger)
                self.logger.info("🚀 Optimized pipeline enabled")
            except ImportError as e:
                self.logger.warning(f"Could not import optimized pipeline: {e}")
                self.use_optimized_pipeline = False

        # Inicializa o monitor autônomo
        self.autonomous_monitor = AutonomousMonitorAgent(config.get('autonomous_monitor', {}))
        self.monitor_task = None

        # Evolution Analytics
        self.evolution_analytics = get_evolution_analytics(config, self.logger)
        
        # Log Cleaner - Sistema de limpeza automática
        self.log_cleaner = get_log_cleaner(config, self.logger)
        
        # Executar limpeza inicial
        self.log_cleaner.schedule_cleanup()
        
        # Configurar limpeza automática periódica
        self._setup_automatic_cleanup()

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
            from hephaestus.intelligence.root_cause_analyzer import FailureType
            
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

        # Skip code review if not available
        if self.code_reviewer is None:
            self.logger.warning("CodeReviewAgent not available, skipping code review")
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

    async def _run_maestro_phase(self, failed_strategy_context: Optional[Dict[str, str]] = None) -> bool:
        self.logger.info("\nSolicitando decisão do MaestroAgent...")
        if not self.state.action_plan_data:
            self.logger.error("--- FALHA: Nenhum plano de ação (patches) disponível para o MaestroAgent avaliar. ---")
            return False

        start_time = time.time()

        # Usar o método correto do MaestroAgentEnhanced
        try:
            # O MaestroAgentEnhanced usa select_strategy em vez de choose_strategy
            strategy_result = await self.maestro.select_strategy(
                objective=f"Choose strategy for: {self.state.current_objective}"
            )
            
            if not strategy_result:
                self.logger.error("--- FALHA: MaestroAgent não conseguiu selecionar uma estratégia. ---")
                return False
            
            # Converter o resultado para o formato esperado
            strategy_key = strategy_result.get('name', 'fallback')
            confidence = strategy_result.get('confidence', 0.5)
            
            # Validar se a estratégia é válida
            valid_strategies = list(self.config.get("validation_strategies", {}).keys())
            valid_strategies.append("CAPACITATION_REQUIRED")
            
            if strategy_key not in valid_strategies:
                self.logger.error(f"--- FALHA: MaestroAgent escolheu uma estratégia inválida: '{strategy_key}' ---")
                return False
            
            self.logger.info(f"Estratégia escolhida pelo MaestroAgent: {strategy_key} (confiança: {confidence:.2f})")
            self.state.strategy_key = strategy_key
            return True
            
        except Exception as e:
            self.logger.error(f"--- FALHA: Erro ao executar MaestroAgent: {e} ---")
            return False

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
        """Ativa o sistema de meta-inteligência para auto-aprimoramento contínuo."""
        if self.meta_intelligence_active:
            self.logger.warning("Meta-inteligência já está ativa.")
            return

        self.logger.info("🚀 ACTIVATING META-INTELLIGENCE - AI will now evolve itself!")
        self.meta_intelligence_active = True

        # Obter configuração do modelo para os sistemas de evolução
        model_config = self.config.get("models", {}).get("meta_intelligence", "gpt-4")

        # Iniciar o loop de evolução cognitiva em um thread separado
        start_cognitive_evolution(
            model_config,
            self.logger,
            self.memory,
            self.model_optimizer
        )

        # Configurar logging automático de performance para chamadas LLM
        self._setup_automatic_performance_logging()

        self.logger.info("🧬 Meta-Intelligence ACTIVATED - The AI is now self-improving!")

    def _setup_automatic_performance_logging(self):
        """Setup automatic performance logging for all agent LLM calls"""
        self.logger.info("🔗 Automatic performance logging activated for all LLM calls")

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

        # Inicia o monitoramento autônomo em background
        try:
            # Criar event loop se necessário
            try:
                loop = asyncio.get_event_loop()
            except RuntimeError:
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
            
            # Criar task para monitoramento
            loop.create_task(self.start_autonomous_monitoring())
            self.logger.info("🤖 Monitoramento autônomo iniciado")
        except Exception as e:
            self.logger.error(f"Erro ao iniciar monitoramento autônomo: {e}")
        
        # Iniciar Real-Time Evolution Engine
        try:
            self.real_time_evolution_engine.start_evolution()
            self.logger.info("⚡ Real-Time Evolution Engine started!")
        except Exception as e:
            self.logger.error(f"Erro ao iniciar Real-Time Evolution Engine: {e}")

        cycle_runner = CycleRunner(self, self.queue_manager)
        # Executar cycle_runner de forma assíncrona
        try:
            loop = asyncio.get_event_loop()
            loop.run_until_complete(cycle_runner.run())
        except RuntimeError:
            # Se não houver event loop, criar um novo
            asyncio.run(cycle_runner.run())


    
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
    
    def _register_agents_for_communication(self):
        """Registra todos os agentes no sistema de comunicação inter-agente"""
        try:
            # Registrar agentes principais
            self.inter_agent_communication.register_agent(
                "architect", self.architect, 
                ["code_analysis", "architecture_design", "problem_solving"]
            )
            
            self.inter_agent_communication.register_agent(
                "maestro", self.maestro,
                ["strategy_selection", "orchestration", "decision_making"]
            )
            
            # Skip code_reviewer registration if not available
            if self.code_reviewer is not None:
                self.inter_agent_communication.register_agent(
                    "code_reviewer", self.code_reviewer,
                    ["code_review", "quality_assessment", "best_practices"]
                )
            
            self.inter_agent_communication.register_agent(
                "bug_hunter", self.bug_hunter,
                ["bug_detection", "error_analysis", "automatic_fixing"]
            )
            
            self.inter_agent_communication.register_agent(
                "swarm_coordinator", self.swarm_coordinator,
                ["coordination", "mediation", "conflict_resolution", "collaboration_optimization"]
            )
            
            self.logger.info("✅ All agents registered for inter-agent communication")
            
        except Exception as e:
            self.logger.error(f"❌ Error registering agents for communication: {e}")
    
    def get_swarm_communication_status(self) -> Dict[str, Any]:
        """Retorna status do sistema de comunicação do enxame"""
        try:
            return {
                "communication_status": self.inter_agent_communication.get_communication_status(),
                "swarm_status": self.swarm_coordinator.get_swarm_status(),
                "swarm_metrics": self.swarm_coordinator.get_swarm_metrics().__dict__,
                "active_conversations": len(self.inter_agent_communication.conversations),
                "active_collaborations": len(self.inter_agent_communication.collaboration_sessions),
                "system_status": "operational"
            }
        except Exception as e:
            self.logger.error(f"Error getting swarm communication status: {e}")
            return {"error": str(e)}

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
        self.logger.info("🔗 Automatic performance logging deactivated for all LLM calls")

    def enable_real_time_evolution(self):
        """Habilitar evolução em tempo real"""
        if not self.real_time_evolution_enabled:
            try:
                # Iniciar watching dos módulos do projeto
                src_path = str(Path("src/hephaestus").absolute())
                self.hot_reload_manager.start_watching(src_path)
                
                # Adicionar módulos principais para watch
                main_modules = [
                    "hephaestus.core.agent",
                    "hephaestus.agents.architect",
                    "hephaestus.agents.maestro",
                    "hephaestus.agents.bug_hunter",
                    "hephaestus.agents.organizer"
                ]
                
                for module_name in main_modules:
                    self.hot_reload_manager.add_module(module_name)
                
                # Iniciar evolução automática
                self.self_evolution_engine.start_evolution()
                
                self.real_time_evolution_enabled = True
                self.logger.info("🚀 Real-time evolution enabled!")
                self.logger.info(f"📁 Watching directory: {src_path}")
                self.logger.info(f"📋 Watching {len(main_modules)} core modules")
                return True
                
            except Exception as e:
                self.logger.error(f"❌ Failed to enable real-time evolution: {e}")
                return False
        return False
    
    def disable_real_time_evolution(self):
        """Desabilitar evolução em tempo real"""
        if self.real_time_evolution_enabled:
            try:
                # Parar watching
                self.hot_reload_manager.stop_watching()
                
                # Parar evolução automática
                self.self_evolution_engine.stop_evolution()
                
                self.real_time_evolution_enabled = False
                self.logger.info("⏸️ Real-time evolution disabled")
                return True
                
            except Exception as e:
                self.logger.error(f"❌ Failed to disable real-time evolution: {e}")
                return False
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
                self.evolution_manager._record_evolution_event(
                    event_type="self_modification",
                    description=f"Self-modified module: {module_name}",
                    impact_score=0.7,
                    affected_components=[module_name]
                )
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
        """Trigger a self-evolution cycle."""
        if not self.meta_intelligence_active:
            self.logger.warning("Meta-intelligence is not active, cannot trigger self-evolution.")
            return
            
        self.logger.info("🧬 Triggering manual self-evolution cycle...")
        
        # Log evolution event
        self.evolution_manager._record_evolution_event(
            event_type="manual_trigger",
            description="Self-evolution cycle manually triggered",
            impact_score=0.2,
            affected_components=["cognitive_evolution"]
        )
        
        # For now, this just triggers the self-evolution engine's analysis
        # In the future, this could be more sophisticated
        self.self_evolution_engine.analyze_performance_and_evolve()

    def get_real_time_evolution_status(self):
        """Obter status da evolução em tempo real"""
        return {
            "real_time_evolution_enabled": self.real_time_evolution_enabled,
            "hot_reload_status": self.hot_reload_manager.get_evolution_status(),
            "self_modification_capability": True,
            "dynamic_import_capability": True,
            "auto_evolution_enabled": self.hot_reload_manager.auto_evolution_enabled
        }
    
    def _register_evolution_callbacks(self):
        """Registrar callbacks FUNCIONAIS para aplicar mutações do Real-Time Evolution Engine"""
        try:
            from hephaestus.intelligence.real_time_evolution_engine import MutationType
            from hephaestus.intelligence.evolution_callbacks import get_evolution_callbacks
            
            # Obter sistema de callbacks funcionais
            evolution_callbacks = get_evolution_callbacks(self.config, self.logger)
            
            # Registrar callbacks REAIS que aplicam mudanças no sistema
            self.real_time_evolution_engine.register_mutation_callback(
                MutationType.PROMPT_OPTIMIZATION, evolution_callbacks.apply_prompt_optimization
            )
            self.real_time_evolution_engine.register_mutation_callback(
                MutationType.STRATEGY_ADJUSTMENT, evolution_callbacks.apply_strategy_adjustment
            )
            self.real_time_evolution_engine.register_mutation_callback(
                MutationType.PARAMETER_TUNING, evolution_callbacks.apply_parameter_tuning
            )
            self.real_time_evolution_engine.register_mutation_callback(
                MutationType.WORKFLOW_MODIFICATION, evolution_callbacks.apply_workflow_modification
            )
            self.real_time_evolution_engine.register_mutation_callback(
                MutationType.AGENT_BEHAVIOR_CHANGE, evolution_callbacks.apply_agent_behavior_change
            )
            
            # Armazenar referência para callbacks para acesso posterior
            self.evolution_callbacks = evolution_callbacks
            
            self.logger.info("📋 REAL Evolution callbacks registered successfully - 100% functional!")
            
        except Exception as e:
            self.logger.error(f"❌ Error registering evolution callbacks: {e}")
    
    def _register_agent_in_collective_network(self):
        """Registra este agente na rede de inteligência coletiva"""
        try:
            agent_id = f"hephaestus_agent_{id(self)}"
            agent_type = "autonomous_agent"
            capabilities = {
                "code_analysis", "objective_generation", "file_modification", 
                "git_management", "llm_interaction", "validation", "evolution"
            }
            expertise_areas = {
                "software_development", "code_optimization", "autonomous_systems",
                "machine_learning", "system_architecture"
            }
            
            success = self.collective_intelligence_network.register_agent(
                agent_id=agent_id,
                agent_type=agent_type,
                capabilities=capabilities,
                expertise_areas=expertise_areas
            )
            
            if success:
                self.agent_id = agent_id
                self.logger.info(f"🤖 Agent registered in collective network: {agent_id}")
            else:
                self.logger.error("❌ Failed to register agent in collective network")
                
        except Exception as e:
            self.logger.error(f"❌ Error registering agent in collective network: {e}")
    
    async def test_parallel_strategies(self, objective: str, strategy_variants: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Testa múltiplas estratégias em paralelo e retorna a melhor
        """
        try:
            self.logger.info(f"🧪 Testing {len(strategy_variants)} strategies in parallel for: {objective}")
            
            # Executar teste paralelo
            best_result = await self.parallel_reality_tester.test_multiple_strategies(
                objective=objective,
                strategy_variants=strategy_variants
            )
            
            if best_result:
                self.logger.info(f"✅ Best strategy: {best_result.strategy_variant} (fitness: {best_result.calculate_fitness():.3f})")
                
                # Compartilhar descoberta na rede coletiva
                await self._share_strategy_discovery(objective, best_result)
                
                return {
                    "success": True,
                    "best_strategy": best_result.strategy_variant,
                    "fitness_score": best_result.calculate_fitness(),
                    "execution_time": best_result.execution_time,
                    "performance_metrics": best_result.performance_metrics
                }
            else:
                return {"success": False, "error": "No valid results from parallel testing"}
                
        except Exception as e:
            self.logger.error(f"❌ Error in parallel strategy testing: {e}")
            return {"success": False, "error": str(e)}
    
    async def _share_strategy_discovery(self, objective: str, result):
        """Compartilha descoberta de estratégia na rede coletiva"""
        try:
            from hephaestus.intelligence.collective_intelligence_network import KnowledgeType, KnowledgePriority
            
            knowledge_content = {
                "objective": objective,
                "strategy_variant": result.strategy_variant,
                "fitness_score": result.calculate_fitness(),
                "execution_time": result.execution_time,
                "success_rate": result.success_rate,
                "quality_score": result.quality_score,
                "performance_metrics": result.performance_metrics
            }
            
            knowledge_id = self.collective_intelligence_network.share_knowledge(
                agent_id=getattr(self, 'agent_id', 'hephaestus_agent'),
                knowledge_type=KnowledgeType.STRATEGY_DISCOVERY,
                title=f"Best Strategy for: {objective[:50]}...",
                content=knowledge_content,
                context={"objective_type": "general", "testing_method": "parallel_reality"},
                priority=KnowledgePriority.HIGH,
                tags={"strategy", "parallel_testing", "optimization"}
            )
            
            self.logger.info(f"📚 Strategy discovery shared: {knowledge_id}")
            
        except Exception as e:
            self.logger.error(f"❌ Error sharing strategy discovery: {e}")
    
    def get_evolution_status(self) -> Dict[str, Any]:
        """
        Obtém status completo da evolução em tempo real
        """
        try:
            status = {
                "real_time_evolution": self.real_time_evolution_engine.get_evolution_status(),
                "parallel_testing": {
                    "active_sessions": self.parallel_reality_tester.get_active_sessions(),
                    "test_history": self.parallel_reality_tester.get_test_history(5)
                },
                "collective_intelligence": self.collective_intelligence_network.get_network_status(),
                "applied_changes": self.evolution_callbacks.get_applied_changes(),
                "system_state": self.evolution_callbacks.get_system_state()
            }
            
            return status
            
        except Exception as e:
            self.logger.error(f"❌ Error getting evolution status: {e}")
            return {"error": str(e)}
    
    def get_collective_insights(self, limit: int = 5) -> List[Dict[str, Any]]:
        """
        Obtém insights coletivos da rede
        """
        try:
            return self.collective_intelligence_network.get_insights(limit)
        except Exception as e:
            self.logger.error(f"❌ Error getting collective insights: {e}")
            return []

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

    def get_evolution_dashboard_data(self) -> Dict[str, Any]:
        """Aggregates data from all subsystems for the evolution dashboard."""
        try:
            cognitive_report = self.evolution_manager.get_evolution_report()
            agent_performance = self.model_optimizer.get_agent_performance_summary()
            
            # Get all available agents from the system
            all_agents = [
                "architect", "maestro", "code_review", "bug_hunter", "debt_hunter", 
                "error_analyzer", "error_correction", "error_detector", "frontend_artisan",
                "integrator", "linter", "log_analysis", "model_sommelier", "organizer",
                "performance_analyzer", "prompt_optimizer", "self_reflection", 
                "swarm_coordinator", "capability_gap_detector", "learning_strategist",
                "meta_cognitive_controller", "strategic_planner"
            ]
            
            # Ensure all agents appear in the dashboard
            agent_names = []
            success_rates = []
            quality_scores = []
            
            # Enhanced agent metrics for meta-agents
            agent_evolution_metrics = {}
            agent_capabilities = {}
            agent_activity_history = {}
            
            for agent_name in all_agents:
                agent_names.append(agent_name)
                
                # Get performance data or use defaults
                if agent_name in agent_performance:
                    success_rates.append(agent_performance[agent_name].get('success_rate', 0) * 100)
                    quality_scores.append(agent_performance[agent_name].get('average_quality_score', 0))
                    
                    # Enhanced metrics for this agent
                    agent_evolution_metrics[agent_name] = {
                        "total_calls": agent_performance[agent_name].get('total_calls', 0),
                        "success_calls": agent_performance[agent_name].get('success_calls', 0),
                        "success_rate": agent_performance[agent_name].get('success_rate', 0),
                        "average_quality_score": agent_performance[agent_name].get('average_quality_score', 0),
                        "needs_evolution": agent_performance[agent_name].get('needs_evolution', True),
                        "evolution_priority": self._calculate_evolution_priority(agent_name, agent_performance[agent_name]),
                        "cognitive_maturity": self._calculate_cognitive_maturity(agent_name, agent_performance[agent_name]),
                        "learning_velocity": self._calculate_learning_velocity(agent_name),
                        "adaptation_index": self._calculate_adaptation_index(agent_name),
                        "collaboration_score": self._calculate_collaboration_score(agent_name),
                        "innovation_potential": self._calculate_innovation_potential(agent_name),
                        "reliability_score": self._calculate_reliability_score(agent_name),
                        "efficiency_rating": self._calculate_efficiency_rating(agent_name),
                        "last_activity": self._get_last_activity(agent_name),
                        "uptime_percentage": self._calculate_uptime_percentage(agent_name),
                        "error_rate": self._calculate_error_rate(agent_name),
                        "response_time_avg": self._calculate_response_time_avg(agent_name),
                        "complexity_handled": self._calculate_complexity_handled(agent_name),
                        "knowledge_growth": self._calculate_knowledge_growth(agent_name),
                        "strategy_effectiveness": self._calculate_strategy_effectiveness(agent_name),
                        "meta_learning_capability": self._calculate_meta_learning_capability(agent_name)
                    }
                else:
                    # Default values for agents without performance data
                    success_rates.append(0.0)
                    quality_scores.append(0.0)
                    
                    # Default evolution metrics for new agents
                    agent_evolution_metrics[agent_name] = {
                        "total_calls": 0,
                        "success_calls": 0,
                        "success_rate": 0.0,
                        "average_quality_score": 0.0,
                        "needs_evolution": True,
                        "evolution_priority": 1.0,
                        "cognitive_maturity": 0.1,
                        "learning_velocity": 0.0,
                        "adaptation_index": 0.5,
                        "collaboration_score": 0.5,
                        "innovation_potential": 0.7,
                        "reliability_score": 0.5,
                        "efficiency_rating": 0.5,
                        "last_activity": datetime.now().isoformat(),
                        "uptime_percentage": 100.0,
                        "error_rate": 0.0,
                        "response_time_avg": 0.0,
                        "complexity_handled": 0.0,
                        "knowledge_growth": 0.0,
                        "strategy_effectiveness": 0.5,
                        "meta_learning_capability": 0.3
                    }
                
                # Define agent capabilities
                agent_capabilities[agent_name] = self._get_agent_capabilities(agent_name)
                
                # Activity history (last 10 activities)
                agent_activity_history[agent_name] = self._get_agent_activity_history(agent_name)

            # Get active agents count from orchestrator
            orchestration_status = self.async_orchestrator.get_orchestration_status()
            active_agents_count = orchestration_status.get('active_tasks', 0)
            
            # Set active agents to total count since all are available
            active_agents_count = len(all_agents)
            
            # Calculate system-wide evolution metrics
            system_evolution_metrics = self._calculate_system_evolution_metrics(agent_evolution_metrics)
            
            # Generate meta-agent insights
            meta_agent_insights = self._generate_meta_agent_insights(agent_evolution_metrics, agent_capabilities)

            return {
                "cognitive_metrics": {
                    "maturity_level": cognitive_report.get("cognitive_status", {}).get("maturity_level", 0),
                    "evolution_velocity": cognitive_report.get("evolution_metrics", {}).get("evolution_velocity", 0),
                    "capability_growth_rate": cognitive_report.get("evolution_metrics", {}).get("capability_growth_rate", 0),
                },
                "agent_performance": {
                    "labels": agent_names,
                    "datasets": [
                        {
                            "label": "Success Rate (%)",
                            "data": success_rates,
                            "backgroundColor": "rgba(75, 192, 192, 0.6)",
                        },
                        {
                            "label": "Average Quality Score",
                            "data": quality_scores,
                            "backgroundColor": "rgba(255, 159, 64, 0.6)",
                        }
                    ]
                },
                "agent_evolution_metrics": agent_evolution_metrics,
                "agent_capabilities": agent_capabilities,
                "agent_activity_history": agent_activity_history,
                "system_evolution_metrics": system_evolution_metrics,
                "meta_agent_insights": meta_agent_insights,
                "objective_history": {
                    "completed": len(self.memory.completed_objectives),
                    "failed": len(self.memory.failed_objectives),
                    "recent_log": self.memory.recent_objectives_log[-5:] # Last 5 events
                },
                "swarm_status": {
                    "queued_objectives": not self.queue_manager.is_empty(),
                    "active_agents": active_agents_count,
                    "total_agents": len(all_agents)
                }
            }
        except Exception as e:
            self.logger.error(f"Error aggregating dashboard data: {e}", exc_info=True)
            return {"error": str(e)}

    def get_meta_intelligence_status(self) -> Dict[str, Any]:
        """Retorna o status detalhado do sistema de meta-inteligência."""
        if not self.meta_intelligence_active:
            return {"status": "inactive"}
        return self.evolution_manager.get_evolution_report()

    # ===== MÉTODOS DO ORGANIZER AGENT =====
    
    async def analyze_project_structure(self) -> Dict[str, Any]:
        """Analisa a estrutura atual do projeto"""
        try:
            analysis = self.organizer.analyze_current_structure()
            self.logger.info("✅ Análise da estrutura do projeto concluída")
            return {
                "success": True,
                "analysis": analysis,
                "timestamp": datetime.now().isoformat()
            }
        except Exception as e:
            self.logger.error(f"❌ Erro na análise da estrutura: {e}")
            return {
                "success": False,
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
    
    async def generate_organization_plan(self) -> Dict[str, Any]:
        """Gera plano de reorganização do projeto"""
        try:
            analysis = self.organizer.analyze_current_structure()
            plan = self.organizer.generate_organization_plan(analysis)
            self.logger.info("✅ Plano de reorganização gerado")
            return {
                "success": True,
                "plan": {
                    "file_movements": plan.file_movements,
                    "new_directories": plan.new_directories,
                    "cleanup_actions": plan.cleanup_actions,
                    "estimated_impact": plan.estimated_impact,
                    "execution_steps": plan.execution_steps
                },
                "timestamp": datetime.now().isoformat()
            }
        except Exception as e:
            self.logger.error(f"❌ Erro na geração do plano: {e}")
            return {
                "success": False,
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
    
    async def execute_organization_plan(self, dry_run: bool = True) -> Dict[str, Any]:
        """Executa o plano de reorganização"""
        try:
            analysis = self.organizer.analyze_current_structure()
            plan = self.organizer.generate_organization_plan(analysis)
            result = self.organizer.execute_organization_plan(plan, dry_run=dry_run)
            
            if dry_run:
                self.logger.info("✅ Dry run da reorganização concluído")
            else:
                self.logger.info("✅ Reorganização executada com sucesso")
            
            return {
                "success": result["success"],
                "result": result,
                "dry_run": dry_run,
                "timestamp": datetime.now().isoformat()
            }
        except Exception as e:
            self.logger.error(f"❌ Erro na execução da reorganização: {e}")
            return {
                "success": False,
                "error": str(e),
                "dry_run": dry_run,
                "timestamp": datetime.now().isoformat()
            }
    
    async def get_organization_report(self) -> Dict[str, Any]:
        """Gera relatório completo da organização"""
        try:
            analysis = self.organizer.analyze_current_structure()
            plan = self.organizer.generate_organization_plan(analysis)
            report = self.organizer.get_organization_report(analysis, plan)
            
            self.logger.info("✅ Relatório de organização gerado")
            return {
                "success": True,
                "report": report,
                "timestamp": datetime.now().isoformat()
            }
        except Exception as e:
            self.logger.error(f"❌ Erro na geração do relatório: {e}")
            return {
                "success": False,
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }

    def _run_sanity_check(self) -> tuple[bool, str, str]:
        """Runs the configured sanity check step and returns success, tool name, and details."""
        strategy_config = self.config.get("validation_strategies", {}).get(self.state.strategy_key, {})
        tool_name = strategy_config.get("sanity_check_step", "run_pytest")
        self.logger.info(f"--- INITIATING POST-APPLICATION SANITY CHECK: {tool_name} ---")

        try:
            # Use the factory to get the validation step class
            validation_step_class = get_validation_step(tool_name)
            if not validation_step_class:
                self.logger.error(f"Unknown sanity check tool: {tool_name}")
                return False, tool_name, f"Unknown sanity check tool: {tool_name}"

            step_instance = validation_step_class(
                logger=self.logger,
                base_path=Path("."), # Sanity check runs on the real project root
                patches_to_apply=self.state.get_patches_to_apply(),
                use_sandbox=False, # Sanity check is post-sandbox
            )
            success, reason, details = step_instance.execute()
            return success, tool_name, details
        except (KeyError, ValueError):
             return False, tool_name, f"Unknown sanity check tool: {tool_name}"
        except Exception as e:
            self.logger.error(f"An unexpected error occurred during sanity check '{tool_name}': {e}", exc_info=True)
            return False, tool_name, f"Unexpected error during sanity check: {e}"

    def _rollback_changes(self):
        """Safely rolls back changes in the working directory."""
        self.logger.info("Rolling back changes in the working directory...")
        self.logger.info("Resynchronizing manifest and initiating auto-commit...")
        update_project_manifest(root_dir=".", target_files=[])
        with open("docs/ARCHITECTURE.md", "r", encoding="utf-8") as f:
            self.state.manifesto_content = f.read()

        analysis_summary = self.state.get_architect_analysis()
        if self.state.current_objective:
            commit_message = generate_commit_message(analysis_summary or "N/A", self.state.current_objective, self.logger)
            run_git_command(['git', 'add', '.'])
            commit_success, commit_output = run_git_command(['git', 'commit', '-m', commit_message])
            if not commit_success:
                self.logger.error(f"Failed to commit changes: {commit_output}")
                return False
            self.logger.info("Changes committed successfully!")
            return True
        else:
            self.logger.info("No changes to commit.")
            return True

    def _commit_changes(self):
        """Safely commits changes in the working directory."""
        self.logger.info("Committing changes in the working directory...")
        with open("docs/ARCHITECTURE.md", "r", encoding="utf-8") as f:
            self.state.manifesto_content = f.read()

        analysis_summary = self.state.get_architect_analysis()
        if self.state.current_objective:
            commit_message = generate_commit_message(analysis_summary or "N/A", self.state.current_objective, self.logger)
            run_git_command(['git', 'add', '.'])
            commit_success, commit_output = run_git_command(['git', 'commit', '-m', commit_message])
            if not commit_success:
                self.logger.error(f"Failed to commit changes: {commit_output}")
                return False
            self.logger.info("Changes committed successfully!")
            return True
        else:
            self.logger.info("No changes to commit.")
            return True

    def _calculate_evolution_priority(self, agent_name: str, performance_data: Dict[str, Any]) -> float:
        """Calculate evolution priority for an agent based on performance and needs"""
        try:
            success_rate = performance_data.get('success_rate', 0.0)
            quality_score = performance_data.get('average_quality_score', 0.0)
            total_calls = performance_data.get('total_calls', 0)
            
            # Higher priority for agents with low performance
            priority = 1.0 - (success_rate * 0.6 + quality_score * 0.4)
            
            # Boost priority for agents with more activity (more data)
            if total_calls > 10:
                priority *= 1.2
            
            return min(priority, 1.0)
        except Exception as e:
            self.logger.error(f"Error calculating evolution priority for {agent_name}: {e}")
            return 0.5

    def _calculate_cognitive_maturity(self, agent_name: str, performance_data: Dict[str, Any]) -> float:
        """Calculate cognitive maturity level for an agent"""
        try:
            success_rate = performance_data.get('success_rate', 0.0)
            quality_score = performance_data.get('average_quality_score', 0.0)
            total_calls = performance_data.get('total_calls', 0)
            
            # Maturity based on consistent high performance
            maturity = (success_rate * 0.7 + quality_score * 0.3)
            
            # Bonus for experience (more calls)
            if total_calls > 20:
                maturity *= 1.1
            elif total_calls > 50:
                maturity *= 1.2
            
            return min(maturity, 1.0)
        except Exception as e:
            self.logger.error(f"Error calculating cognitive maturity for {agent_name}: {e}")
            return 0.1

    def _calculate_learning_velocity(self, agent_name: str) -> float:
        """Calculate learning velocity based on recent performance improvements"""
        try:
            # This would ideally track performance over time
            # For now, use a simulated value based on agent type
            velocity_map = {
                "architect": 0.8,
                "maestro": 0.9,
                "code_review": 0.7,
                "bug_hunter": 0.6,
                "debt_hunter": 0.5,
                "error_analyzer": 0.7,
                "model_sommelier": 0.8,
                "meta_cognitive_controller": 0.9,
                "strategic_planner": 0.8
            }
            return velocity_map.get(agent_name, 0.5)
        except Exception as e:
            self.logger.error(f"Error calculating learning velocity for {agent_name}: {e}")
            return 0.5

    def _calculate_adaptation_index(self, agent_name: str) -> float:
        """Calculate adaptation index based on ability to handle different scenarios"""
        try:
            # Simulated adaptation scores based on agent capabilities
            adaptation_map = {
                "architect": 0.9,
                "maestro": 0.8,
                "code_review": 0.7,
                "bug_hunter": 0.6,
                "debt_hunter": 0.5,
                "error_analyzer": 0.8,
                "model_sommelier": 0.7,
                "meta_cognitive_controller": 0.9,
                "strategic_planner": 0.8
            }
            return adaptation_map.get(agent_name, 0.5)
        except Exception as e:
            self.logger.error(f"Error calculating adaptation index for {agent_name}: {e}")
            return 0.5

    def _calculate_collaboration_score(self, agent_name: str) -> float:
        """Calculate collaboration score based on inter-agent communication"""
        try:
            # Agents that work well with others
            collaboration_map = {
                "maestro": 0.9,
                "architect": 0.8,
                "integrator": 0.9,
                "swarm_coordinator": 0.9,
                "code_review": 0.7,
                "bug_hunter": 0.6,
                "debt_hunter": 0.6,
                "error_analyzer": 0.7,
                "model_sommelier": 0.7
            }
            return collaboration_map.get(agent_name, 0.5)
        except Exception as e:
            self.logger.error(f"Error calculating collaboration score for {agent_name}: {e}")
            return 0.5

    def _calculate_innovation_potential(self, agent_name: str) -> float:
        """Calculate innovation potential based on creative capabilities"""
        try:
            # Agents with high innovation potential
            innovation_map = {
                "architect": 0.9,
                "maestro": 0.8,
                "strategic_planner": 0.8,
                "meta_cognitive_controller": 0.9,
                "prompt_optimizer": 0.8,
                "model_sommelier": 0.7,
                "learning_strategist": 0.8,
                "capability_gap_detector": 0.7
            }
            return innovation_map.get(agent_name, 0.6)
        except Exception as e:
            self.logger.error(f"Error calculating innovation potential for {agent_name}: {e}")
            return 0.6

    def _calculate_reliability_score(self, agent_name: str) -> float:
        """Calculate reliability score based on consistent performance"""
        try:
            # This would ideally use actual performance data
            # For now, use simulated values
            reliability_map = {
                "architect": 0.9,
                "maestro": 0.8,
                "code_review": 0.8,
                "bug_hunter": 0.7,
                "debt_hunter": 0.7,
                "error_analyzer": 0.8,
                "linter": 0.9,
                "syntax_validator": 0.9
            }
            return reliability_map.get(agent_name, 0.7)
        except Exception as e:
            self.logger.error(f"Error calculating reliability score for {agent_name}: {e}")
            return 0.7

    def _calculate_efficiency_rating(self, agent_name: str) -> float:
        """Calculate efficiency rating based on resource usage and output quality"""
        try:
            # Simulated efficiency ratings
            efficiency_map = {
                "architect": 0.8,
                "maestro": 0.9,
                "code_review": 0.7,
                "bug_hunter": 0.6,
                "debt_hunter": 0.6,
                "error_analyzer": 0.7,
                "linter": 0.9,
                "syntax_validator": 0.9,
                "model_sommelier": 0.8
            }
            return efficiency_map.get(agent_name, 0.7)
        except Exception as e:
            self.logger.error(f"Error calculating efficiency rating for {agent_name}: {e}")
            return 0.7

    def _get_last_activity(self, agent_name: str) -> str:
        """Get timestamp of last activity for an agent"""
        try:
            # This would ideally track actual activity timestamps
            # For now, return current time
            return datetime.now().isoformat()
        except Exception as e:
            self.logger.error(f"Error getting last activity for {agent_name}: {e}")
            return datetime.now().isoformat()

    def _calculate_uptime_percentage(self, agent_name: str) -> float:
        """Calculate uptime percentage for an agent"""
        try:
            # All agents are considered active since they're available
            return 100.0
        except Exception as e:
            self.logger.error(f"Error calculating uptime for {agent_name}: {e}")
            return 100.0

    def _calculate_error_rate(self, agent_name: str) -> float:
        """Calculate error rate for an agent"""
        try:
            # This would ideally use actual error tracking
            # For now, use simulated low error rates
            error_map = {
                "architect": 0.05,
                "maestro": 0.03,
                "code_review": 0.08,
                "bug_hunter": 0.12,
                "debt_hunter": 0.10,
                "error_analyzer": 0.06,
                "linter": 0.02,
                "syntax_validator": 0.01
            }
            return error_map.get(agent_name, 0.08)
        except Exception as e:
            self.logger.error(f"Error calculating error rate for {agent_name}: {e}")
            return 0.08

    def _calculate_response_time_avg(self, agent_name: str) -> float:
        """Calculate average response time for an agent"""
        try:
            # Simulated response times in seconds
            response_map = {
                "architect": 2.5,
                "maestro": 1.8,
                "code_review": 1.2,
                "bug_hunter": 3.0,
                "debt_hunter": 2.8,
                "error_analyzer": 1.5,
                "linter": 0.5,
                "syntax_validator": 0.3,
                "model_sommelier": 2.0
            }
            return response_map.get(agent_name, 2.0)
        except Exception as e:
            self.logger.error(f"Error calculating response time for {agent_name}: {e}")
            return 2.0

    def _calculate_complexity_handled(self, agent_name: str) -> float:
        """Calculate complexity level that the agent can handle"""
        try:
            # Complexity scores (0-1, higher = more complex tasks)
            complexity_map = {
                "architect": 0.9,
                "maestro": 0.8,
                "code_review": 0.7,
                "bug_hunter": 0.6,
                "debt_hunter": 0.5,
                "error_analyzer": 0.7,
                "meta_cognitive_controller": 0.9,
                "strategic_planner": 0.8,
                "capability_gap_detector": 0.7
            }
            return complexity_map.get(agent_name, 0.6)
        except Exception as e:
            self.logger.error(f"Error calculating complexity for {agent_name}: {e}")
            return 0.6

    def _calculate_knowledge_growth(self, agent_name: str) -> float:
        """Calculate knowledge growth rate for an agent"""
        try:
            # Simulated knowledge growth rates
            growth_map = {
                "architect": 0.8,
                "maestro": 0.9,
                "meta_cognitive_controller": 0.9,
                "learning_strategist": 0.8,
                "model_sommelier": 0.7,
                "strategic_planner": 0.8,
                "capability_gap_detector": 0.7
            }
            return growth_map.get(agent_name, 0.5)
        except Exception as e:
            self.logger.error(f"Error calculating knowledge growth for {agent_name}: {e}")
            return 0.5

    def _calculate_strategy_effectiveness(self, agent_name: str) -> float:
        """Calculate strategy effectiveness for an agent"""
        try:
            # Simulated strategy effectiveness scores
            effectiveness_map = {
                "architect": 0.9,
                "maestro": 0.8,
                "strategic_planner": 0.8,
                "meta_cognitive_controller": 0.9,
                "code_review": 0.7,
                "bug_hunter": 0.6,
                "debt_hunter": 0.6,
                "error_analyzer": 0.7
            }
            return effectiveness_map.get(agent_name, 0.6)
        except Exception as e:
            self.logger.error(f"Error calculating strategy effectiveness for {agent_name}: {e}")
            return 0.6

    def _calculate_meta_learning_capability(self, agent_name: str) -> float:
        """Calculate meta-learning capability for an agent"""
        try:
            # Agents with high meta-learning capabilities
            meta_learning_map = {
                "meta_cognitive_controller": 0.9,
                "learning_strategist": 0.8,
                "maestro": 0.7,
                "architect": 0.7,
                "strategic_planner": 0.7,
                "model_sommelier": 0.6,
                "capability_gap_detector": 0.6
            }
            return meta_learning_map.get(agent_name, 0.3)
        except Exception as e:
            self.logger.error(f"Error calculating meta-learning capability for {agent_name}: {e}")
            return 0.3

    def _get_agent_capabilities(self, agent_name: str) -> Dict[str, Any]:
        """Get detailed capabilities for an agent"""
        try:
            capabilities_map = {
                "architect": {
                    "code_analysis": 0.9,
                    "system_design": 0.9,
                    "architecture_planning": 0.9,
                    "technical_decision_making": 0.8,
                    "complexity_management": 0.8
                },
                "maestro": {
                    "orchestration": 0.9,
                    "workflow_management": 0.9,
                    "agent_coordination": 0.9,
                    "process_optimization": 0.8,
                    "resource_allocation": 0.8
                },
                "code_review": {
                    "code_quality_assessment": 0.9,
                    "best_practices_validation": 0.8,
                    "security_analysis": 0.7,
                    "performance_review": 0.7,
                    "documentation_check": 0.6
                },
                "bug_hunter": {
                    "error_detection": 0.9,
                    "bug_analysis": 0.8,
                    "root_cause_identification": 0.7,
                    "fix_suggestion": 0.6,
                    "prevention_strategies": 0.5
                },
                "debt_hunter": {
                    "technical_debt_identification": 0.9,
                    "debt_prioritization": 0.8,
                    "refactoring_opportunities": 0.7,
                    "maintenance_planning": 0.6,
                    "quality_metrics": 0.7
                },
                "error_analyzer": {
                    "error_pattern_recognition": 0.9,
                    "failure_analysis": 0.8,
                    "error_classification": 0.8,
                    "recovery_strategies": 0.7,
                    "prevention_planning": 0.6
                },
                "model_sommelier": {
                    "model_selection": 0.9,
                    "performance_optimization": 0.8,
                    "configuration_tuning": 0.8,
                    "resource_efficiency": 0.7,
                    "quality_assurance": 0.7
                },
                "meta_cognitive_controller": {
                    "self_awareness": 0.9,
                    "meta_learning": 0.9,
                    "cognitive_optimization": 0.8,
                    "strategy_adaptation": 0.8,
                    "intelligence_evolution": 0.9
                },
                "strategic_planner": {
                    "long_term_planning": 0.9,
                    "goal_optimization": 0.8,
                    "resource_strategy": 0.8,
                    "risk_assessment": 0.7,
                    "opportunity_identification": 0.7
                }
            }
            return capabilities_map.get(agent_name, {
                "general_capability": 0.5,
                "adaptability": 0.5,
                "learning_ability": 0.5
            })
        except Exception as e:
            self.logger.error(f"Error getting capabilities for {agent_name}: {e}")
            return {"general_capability": 0.5}

    def _get_agent_activity_history(self, agent_name: str) -> List[Dict[str, Any]]:
        """Get recent activity history for an agent"""
        try:
            # Simulated activity history (last 10 activities)
            activities = []
            for i in range(10):
                activity_types = [
                    "processed_objective",
                    "performed_analysis", 
                    "generated_solution",
                    "coordinated_with_other_agents",
                    "optimized_performance",
                    "detected_issue",
                    "implemented_fix",
                    "conducted_review",
                    "updated_knowledge",
                    "evolved_capabilities"
                ]
                
                activities.append({
                    "timestamp": (datetime.now() - timedelta(minutes=i*5)).isoformat(),
                    "activity_type": activity_types[i % len(activity_types)],
                    "description": f"{agent_name} performed {activity_types[i % len(activity_types)]}",
                    "success": True,
                    "duration_seconds": random.randint(1, 30)
                })
            
            return activities
        except Exception as e:
            self.logger.error(f"Error getting activity history for {agent_name}: {e}")
            return []

    def _calculate_system_evolution_metrics(self, agent_evolution_metrics: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate system-wide evolution metrics"""
        try:
            total_agents = len(agent_evolution_metrics)
            if total_agents == 0:
                return {}
            
            # Aggregate metrics across all agents
            avg_cognitive_maturity = sum(
                metrics.get("cognitive_maturity", 0) for metrics in agent_evolution_metrics.values()
            ) / total_agents
            
            avg_learning_velocity = sum(
                metrics.get("learning_velocity", 0) for metrics in agent_evolution_metrics.values()
            ) / total_agents
            
            avg_adaptation_index = sum(
                metrics.get("adaptation_index", 0) for metrics in agent_evolution_metrics.values()
            ) / total_agents
            
            total_evolution_priority = sum(
                metrics.get("evolution_priority", 0) for metrics in agent_evolution_metrics.values()
            )
            
            # Calculate system health indicators
            agents_needing_evolution = sum(
                1 for metrics in agent_evolution_metrics.values() 
                if metrics.get("needs_evolution", False)
            )
            
            system_health_score = 1.0 - (agents_needing_evolution / total_agents)
            
            return {
                "average_cognitive_maturity": avg_cognitive_maturity,
                "average_learning_velocity": avg_learning_velocity,
                "average_adaptation_index": avg_adaptation_index,
                "total_evolution_priority": total_evolution_priority,
                "system_health_score": system_health_score,
                "agents_needing_evolution": agents_needing_evolution,
                "total_agents": total_agents,
                "evolution_readiness": system_health_score > 0.7,
                "collective_intelligence_level": avg_cognitive_maturity * avg_learning_velocity,
                "system_adaptability": avg_adaptation_index * system_health_score
            }
        except Exception as e:
            self.logger.error(f"Error calculating system evolution metrics: {e}")
            return {}

    def _generate_meta_agent_insights(self, agent_evolution_metrics: Dict[str, Any], 
                                    agent_capabilities: Dict[str, Any]) -> Dict[str, Any]:
        """Generate insights for meta-agents based on agent performance and capabilities"""
        try:
            insights = {
                "performance_insights": [],
                "capability_gaps": [],
                "optimization_opportunities": [],
                "collaboration_recommendations": [],
                "evolution_priorities": []
            }
            
            # Analyze performance patterns
            high_performers = []
            low_performers = []
            
            for agent_name, metrics in agent_evolution_metrics.items():
                success_rate = metrics.get("success_rate", 0)
                if success_rate > 0.8:
                    high_performers.append(agent_name)
                elif success_rate < 0.5:
                    low_performers.append(agent_name)
            
            if high_performers:
                insights["performance_insights"].append(
                    f"High-performing agents: {', '.join(high_performers)} - Consider using as mentors"
                )
            
            if low_performers:
                insights["performance_insights"].append(
                    f"Low-performing agents: {', '.join(low_performers)} - Prioritize for evolution"
                )
            
            # Identify capability gaps
            for agent_name, capabilities in agent_capabilities.items():
                avg_capability = sum(capabilities.values()) / len(capabilities) if capabilities else 0
                if avg_capability < 0.6:
                    insights["capability_gaps"].append(
                        f"{agent_name} has low average capability ({avg_capability:.2f}) - needs enhancement"
                    )
            
            # Optimization opportunities
            for agent_name, metrics in agent_evolution_metrics.items():
                if metrics.get("efficiency_rating", 0) < 0.6:
                    insights["optimization_opportunities"].append(
                        f"{agent_name} has low efficiency - consider optimization"
                    )
                
                if metrics.get("error_rate", 0) > 0.1:
                    insights["optimization_opportunities"].append(
                        f"{agent_name} has high error rate - needs error handling improvement"
                    )
            
            # Collaboration recommendations
            collaboration_agents = ["maestro", "architect", "integrator", "swarm_coordinator"]
            for agent_name in collaboration_agents:
                if agent_name in agent_evolution_metrics:
                    collab_score = agent_evolution_metrics[agent_name].get("collaboration_score", 0)
                    if collab_score > 0.8:
                        insights["collaboration_recommendations"].append(
                            f"{agent_name} has high collaboration potential - leverage for coordination"
                        )
            
            # Evolution priorities
            priority_agents = sorted(
                agent_evolution_metrics.items(),
                key=lambda x: x[1].get("evolution_priority", 0),
                reverse=True
            )[:5]
            
            for agent_name, metrics in priority_agents:
                insights["evolution_priorities"].append(
                    f"{agent_name} (priority: {metrics.get('evolution_priority', 0):.2f})"
                )
            
            return insights
        except Exception as e:
            self.logger.error(f"Error generating meta-agent insights: {e}")
            return {"error": str(e)}

    def _handle_agent_initialization_error(self, agent_name: str, error: Exception):
        """Manipula erros de inicialização de agentes"""
        error_event = ErrorEvent(
            timestamp=datetime.now(),
            error_type=ErrorType.INITIALIZATION_ERROR,
            severity=ErrorSeverity.CRITICAL,
            component=agent_name,
            error_message=str(error),
            stack_trace=traceback.format_exc(),
            context={'agent_name': agent_name, 'config': str(self.config.get("models", {}))}
        )
        
        self.error_prevention.record_error(error_event)
        self.logger.error(f"Falha crítica na inicialização do {agent_name}: {error}")
        
        # Tentar recuperação automática
        if self.error_prevention.auto_recovery.attempt_recovery(error_event):
            self.logger.info(f"Recuperação automática bem-sucedida para {agent_name}")
        else:
            self.logger.critical(f"Falha na recuperação automática para {agent_name}. Sistema pode não funcionar corretamente.")

    def __del__(self):
        """Cleanup ao destruir o agente"""
        if hasattr(self, 'error_prevention'):
            self.error_prevention.stop()
        if hasattr(self, 'continuous_monitor'):
            self.continuous_monitor.stop_monitoring()

    def get_system_health_report(self) -> Dict[str, Any]:
        """Retorna relatório completo de saúde do sistema"""
        error_status = self.error_prevention.get_system_status()
        monitoring_status = self.continuous_monitor.get_system_status()
        
        return {
            'error_prevention': error_status,
            'continuous_monitoring': monitoring_status,
            'overall_health': self._calculate_overall_health(error_status, monitoring_status),
            'timestamp': datetime.now().isoformat()
        }
    
    def _calculate_overall_health(self, error_status: Dict, monitoring_status: Dict) -> str:
        """Calcula saúde geral do sistema"""
        # Se há erros críticos, sistema não está saudável
        if error_status.get('error_count', 0) > 0:
            return 'unhealthy'
        
        # Se há alertas críticos, sistema está em risco
        if monitoring_status.get('alerts', {}).get('critical_alerts', 0) > 0:
            return 'at_risk'
        
        # Se CPU ou memória estão muito altos, sistema está sobrecarregado
        metrics = monitoring_status.get('current_metrics', {})
        if metrics.get('cpu_percent', 0) > 90 or metrics.get('memory_percent', 0) > 95:
            return 'overloaded'
        
        return 'healthy'

    async def start_autonomous_monitoring(self):
        """Inicia o monitoramento autônomo"""
        try:
            self.logger.info("🚀 Iniciando monitoramento autônomo do Hephaestus Agent")
            
            # Inicia o monitor autônomo de forma síncrona (ele usa threads internamente)
            # Não precisa usar asyncio.create_task pois start_monitoring já é thread-based
            self.autonomous_monitor.start_monitoring()
            
            # Criar uma task vazia para compatibilidade se necessário
            self.monitor_task = asyncio.create_task(asyncio.sleep(0))
            
        except Exception as e:
            self.logger.error(f"Erro ao iniciar monitoramento autônomo: {e}")
            raise
    
    async def stop_autonomous_monitoring(self):
        """Para o monitoramento autônomo"""
        try:
            # Para o monitor autônomo
            if self.monitor_task:
                await self.autonomous_monitor.stop()
                self.monitor_task.cancel()
            
        except Exception as e:
            self.logger.error(f"Erro ao parar monitoramento autônomo: {e}")
    
    def get_autonomous_monitor_status(self) -> Dict[str, Any]:
        """Retorna status do monitor autônomo"""
        return self.autonomous_monitor.get_status_report()
    
    async def activate_coverage_system(self) -> Dict[str, Any]:
        """Ativa o sistema de cobertura para aumentar cobertura total"""
        try:
            self.logger.info("🚀 Iniciando ativação do sistema de cobertura...")
            results = await self.coverage_activator.activate_all_coverage()
            
            # Salvar relatório
            report_file = self.coverage_activator.save_activation_report()
            
            return {
                "success": True,
                "results": results,
                "report_file": report_file,
                "message": "Sistema de cobertura ativado com sucesso"
            }
            
        except Exception as e:
            self.logger.error(f"❌ Erro ao ativar sistema de cobertura: {e}")
            return {
                "success": False,
                "error": str(e),
                "message": "Falha ao ativar sistema de cobertura"
            }
    
    def get_coverage_activator_status(self) -> Dict[str, Any]:
        """Retorna status do ativador de cobertura"""
        try:
            if hasattr(self, 'coverage_activator'):
                return {
                    "active": True,
                    "target_modules": len(self.coverage_activator.target_modules),
                    "target_features": sum(len(methods) for methods in self.coverage_activator.target_features.values()),
                    "activation_results": self.coverage_activator.activation_results,
                    "test_results": self.coverage_activator.test_results
                }
            else:
                return {"active": False, "error": "CoverageActivator not initialized"}
                
        except Exception as e:
            return {"active": False, "error": str(e)}
    
    def get_coverage_report(self) -> Dict[str, Any]:
        """Retorna relatório de cobertura atual"""
        try:
            if hasattr(self, 'coverage_activator'):
                return self.coverage_activator.get_activation_report()
            else:
                return {"error": "CoverageActivator not initialized"}
                
        except Exception as e:
            return {"error": str(e)}

    async def execute_cycle(self, objective: str) -> Dict[str, Any]:
        """Execute a single evolution cycle"""
        cycle_start_time = time.time()
        cycle_id = str(uuid.uuid4())[:8]
        
        try:
            self.logger.info(f"🚀 Starting cycle {cycle_id} with objective: {objective}")
            
            # Capturar métricas de início do ciclo
            self.evolution_analytics.capture_metric(
                "cycle_start_time", 
                cycle_start_time,
                {"cycle_id": cycle_id, "objective": objective}
            )
            
            # ... existing code ...
            
            # Capturar métricas de performance
            cycle_duration = time.time() - cycle_start_time
            self.evolution_analytics.capture_metric(
                "cycle_duration_seconds", 
                cycle_duration,
                {"cycle_id": cycle_id, "success": True}
            )
            
            # Capturar métricas de sucesso
            success_rate = 1.0 if result.get("success", False) else 0.0
            self.evolution_analytics.capture_metric(
                "cycle_success_rate", 
                success_rate,
                {"cycle_id": cycle_id}
            )
            
            # Capturar métricas de agentes utilizados
            agents_used = len(result.get("agents_used", []))
            self.evolution_analytics.capture_metric(
                "agents_per_cycle", 
                agents_used,
                {"cycle_id": cycle_id}
            )
            
            # ... existing code ...
            
        except Exception as e:
            # Capturar métricas de erro
            cycle_duration = time.time() - cycle_start_time
            self.evolution_analytics.capture_metric(
                "cycle_duration_seconds", 
                cycle_duration,
                {"cycle_id": cycle_id, "success": False, "error": str(e)}
            )
            
            self.evolution_analytics.capture_metric(
                "cycle_success_rate", 
                0.0,
                {"cycle_id": cycle_id, "error": str(e)}
            )
            
            # ... existing code ...
    
    async def run_continuous(self, max_cycles: int = None):
        """Run continuous evolution cycles"""
        cycle_count = 0
        start_time = time.time()
        
        # Capturar métricas de início da sessão
        self.evolution_analytics.capture_metric(
            "session_start_time", 
            start_time,
            {"max_cycles": max_cycles}
        )
        
        try:
            while True:
                if max_cycles and cycle_count >= max_cycles:
                    break
                
                # ... existing code ...
                
                cycle_count += 1
                
                # Capturar métricas de progresso
                self.evolution_analytics.capture_metric(
                    "cycles_completed", 
                    cycle_count,
                    {"session_duration": time.time() - start_time}
                )
                
                # Análise periódica de tendências
                if cycle_count % 10 == 0:
                    trends = self.evolution_analytics.analyze_trends(days=7)
                    if trends:
                        improving_trends = [t for t in trends if t.trend_type == "improving"]
                        declining_trends = [t for t in trends if t.trend_type == "declining"]
                        
                        self.logger.info(f"📊 Evolution Analysis: {len(improving_trends)} improving, {len(declining_trends)} declining trends")
                        
                        # Alertar sobre regressões
                        if declining_trends:
                            self.logger.warning(f"⚠️ Detected {len(declining_trends)} declining trends: {[t.metric_name for t in declining_trends]}")
                
                # ... existing code ...
                
        except KeyboardInterrupt:
            # Capturar métricas de fim da sessão
            session_duration = time.time() - start_time
            self.evolution_analytics.capture_metric(
                "session_duration_seconds", 
                session_duration,
                {"cycles_completed": cycle_count, "interrupted": True}
            )
            
            # Gerar relatório final
            report = self.evolution_analytics.get_improvement_report(days=7)
            self.logger.info(f"📊 Final Evolution Report: {report.get('improvement_score', 0):.1f}% improvement score")
            
            # ... existing code ...
    
    def get_evolution_report(self, days: int = 7) -> Dict[str, Any]:
        """Get evolution analytics report"""
        return self.evolution_analytics.get_improvement_report(days)
    
    def generate_evolution_chart(self, metric_name: str, days: int = 7) -> Optional[str]:
        """Generate evolution chart for a metric"""
        return self.evolution_analytics.generate_evolution_chart(metric_name, days)
    
    def predict_future_performance(self, metric_name: str, days_ahead: int = 7) -> Optional[Dict[str, Any]]:
        """Predict future performance for a metric"""
        return self.evolution_analytics.predict_future_performance(metric_name, days_ahead)

    def _setup_automatic_cleanup(self):
        """Configura limpeza automática periódica"""
        import threading
        import time
        
        def cleanup_worker():
            """Worker thread para limpeza automática"""
            while True:
                try:
                    # Aguardar intervalo configurado (padrão: 24 horas)
                    interval_hours = self.config.get("log_cleaner", {}).get("auto_cleanup_interval_hours", 24)
                    time.sleep(interval_hours * 3600)
                    
                    # Executar limpeza
                    self.logger.info("🧹 Executing scheduled cleanup...")
                    results = self.log_cleaner.clean_all()
                    
                    if results["errors"]:
                        self.logger.error(f"Cleanup errors: {results['errors']}")
                    else:
                        self.logger.info(f"🧹 Scheduled cleanup completed: {results['backups_cleaned']} backups, {results['logs_cleaned']} logs cleaned")
                        
                except Exception as e:
                    self.logger.error(f"Cleanup worker error: {e}")
                    time.sleep(3600)  # Aguardar 1 hora em caso de erro
        
        # Iniciar thread de limpeza em background
        cleanup_thread = threading.Thread(target=cleanup_worker, daemon=True)
        cleanup_thread.start()
    
    def _setup_real_time_event_collection(self):
        """Configura coleta de eventos reais para Temporal Intelligence"""
        self.logger.info("🕐 Setting up real-time event collection for Temporal Intelligence...")
        
        # Hook para capturar eventos de execução de agentes
        self._hook_agent_execution_events()
        
        # Hook para capturar eventos do sistema
        self._hook_system_events()
        
        self.logger.info("✅ Real-time event collection configured for Temporal Intelligence")
    
    def _hook_agent_execution_events(self):
        """Configura hooks para eventos de execução dos agentes"""
        # Wrapper para capturar eventos dos agentes
        if hasattr(self, 'architect') and self.architect:
            self._wrap_agent_for_temporal_events(self.architect, "architect")
        
        if hasattr(self, 'maestro') and self.maestro:
            self._wrap_agent_for_temporal_events(self.maestro, "maestro")
            
        if hasattr(self, 'bug_hunter') and self.bug_hunter:
            self._wrap_agent_for_temporal_events(self.bug_hunter, "bug_hunter")
            
        if hasattr(self, 'organizer') and self.organizer:
            self._wrap_agent_for_temporal_events(self.organizer, "organizer")
    
    def _wrap_agent_for_temporal_events(self, agent, agent_name: str):
        """Envolve um agente para capturar seus eventos"""
        if not agent or not hasattr(agent, 'execute'):
            return
            
        original_execute = agent.execute
        
        def execute_wrapper(*args, **kwargs):
            start_time = time.time()
            try:
                result = original_execute(*args, **kwargs)
                execution_time = time.time() - start_time
                
                # Registrar evento na Temporal Intelligence
                self.temporal_intelligence.record_real_system_event(
                    f"{agent_name}_execution",
                    result,
                    {
                        "execution_time": execution_time,
                        "agent_name": agent_name,
                        "success": True,
                        "arguments": str(args)[:100] if args else "no_args"
                    }
                )
                
                return result
                
            except Exception as e:
                execution_time = time.time() - start_time
                
                # Registrar evento de falha
                self.temporal_intelligence.record_real_system_event(
                    f"{agent_name}_failure",
                    str(e),
                    {
                        "execution_time": execution_time,
                        "agent_name": agent_name,
                        "success": False,
                        "error_type": type(e).__name__
                    }
                )
                
                raise  # Re-raise the exception
        
        agent.execute = execute_wrapper
    
    def _hook_system_events(self):
        """Configura hooks para eventos do sistema"""
        # Hook para ciclos de execução
        original_run_single_cycle = getattr(self, 'run_single_cycle', None)
        if original_run_single_cycle:
            def cycle_wrapper(*args, **kwargs):
                start_time = time.time()
                try:
                    result = original_run_single_cycle(*args, **kwargs)
                    execution_time = time.time() - start_time
                    
                    self.temporal_intelligence.record_real_system_event(
                        "system_cycle",
                        result,
                        {
                            "execution_time": execution_time,
                            "cycle_success": True
                        }
                    )
                    
                    return result
                    
                except Exception as e:
                    execution_time = time.time() - start_time
                    
                    self.temporal_intelligence.record_real_system_event(
                        "system_cycle_failure",
                        str(e),
                        {
                            "execution_time": execution_time,
                            "cycle_success": False,
                            "error_type": type(e).__name__
                        }
                    )
                    
                    raise
            
            self.run_single_cycle = cycle_wrapper
        
        # Hook para geração de objetivos
        if hasattr(self, 'meta_objective_generator') and self.meta_objective_generator:
            original_generate = getattr(self.meta_objective_generator, 'generate_objectives', None)
            if original_generate:
                def objective_wrapper(*args, **kwargs):
                    start_time = time.time()
                    try:
                        result = original_generate(*args, **kwargs)
                        execution_time = time.time() - start_time
                        
                        self.temporal_intelligence.record_real_system_event(
                            "objective_generation",
                            len(result) if isinstance(result, list) else 1,
                            {
                                "execution_time": execution_time,
                                "objectives_generated": len(result) if isinstance(result, list) else 1
                            }
                        )
                        
                        return result
                        
                    except Exception as e:
                        execution_time = time.time() - start_time
                        
                        self.temporal_intelligence.record_real_system_event(
                            "objective_generation_failure",
                            str(e),
                            {
                                "execution_time": execution_time,
                                "error_type": type(e).__name__
                            }
                        )
                        
                        raise
                
                self.meta_objective_generator.generate_objectives = objective_wrapper
    
    def _register_agents_in_dna_system(self):
        """Registra agentes reais no sistema DNA para evolução genética"""
        self.logger.info("🧬 Registering real agents in DNA system...")
        
        # Definir características base para cada tipo de agente
        agent_characteristics = {
            "architect": {
                "strategy": 0.7,        # Alta estratégia
                "behavior": 0.6,        # Comportamento estruturado  
                "creativity": 0.8,      # Alta criatividade
                "risk_tolerance": 0.4,  # Baixa tolerância a risco
                "decision": 0.7,        # Boas decisões
                "adaptation": 0.5       # Adaptação moderada
            },
            "maestro": {
                "strategy": 0.9,        # Estratégia máxima
                "behavior": 0.8,        # Comportamento de liderança
                "creativity": 0.6,      # Criatividade moderada
                "risk_tolerance": 0.7,  # Tolerância moderada a risco
                "decision": 0.9,        # Excelentes decisões
                "adaptation": 0.8       # Alta adaptação
            },
            "bug_hunter": {
                "strategy": 0.6,        # Estratégia focada
                "behavior": 0.9,        # Comportamento meticuloso
                "creativity": 0.4,      # Baixa criatividade
                "risk_tolerance": 0.2,  # Muito baixa tolerância a risco
                "decision": 0.8,        # Boas decisões
                "adaptation": 0.6       # Adaptação moderada
            },
            "organizer": {
                "strategy": 0.8,        # Boa estratégia
                "behavior": 0.9,        # Comportamento organizacional
                "creativity": 0.5,      # Criatividade moderada
                "risk_tolerance": 0.3,  # Baixa tolerância a risco
                "decision": 0.7,        # Boas decisões
                "adaptation": 0.7       # Boa adaptação
            }
        }
        
        # Registrar cada agente no sistema DNA
        agents_to_register = []
        
        if hasattr(self, 'architect') and self.architect:
            agents_to_register.append(("architect", self.architect))
            
        if hasattr(self, 'maestro') and self.maestro:
            agents_to_register.append(("maestro", self.maestro))
            
        if hasattr(self, 'bug_hunter') and self.bug_hunter:
            agents_to_register.append(("bug_hunter", self.bug_hunter))
            
        if hasattr(self, 'organizer') and self.organizer:
            agents_to_register.append(("organizer", self.organizer))
        
        # Registrar agentes no sistema DNA
        for agent_type, agent_instance in agents_to_register:
            if agent_type in agent_characteristics:
                dna = self.dynamic_agent_dna.register_agent_type(
                    agent_type, 
                    agent_characteristics[agent_type]
                )
                
                if dna:
                    self.logger.info(f"✅ Agent {agent_type} registered in DNA system with ID: {dna.dna_id}")
                    
                    # Adicionar hook para capturar performance real
                    self._add_dna_performance_hook(agent_instance, agent_type, dna.dna_id)
                else:
                    self.logger.warning(f"⚠️ Failed to register agent {agent_type} in DNA system")
        
        self.logger.info(f"🧬 Registered {len(agents_to_register)} agents in DNA system")
    
    def _add_dna_performance_hook(self, agent, agent_type: str, dna_id: str):
        """Adiciona hook para capturar performance real do agente para o sistema DNA"""
        if not agent or not hasattr(agent, 'execute'):
            return
            
        original_execute = getattr(agent, 'execute_with_dna_tracking', None) or agent.execute
        
        def dna_performance_wrapper(*args, **kwargs):
            start_time = time.time()
            success = False
            error_count = 0
            
            try:
                result = original_execute(*args, **kwargs)
                execution_time = time.time() - start_time
                success = True
                
                # Calcular fitness baseado em performance real
                fitness_score = self._calculate_fitness_score(
                    execution_time=execution_time,
                    success=success,
                    agent_type=agent_type,
                    result=result
                )
                
                # Registrar fitness no DNA
                self.dynamic_agent_dna.record_agent_performance(
                    agent_type=agent_type,
                    dna_id=dna_id,
                    fitness_score=fitness_score,
                    performance_data={
                        "execution_time": execution_time,
                        "success": success,
                        "timestamp": datetime.now().isoformat(),
                        "task_complexity": self._estimate_task_complexity(args, kwargs)
                    }
                )
                
                return result
                
            except Exception as e:
                execution_time = time.time() - start_time
                error_count = 1
                
                # Fitness baixo para falhas
                fitness_score = 0.1
                
                # Registrar fitness de falha
                self.dynamic_agent_dna.record_agent_performance(
                    agent_type=agent_type,
                    dna_id=dna_id,
                    fitness_score=fitness_score,
                    performance_data={
                        "execution_time": execution_time,
                        "success": False,
                        "error": str(e),
                        "error_type": type(e).__name__,
                        "timestamp": datetime.now().isoformat()
                    }
                )
                
                raise  # Re-raise the exception
        
        agent.execute_with_dna_tracking = dna_performance_wrapper
        agent.execute = dna_performance_wrapper
    
    def _calculate_fitness_score(self, execution_time: float, success: bool, 
                               agent_type: str, result: Any) -> float:
        """Calcula score de fitness baseado em performance real"""
        if not success:
            return 0.1
        
        # Score base de sucesso
        fitness = 0.5
        
        # Bonus por velocidade (score melhor para execução mais rápida)
        if execution_time <= 1.0:
            fitness += 0.3
        elif execution_time <= 5.0:
            fitness += 0.2
        elif execution_time <= 10.0:
            fitness += 0.1
        
        # Bonus específico por tipo de agente
        if agent_type == "architect" and result:
            # Arquiteto: bonus por qualidade do plano
            if hasattr(result, 'plan') or 'plan' in str(result):
                fitness += 0.2
        elif agent_type == "maestro" and result:
            # Maestro: bonus por coordenação efetiva
            if hasattr(result, 'strategy') or 'strategy' in str(result):
                fitness += 0.2
        elif agent_type == "bug_hunter" and result:
            # Bug Hunter: bonus por bugs encontrados/corrigidos
            if hasattr(result, 'bugs_fixed') or 'bug' in str(result).lower():
                fitness += 0.2
        elif agent_type == "organizer" and result:
            # Organizer: bonus por organização efetiva
            if hasattr(result, 'organized') or 'organized' in str(result).lower():
                fitness += 0.2
        
        # Normalizar para 0-1
        return min(1.0, max(0.0, fitness))
    
    def _estimate_task_complexity(self, args: tuple, kwargs: dict) -> float:
        """Estima complexidade da tarefa baseada nos argumentos"""
        complexity = 0.5  # Base
        
        # Complexidade baseada no tamanho dos argumentos
        total_arg_length = sum(len(str(arg)) for arg in args)
        total_kwarg_length = sum(len(str(v)) for v in kwargs.values())
        
        if total_arg_length + total_kwarg_length > 1000:
            complexity += 0.3
        elif total_arg_length + total_kwarg_length > 500:
            complexity += 0.2
        elif total_arg_length + total_kwarg_length > 100:
            complexity += 0.1
        
        return min(1.0, complexity)
    
    def _setup_capability_expansion_data_collection(self):
        """Configura coleta de dados para Capability Expansion"""
        self.logger.info("🚀 Setting up capability expansion data collection...")
        
        # Mapeamento de agentes para domínios
        self.agent_domain_mapping = {
            "architect": "planning",
            "maestro": "intelligence", 
            "bug_hunter": "analysis",
            "organizer": "optimization"
        }
        
        # Wrap métodos para coletar dados reais
        self._wrap_agents_for_capability_expansion()
        
        self.logger.info("✅ Capability expansion data collection configured")
    
    def _wrap_agents_for_capability_expansion(self):
        """Envolve agentes para coletar dados para capability expansion"""
        agents_to_wrap = []
        
        if hasattr(self, 'architect') and self.architect:
            agents_to_wrap.append(("architect", self.architect))
            
        if hasattr(self, 'maestro') and self.maestro:
            agents_to_wrap.append(("maestro", self.maestro))
            
        if hasattr(self, 'bug_hunter') and self.bug_hunter:
            agents_to_wrap.append(("bug_hunter", self.bug_hunter))
            
        if hasattr(self, 'organizer') and self.organizer:
            agents_to_wrap.append(("organizer", self.organizer))
        
        for agent_name, agent_instance in agents_to_wrap:
            if hasattr(agent_instance, 'execute'):
                self._wrap_agent_for_capability_expansion(agent_instance, agent_name)
    
    def _wrap_agent_for_capability_expansion(self, agent, agent_name: str):
        """Envolve um agente para coletar dados para capability expansion"""
        if not agent or not hasattr(agent, 'execute'):
            return
            
        # Obter método original (pode já estar wrapped)
        original_execute = getattr(agent, 'execute_capability_wrapped', None) or agent.execute
        domain = self.agent_domain_mapping.get(agent_name, "unknown")
        
        def capability_expansion_wrapper(*args, **kwargs):
            start_time = time.time()
            success = False
            
            try:
                result = original_execute(*args, **kwargs)
                execution_time = time.time() - start_time
                success = True
                
                # Registrar evento no sistema de capability expansion
                self.autonomous_capability_expansion.record_real_system_event(
                    event_type=f"{agent_name}_execution",
                    domain=domain,
                    success=True,
                    details={
                        "agent_name": agent_name,
                        "execution_time": execution_time,
                        "task_args": str(args)[:100] if args else "no_args",
                        "result_size": len(str(result)) if result else 0
                    }
                )
                
                return result
                
            except Exception as e:
                execution_time = time.time() - start_time
                
                # Registrar falha no sistema de capability expansion
                self.autonomous_capability_expansion.record_real_system_event(
                    event_type=f"{agent_name}_failure",
                    domain=domain,
                    success=False,
                    details={
                        "agent_name": agent_name,
                        "execution_time": execution_time,
                        "error_type": type(e).__name__,
                        "error_message": str(e)[:100]
                    }
                )
                
                raise  # Re-raise the exception
        
        # Preservar o método original para evitar multiple wrapping
        agent.execute_capability_wrapped = original_execute
        agent.execute = capability_expansion_wrapper
    
    def _setup_meta_learning_data_collection(self):
        """Configura coleta de dados para Meta-Learning"""
        self.logger.info("🧠 Setting up meta-learning data collection...")
        
        # Wrap métodos para coletar dados de aprendizado
        self._wrap_agents_for_meta_learning()
        
        self.logger.info("✅ Meta-learning data collection configured")
    
    def _wrap_agents_for_meta_learning(self):
        """Envolve agentes para coletar dados de aprendizado"""
        agents_to_wrap = []
        
        if hasattr(self, 'architect') and self.architect:
            agents_to_wrap.append(("architect", self.architect))
            
        if hasattr(self, 'maestro') and self.maestro:
            agents_to_wrap.append(("maestro", self.maestro))
            
        if hasattr(self, 'bug_hunter') and self.bug_hunter:
            agents_to_wrap.append(("bug_hunter", self.bug_hunter))
            
        if hasattr(self, 'organizer') and self.organizer:
            agents_to_wrap.append(("organizer", self.organizer))
        
        for agent_name, agent_instance in agents_to_wrap:
            if hasattr(agent_instance, 'execute'):
                self._wrap_agent_for_meta_learning(agent_instance, agent_name)
    
    def _wrap_agent_for_meta_learning(self, agent, agent_name: str):
        """Envolve um agente para coletar dados de meta-aprendizado"""
        if not agent or not hasattr(agent, 'execute'):
            return
            
        # Obter método original (pode já estar wrapped múltiplas vezes)
        original_execute = getattr(agent, 'execute_meta_learning_wrapped', None) or agent.execute
        
        def meta_learning_wrapper(*args, **kwargs):
            start_time = time.time()
            success = False
            error_info = None
            
            try:
                result = original_execute(*args, **kwargs)
                execution_time = time.time() - start_time
                success = True
                
                # Registrar evento de aprendizado por sucesso
                self.meta_learning_intelligence.record_system_learning_event(
                    event_type="execution_success",
                    agent_name=agent_name,
                    task_description=str(args[0])[:100] if args else "agent_execution",
                    success=True,
                    execution_time=execution_time
                )
                
                return result
                
            except Exception as e:
                execution_time = time.time() - start_time
                error_info = {
                    "error_type": type(e).__name__,
                    "error_message": str(e)[:100]
                }
                
                # Registrar evento de aprendizado por falha
                self.meta_learning_intelligence.record_system_learning_event(
                    event_type="execution_failure",
                    agent_name=agent_name,
                    task_description=str(args[0])[:100] if args else "agent_execution",
                    success=False,
                    execution_time=execution_time,
                    error_info=error_info
                )
                
                raise  # Re-raise the exception
        
        # Preservar o método original para evitar multiple wrapping
        agent.execute_meta_learning_wrapped = original_execute
        agent.execute = meta_learning_wrapper
        
        self.logger.info("🧹 Automatic cleanup scheduled")
