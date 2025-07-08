"""
Formal Agent Interface Protocol - Agente Autônomo v2.8.1
Implements the AgentInterface protocol to standardize agent contracts and reduce coupling.
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, List, Tuple, Protocol, runtime_checkable
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime
import logging
import asyncio
from pathlib import Path


class AgentCapability(Enum):
    """Standardized agent capabilities"""
    CODE_ANALYSIS = "code_analysis"
    ARCHITECTURE_DESIGN = "architecture_design"
    PROBLEM_SOLVING = "problem_solving"
    STRATEGY_SELECTION = "strategy_selection"
    ORCHESTRATION = "orchestration"
    DECISION_MAKING = "decision_making"
    CODE_REVIEW = "code_review"
    QUALITY_ASSESSMENT = "quality_assessment"
    BUG_DETECTION = "bug_detection"
    ERROR_ANALYSIS = "error_analysis"
    AUTOMATIC_FIXING = "automatic_fixing"
    COORDINATION = "coordination"
    MEDIATION = "mediation"
    CONFLICT_RESOLUTION = "conflict_resolution"
    COLLABORATION_OPTIMIZATION = "collaboration_optimization"
    TECHNICAL_DEBT_IDENTIFICATION = "technical_debt_identification"
    REFACTORING_OPPORTUNITIES = "refactoring_opportunities"
    PERFORMANCE_ANALYSIS = "performance_analysis"
    MODEL_SELECTION = "model_selection"
    CONFIGURATION_TUNING = "configuration_tuning"
    SELF_AWARENESS = "self_awareness"
    META_LEARNING = "meta_learning"
    COGNITIVE_OPTIMIZATION = "cognitive_optimization"
    INTELLIGENCE_EVOLUTION = "intelligence_evolution"
    LONG_TERM_PLANNING = "long_term_planning"
    GOAL_OPTIMIZATION = "goal_optimization"
    RESOURCE_STRATEGY = "resource_strategy"
    RISK_ASSESSMENT = "risk_assessment"
    OPPORTUNITY_IDENTIFICATION = "opportunity_identification"


class AgentPriority(Enum):
    """Standardized agent priority levels"""
    CRITICAL = 1
    HIGH = 2
    MEDIUM = 3
    LOW = 4
    BACKGROUND = 5


class AgentStatus(Enum):
    """Standardized agent status"""
    IDLE = "idle"
    BUSY = "busy"
    ERROR = "error"
    OFFLINE = "offline"
    INITIALIZING = "initializing"
    SHUTTING_DOWN = "shutting_down"


@dataclass
class AgentContext:
    """Typed context system for agent operations"""
    task_id: str
    objective: str
    priority: AgentPriority
    capabilities_required: List[AgentCapability]
    metadata: Dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.now)
    timeout: Optional[float] = None
    dependencies: List[str] = field(default_factory=list)
    
    def __post_init__(self):
        if not isinstance(self.priority, AgentPriority):
            self.priority = AgentPriority(self.priority)


@dataclass
class AgentResult:
    """Standardized agent result format"""
    task_id: str
    success: bool
    data: Any
    error_message: Optional[str] = None
    execution_time: float = 0.0
    metadata: Dict[str, Any] = field(default_factory=dict)
    timestamp: datetime = field(default_factory=datetime.now)


@dataclass
class AgentMetrics:
    """Standardized agent performance metrics"""
    agent_name: str
    tasks_completed: int = 0
    tasks_failed: int = 0
    average_execution_time: float = 0.0
    success_rate: float = 0.0
    last_activity: Optional[datetime] = None
    capabilities_used: Dict[AgentCapability, int] = field(default_factory=dict)
    resource_usage: Dict[str, float] = field(default_factory=dict)


@runtime_checkable
class AgentInterface(Protocol):
    """Formal interface protocol for all agents"""
    
    @property
    def name(self) -> str:
        """Agent name"""
        ...
    
    @property
    def capabilities(self) -> List[AgentCapability]:
        """List of agent capabilities"""
        ...
    
    @property
    def status(self) -> AgentStatus:
        """Current agent status"""
        ...
    
    @property
    def metrics(self) -> AgentMetrics:
        """Agent performance metrics"""
        ...
    
    async def initialize(self, config: Dict[str, Any]) -> bool:
        """Initialize the agent with configuration"""
        ...
    
    async def execute(self, context: AgentContext) -> AgentResult:
        """Execute a task with the given context"""
        ...
    
    async def handle_message(self, message: Any) -> bool:
        """Handle inter-agent communication messages"""
        ...
    
    async def shutdown(self) -> bool:
        """Gracefully shutdown the agent"""
        ...
    
    def get_capability_score(self, capability: AgentCapability) -> float:
        """Get confidence score for a specific capability (0.0-1.0)"""
        ...


class BaseAgent(ABC):
    """Abstract base class implementing the AgentInterface protocol"""
    
    def __init__(self, name: str, capabilities: List[AgentCapability], logger: logging.Logger):
        self._name = name
        self._capabilities = capabilities
        self._logger = logger
        self._status = AgentStatus.INITIALIZING
        self._metrics = AgentMetrics(agent_name=name)
        self._config: Optional[Dict[str, Any]] = None
        self._initialized = False
    
    @property
    def name(self) -> str:
        return self._name
    
    @property
    def capabilities(self) -> List[AgentCapability]:
        return self._capabilities.copy()
    
    @property
    def status(self) -> AgentStatus:
        return self._status
    
    @property
    def metrics(self) -> AgentMetrics:
        return self._metrics
    
    async def initialize(self, config: Dict[str, Any]) -> bool:
        """Initialize the agent with configuration"""
        try:
            self._logger.info(f"Initializing {self._name}...")
            self._config = config
            self._status = AgentStatus.IDLE
            self._initialized = True
            self._metrics.last_activity = datetime.now()
            self._logger.info(f"{self._name} initialized successfully")
            return True
        except Exception as e:
            self._logger.error(f"Failed to initialize {self._name}: {e}")
            self._status = AgentStatus.ERROR
            return False
    
    @abstractmethod
    async def execute(self, context: AgentContext) -> AgentResult:
        """Execute a task with the given context - must be implemented by subclasses"""
        pass
    
    async def handle_message(self, message: Any) -> bool:
        """Default message handler - can be overridden by subclasses"""
        self._logger.debug(f"{self._name} received message: {type(message).__name__}")
        return True
    
    async def shutdown(self) -> bool:
        """Gracefully shutdown the agent"""
        try:
            self._logger.info(f"Shutting down {self._name}...")
            self._status = AgentStatus.SHUTTING_DOWN
            # Allow subclasses to implement cleanup
            await self._cleanup()
            self._status = AgentStatus.OFFLINE
            self._logger.info(f"{self._name} shut down successfully")
            return True
        except Exception as e:
            self._logger.error(f"Error shutting down {self._name}: {e}")
            return False
    
    def get_capability_score(self, capability: AgentCapability) -> float:
        """Get confidence score for a specific capability"""
        if capability in self._capabilities:
            # Default implementation - subclasses should override
            return 0.8
        return 0.0
    
    async def _cleanup(self):
        """Internal cleanup method - can be overridden by subclasses"""
        pass
    
    def _update_metrics(self, success: bool, execution_time: float, capability_used: Optional[AgentCapability] = None):
        """Update agent metrics"""
        if success:
            self._metrics.tasks_completed += 1
        else:
            self._metrics.tasks_failed += 1
        
        # Update average execution time
        total_tasks = self._metrics.tasks_completed + self._metrics.tasks_failed
        if total_tasks > 0:
            self._metrics.average_execution_time = (
                (self._metrics.average_execution_time * (total_tasks - 1) + execution_time) / total_tasks
            )
        
        # Update success rate
        if total_tasks > 0:
            self._metrics.success_rate = self._metrics.tasks_completed / total_tasks
        
        # Update capability usage
        if capability_used:
            self._metrics.capabilities_used[capability_used] = (
                self._metrics.capabilities_used.get(capability_used, 0) + 1
            )
        
        self._metrics.last_activity = datetime.now()


class AgentRegistry:
    """Registry for managing agent instances and their capabilities"""
    
    def __init__(self):
        self._agents: Dict[str, AgentInterface] = {}
        self._capability_index: Dict[AgentCapability, List[str]] = {}
        self._logger = logging.getLogger(__name__)
    
    def register_agent(self, agent: AgentInterface) -> bool:
        """Register an agent in the registry"""
        try:
            if agent.name in self._agents:
                self._logger.warning(f"Agent {agent.name} already registered, overwriting")
            
            self._agents[agent.name] = agent
            
            # Update capability index
            for capability in agent.capabilities:
                if capability not in self._capability_index:
                    self._capability_index[capability] = []
                if agent.name not in self._capability_index[capability]:
                    self._capability_index[capability].append(agent.name)
            
            self._logger.info(f"Registered agent {agent.name} with capabilities: {[c.value for c in agent.capabilities]}")
            return True
        except Exception as e:
            self._logger.error(f"Failed to register agent {agent.name}: {e}")
            return False
    
    def unregister_agent(self, agent_name: str) -> bool:
        """Unregister an agent from the registry"""
        try:
            if agent_name not in self._agents:
                return False
            
            agent = self._agents[agent_name]
            
            # Remove from capability index
            for capability in agent.capabilities:
                if capability in self._capability_index and agent_name in self._capability_index[capability]:
                    self._capability_index[capability].remove(agent_name)
            
            del self._agents[agent_name]
            self._logger.info(f"Unregistered agent {agent_name}")
            return True
        except Exception as e:
            self._logger.error(f"Failed to unregister agent {agent_name}: {e}")
            return False
    
    def get_agent(self, agent_name: str) -> Optional[AgentInterface]:
        """Get an agent by name"""
        return self._agents.get(agent_name)
    
    def get_agents_with_capability(self, capability: AgentCapability) -> List[AgentInterface]:
        """Get all agents with a specific capability"""
        agent_names = self._capability_index.get(capability, [])
        return [self._agents[name] for name in agent_names if name in self._agents]
    
    def get_best_agent_for_capability(self, capability: AgentCapability) -> Optional[AgentInterface]:
        """Get the best agent for a specific capability based on scores"""
        agents = self.get_agents_with_capability(capability)
        if not agents:
            return None
        
        # Find agent with highest capability score
        best_agent = max(agents, key=lambda a: a.get_capability_score(capability))
        return best_agent if best_agent.get_capability_score(capability) > 0 else None
    
    def get_all_agents(self) -> List[AgentInterface]:
        """Get all registered agents"""
        return list(self._agents.values())
    
    def get_agent_metrics(self) -> Dict[str, AgentMetrics]:
        """Get metrics for all agents"""
        return {name: agent.metrics for name, agent in self._agents.items()}


# Global agent registry instance
_agent_registry = AgentRegistry()

def get_agent_registry() -> AgentRegistry:
    """Get the global agent registry instance"""
    return _agent_registry 