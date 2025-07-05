"""
Async Agent Orchestrator - Coordena múltiplos agentes em paralelo
"""

import asyncio
import logging
import time
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from enum import Enum
import concurrent.futures
from datetime import datetime

from agent.agents import ArchitectAgent, MaestroAgent, CodeReviewAgent
from agent.agents.log_analysis_agent import LogAnalysisAgent
from agent.agents.model_sommelier_agent import ModelSommelierAgent
from agent.agents.frontend_artisan_agent import FrontendArtisanAgent
from agent.tool_executor import list_available_models


class AgentType(Enum):
    ARCHITECT = "architect"
    MAESTRO = "maestro"
    CODE_REVIEW = "code_review"
    LOG_ANALYSIS = "log_analysis"
    MODEL_SOMMELIER = "model_sommelier"
    FRONTEND_ARTISAN = "frontend_artisan"


@dataclass
class AgentTask:
    """Representa uma tarefa para um agente específico"""
    agent_type: AgentType
    task_id: str
    objective: str
    context: Dict[str, Any]
    priority: int = 5
    dependencies: Optional[List[str]] = None
    timeout: Optional[float] = None
    created_at: Optional[datetime] = None
    
    def __post_init__(self):
        if self.dependencies is None:
            self.dependencies = []
        if self.created_at is None:
            self.created_at = datetime.now()


@dataclass
class AgentResult:
    """Resultado de uma tarefa de agente"""
    task_id: str
    agent_type: AgentType
    success: bool
    result: Any
    execution_time: float
    error_message: Optional[str] = None


class AsyncAgentOrchestrator:
    """Orquestrador assíncrono para múltiplos agentes"""
    
    def __init__(self, config: Dict[str, Any], logger: logging.Logger):
        self.config = config
        self.logger = logger
        self.agent_pools = {}
        self.active_tasks = {}
        self.completed_tasks = {}
        self.failed_tasks = {}
        
        # Configurações
        self.max_concurrent_agents = config.get('async_orchestration', {}).get('max_concurrent', 4)
        self.default_timeout = config.get('async_orchestration', {}).get('default_timeout', 300)
        
        # Semáforos para controle de concorrência
        self.semaphores = {
            agent_type: asyncio.Semaphore(self.max_concurrent_agents) 
            for agent_type in AgentType
        }
        
        # Inicializar agentes
        self._initialize_agent_pools()
        
        self.logger.info(f"🚀 AsyncAgentOrchestrator initialized with {self.max_concurrent_agents} concurrent agents")
    
    def _initialize_agent_pools(self):
        """Inicializa pools de agentes com as assinaturas de construtor corretas."""
        try:
            self.agent_pools[AgentType.ARCHITECT] = ArchitectAgent(
                model_config=self.config.get("models", {}).get("architect_default", "gpt-4"),
                logger=self.logger.getChild("ArchitectAgent")
            )
            
            self.agent_pools[AgentType.MAESTRO] = MaestroAgent(
                config=self.config,
                logger=self.logger.getChild("MaestroAgent")
            )
            
            self.agent_pools[AgentType.CODE_REVIEW] = CodeReviewAgent(
                model_config=self.config.get("models", {}).get("code_review_default", "gpt-4"),
                logger=self.logger.getChild("CodeReviewAgent")
            )
            
            log_analyzer_model_config = self.config.get("models", {}).get("log_analyzer_default", self.config.get("models", {}).get("architect_default"))
            self.agent_pools[AgentType.LOG_ANALYSIS] = LogAnalysisAgent(
                model_config=log_analyzer_model_config,
                logger=self.logger.getChild("LogAnalysisAgent")
            )

            self.agent_pools[AgentType.MODEL_SOMMELIER] = ModelSommelierAgent(
                model_config=self.config.get("models", {}).get("sommelier_default", self.config.get("models", {}).get("architect_default")),
                config=self.config,
                logger=self.logger.getChild("ModelSommelierAgent")
            )

            self.agent_pools[AgentType.FRONTEND_ARTISAN] = FrontendArtisanAgent(
                model_config=self.config.get("models", {}).get("frontend_artisan_default", self.config.get("models", {}).get("architect_default")),
                config=self.config,
                logger=self.logger.getChild("FrontendArtisanAgent")
            )
            
            self.logger.info("✅ Agent pools initialized successfully")
            
        except Exception as e:
            self.logger.error(f"❌ Error initializing agent pools: {str(e)}", exc_info=True)
            raise
    
    async def submit_parallel_tasks(self, tasks: List[AgentTask]) -> List[str]:
        """Submete múltiplas tarefas para execução paralela"""
        task_ids = []
        
        # Ordenar por prioridade
        sorted_tasks = sorted(tasks, key=lambda t: t.priority, reverse=True)
        
        # Criar tasks assíncronas
        async_tasks = []
        for task in sorted_tasks:
            self.active_tasks[task.task_id] = task
            task_ids.append(task.task_id)
            async_tasks.append(self._execute_task(task))
        
        # Executar todas as tarefas em paralelo
        await asyncio.gather(*async_tasks, return_exceptions=True)
        
        return task_ids
    
    async def _execute_task(self, task: AgentTask) -> AgentResult:
        """Executa uma tarefa específica"""
        start_time = time.time()
        
        try:
            # Aguardar dependências
            await self._wait_for_dependencies(task)
            
            # Controlar concorrência
            async with self.semaphores[task.agent_type]:
                self.logger.info(f"🔄 Starting task: {task.task_id} ({task.agent_type.value})")
                
                # Executar tarefa
                result = await asyncio.wait_for(
                    self._run_agent_task(task),
                    timeout=task.timeout or self.default_timeout
                )
                
                execution_time = time.time() - start_time
                
                agent_result = AgentResult(
                    task_id=task.task_id,
                    agent_type=task.agent_type,
                    success=True,
                    result=result,
                    execution_time=execution_time
                )
                
                self.completed_tasks[task.task_id] = agent_result
                self.logger.info(f"✅ Task completed: {task.task_id} ({execution_time:.2f}s)")
                
                return agent_result
                
        except Exception as e:
            execution_time = time.time() - start_time
            error_msg = f"Task {task.task_id} failed: {str(e)}"
            self.logger.error(f"❌ {error_msg}")
            
            result = AgentResult(
                task_id=task.task_id,
                agent_type=task.agent_type,
                success=False,
                result=None,
                execution_time=execution_time,
                error_message=error_msg
            )
            
            self.failed_tasks[task.task_id] = result
            return result
        
        finally:
            if task.task_id in self.active_tasks:
                del self.active_tasks[task.task_id]
    
    async def _wait_for_dependencies(self, task: AgentTask):
        """Aguarda dependências serem completadas"""
        if not task.dependencies:
            return
        
        self.logger.info(f"⏳ Waiting for dependencies: {task.dependencies}")
        
        while True:
            unfinished_deps = []
            for dep_id in task.dependencies:
                if dep_id not in self.completed_tasks:
                    unfinished_deps.append(dep_id)
            
            if not unfinished_deps:
                break
            
            await asyncio.sleep(0.1)
    
    async def _run_agent_task(self, task: AgentTask) -> Any:
        """Executa a tarefa específica do agente"""
        agent = self.agent_pools[task.agent_type]
        loop = asyncio.get_event_loop()
        
        if task.agent_type == AgentType.ARCHITECT:
            with concurrent.futures.ThreadPoolExecutor() as executor:
                future = executor.submit(
                    agent.plan_action,
                    task.objective,
                    task.context.get('manifest', ''),
                    task.context.get('file_content_context', '')
                )
                return await loop.run_in_executor(None, future.result)
        
        elif task.agent_type == AgentType.MAESTRO:
            with concurrent.futures.ThreadPoolExecutor() as executor:
                future = executor.submit(
                    agent.choose_strategy,
                    task.context.get('action_plan_data', {}),
                    task.context.get('memory_summary', ''),
                    task.context.get('failed_strategy_context')
                )
                return await loop.run_in_executor(None, future.result)
        
        elif task.agent_type == AgentType.CODE_REVIEW:
            with concurrent.futures.ThreadPoolExecutor() as executor:
                future = executor.submit(
                    agent.review_patches,
                    task.context.get('patches_to_apply', [])
                )
                return await loop.run_in_executor(None, future.result)
        
        elif task.agent_type == AgentType.LOG_ANALYSIS:
            with concurrent.futures.ThreadPoolExecutor() as executor:
                future = executor.submit(
                    agent.analyze_logs,
                    task.context.get('log_file_path', 'logs/app.log'),
                    task.context.get('lines_to_analyze', 200)
                )
                return await loop.run_in_executor(None, future.result)
        
        elif task.agent_type == AgentType.MODEL_SOMMELIER:
            with concurrent.futures.ThreadPoolExecutor() as executor:
                # This agent has dependencies on other tools/data
                agent_perf_summary = task.context.get('agent_performance_summary', {})
                success, available_models = list_available_models()
                if not success:
                    self.logger.error("Could not retrieve available models for Model Sommelier.")
                    available_models = [] # Proceed with an empty list

                future = executor.submit(
                    agent.propose_model_optimization,
                    agent_performance_summary=agent_perf_summary,
                    available_models=available_models
                )
                return await loop.run_in_executor(None, future.result)
        
        elif task.agent_type == AgentType.FRONTEND_ARTISAN:
            with concurrent.futures.ThreadPoolExecutor() as executor:
                future = executor.submit(
                    agent.propose_frontend_improvement,
                    file_path=task.context.get('file_path'),
                    file_content=task.context.get('file_content')
                )
                return await loop.run_in_executor(None, future.result)
        
        else:
            raise ValueError(f"Unknown agent type: {task.agent_type}")
    
    async def create_parallel_evolution_cycle(self, objective: str, context: Dict[str, Any]) -> List[AgentTask]:
        """Cria um ciclo de evolução paralelo"""
        tasks = []
        
        # Task 1: Architect gera patches (alta prioridade)
        architect_task = AgentTask(
            agent_type=AgentType.ARCHITECT,
            task_id=f"architect_{int(time.time())}",
            objective=f"Generate solution patches for: {objective}",
            context=context,
            priority=9,
            timeout=120
        )
        tasks.append(architect_task)
        
        # Task 2: Code Review em paralelo
        code_review_task = AgentTask(
            agent_type=AgentType.CODE_REVIEW,
            task_id=f"code_review_{int(time.time())}",
            objective=f"Review current code for: {objective}",
            context=context,
            priority=7,
            timeout=90
        )
        tasks.append(code_review_task)
        
        # Task 3: Maestro escolhe estratégia (depende do Architect)
        maestro_task = AgentTask(
            agent_type=AgentType.MAESTRO,
            task_id=f"maestro_{int(time.time())}",
            objective=f"Choose optimal strategy for: {objective}",
            context=context,
            priority=8,
            dependencies=[architect_task.task_id],
            timeout=60
        )
        tasks.append(maestro_task)
        
        self.logger.info(f"🚀 Created parallel evolution cycle with {len(tasks)} tasks")
        return tasks
    
    def get_orchestration_status(self) -> Dict[str, Any]:
        """Retorna status detalhado da orquestração"""
        return {
            'active_tasks': len(self.active_tasks),
            'completed_tasks': len(self.completed_tasks),
            'failed_tasks': len(self.failed_tasks),
            'max_concurrent_agents': self.max_concurrent_agents,
            'agent_pools_status': {
                agent_type.value: 'active' 
                for agent_type in self.agent_pools.keys()
            }
        }
