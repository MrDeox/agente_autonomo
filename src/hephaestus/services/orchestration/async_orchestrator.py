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

from hephaestus.agents import (
    ArchitectAgent, 
    MaestroAgent, 
    BugHunterAgent,
    LogAnalysisAgent,
    PerformanceAnalysisAgent
)
from hephaestus.utils.tool_executor import list_available_models


class AgentType(Enum):
    ARCHITECT = "architect"
    MAESTRO = "maestro"
    CODE_REVIEW = "code_review"
    LOG_ANALYSIS = "log_analysis"
    MODEL_SOMMELIER = "model_sommelier"
    FRONTEND_ARTISAN = "frontend_artisan"
    BUG_HUNTER = "bug_hunter"


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
        
        # Executor para tarefas bloqueantes
        self.executor = concurrent.futures.ThreadPoolExecutor(max_workers=self.max_concurrent_agents * 2)

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
                model_config=self.config.get("models", {}).get("maestro_default", self.config.get("models", {}).get("architect_default")),
                logger=self.logger.getChild("MaestroAgent"),
                config=self.config
            )
            
            self.agent_pools[AgentType.CODE_REVIEW] = BugHunterAgent(
                model_config=self.config.get("models", {}).get("code_review_default", "gpt-4"),
                config=self.config,
                logger=self.logger.getChild("BugHunterAgent")
            )
            
            log_analyzer_model_config = self.config.get("models", {}).get("log_analyzer_default", self.config.get("models", {}).get("architect_default"))
            self.agent_pools[AgentType.LOG_ANALYSIS] = LogAnalysisAgent(
                model_config=log_analyzer_model_config,
                logger=self.logger.getChild("LogAnalysisAgent")
            )

            # Skip agents that don't exist for now
            # self.agent_pools[AgentType.MODEL_SOMMELIER] = ModelSommelierAgent(...)
            # self.agent_pools[AgentType.FRONTEND_ARTISAN] = FrontendArtisanAgent(...)
            
            self.agent_pools[AgentType.BUG_HUNTER] = BugHunterAgent(
                model_config=self.config.get("models", {}).get("bug_hunter_default", self.config.get("models", {}).get("architect_default")),
                config=self.config,
                logger=self.logger.getChild("BugHunterAgent")
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
        """Aguarda dependências serem completadas ou falharem."""
        if not task.dependencies:
            return

        self.logger.info(f"⏳ Task {task.task_id} waiting for dependencies: {task.dependencies}")

        for dep_id in task.dependencies:
            while dep_id not in self.completed_tasks and dep_id not in self.failed_tasks:
                await asyncio.sleep(1)  # Poll less aggressively

            if dep_id in self.failed_tasks:
                raise RuntimeError(f"Dependency task {dep_id} failed. Aborting task {task.task_id}.")
        
        self.logger.info(f"✅ Dependencies for task {task.task_id} are met.")
    
    async def _run_agent_task(self, task: AgentTask) -> Any:
        """Executa a tarefa específica do agente de forma não-bloqueante."""
        agent = self.agent_pools[task.agent_type]

        if task.agent_type == AgentType.ARCHITECT:
            # For async methods, call directly without executor
            if hasattr(agent, 'plan_action') and asyncio.iscoroutinefunction(agent.plan_action):
                result = await agent.plan_action(
                    task.objective,
                    task.context.get('manifest', ''),
                    task.context.get('file_content_context', '')
                )
                # If it returns a tuple (result, error), take the result part
                if isinstance(result, tuple) and len(result) == 2:
                    plan, error = result
                    if error:
                        raise Exception(f"Plan action failed: {error}")
                    return plan
                return result
            else:
                # For sync methods, use executor
                loop = asyncio.get_running_loop()
                return await loop.run_in_executor(
                    self.executor,
                    agent.plan_action,
                    task.objective,
                    task.context.get('manifest', ''),
                    task.context.get('file_content_context', '')
                )

        elif task.agent_type == AgentType.MAESTRO:
            loop = asyncio.get_running_loop()
            return await loop.run_in_executor(
                self.executor,
                agent.choose_strategy,
                task.context.get('action_plan_data', {}),
                task.context.get('memory_summary', ''),
                task.context.get('failed_strategy_context')
            )

        elif task.agent_type == AgentType.CODE_REVIEW:
            loop = asyncio.get_running_loop()
            # Check if agent has hunt_bugs method
            if hasattr(agent, 'hunt_bugs'):
                return await loop.run_in_executor(
                    self.executor,
                    agent.hunt_bugs,
                    task.context.get('project_path', ''),
                    task.context.get('code_to_analyze', '')
                )
            else:
                self.logger.warning(f"Agent {agent.__class__.__name__} does not have hunt_bugs method")
                return {"status": "skipped", "reason": "method not available"}

        elif task.agent_type == AgentType.LOG_ANALYSIS:
            loop = asyncio.get_running_loop()
            return await loop.run_in_executor(
                self.executor,
                agent.analyze_logs,
                task.context.get('log_file_path', 'logs/app.log'),
                task.context.get('lines_to_analyze', 200)
            )

        # Skip unavailable agents
        elif task.agent_type == AgentType.MODEL_SOMMELIER:
            self.logger.warning("Model Sommelier agent not available")
            return {"status": "skipped", "reason": "agent not available"}

        elif task.agent_type == AgentType.FRONTEND_ARTISAN:
            self.logger.warning("Frontend Artisan agent not available")
            return {"status": "skipped", "reason": "agent not available"}

        elif task.agent_type == AgentType.BUG_HUNTER:
            loop = asyncio.get_running_loop()
            # Check if agent has hunt_bugs method
            if hasattr(agent, 'hunt_bugs'):
                return await loop.run_in_executor(
                    self.executor,
                    agent.hunt_bugs,
                    task.context.get('project_path', ''),
                    task.context.get('code_to_analyze', '')
                )
            else:
                self.logger.warning(f"Agent {agent.__class__.__name__} does not have hunt_bugs method")
                return {"status": "skipped", "reason": "method not available"}

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
        
        # Task 2: Bug Hunter em paralelo (nova!)
        bug_hunter_task = AgentTask(
            agent_type=AgentType.BUG_HUNTER,
            task_id=f"bug_hunter_{int(time.time())}",
            objective=f"Hunt for bugs while processing: {objective}",
            context=context,
            priority=8,
            timeout=180
        )
        tasks.append(bug_hunter_task)
        
        # Task 3: Code Review em paralelo
        code_review_task = AgentTask(
            agent_type=AgentType.CODE_REVIEW,
            task_id=f"code_review_{int(time.time())}",
            objective=f"Review current code for: {objective}",
            context=context,
            priority=7,
            timeout=90
        )
        tasks.append(code_review_task)
        
        # Task 4: Maestro escolhe estratégia (depende do Architect)
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
        
        self.logger.info(f"🚀 Created parallel evolution cycle with {len(tasks)} tasks (including Bug Hunter!)")
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