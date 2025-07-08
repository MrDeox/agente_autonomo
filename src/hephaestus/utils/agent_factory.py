"""
Agent Factory - Centralizes agent creation with dependency injection
"""

from typing import Dict, Any, Type, Optional
import logging
from hephaestus.agents.base import BaseAgent
from hephaestus.utils.config_manager import ConfigManager
from hephaestus.utils.logger_factory import LoggerFactory


class AgentFactory:
    """Factory for creating agents with standardized dependency injection."""
    
    @staticmethod
    def create_agent(agent_type: str, **kwargs) -> BaseAgent:
        """
        Create an agent with automatic dependency injection.
        
        Args:
            agent_type: Type of agent to create (e.g., "ArchitectAgent")
            **kwargs: Additional parameters for agent initialization
            
        Returns:
            Configured agent instance
        """
        # Get agent-specific configuration
        config = ConfigManager.get_agent_config(agent_type)
        
        # Get standardized logger
        logger = LoggerFactory.get_agent_logger(agent_type)
        
        # Import and create agent dynamically
        agent_class = AgentFactory._get_agent_class(agent_type)
        
        # Inject standard dependencies
        standard_kwargs = {
            'config': config,
            'logger': logger,
            'model_config': ConfigManager.get_model_config(config.get('model_type', 'default')),
            **kwargs
        }
        
        return agent_class(**standard_kwargs)
    
    @staticmethod
    def inject_dependencies(agent: BaseAgent, config: Dict[str, Any], logger: logging.Logger) -> None:
        """
        Inject dependencies into an existing agent.
        
        Args:
            agent: Agent instance to inject dependencies into
            config: Configuration dictionary
            logger: Logger instance
        """
        if hasattr(agent, 'config'):
            agent.config = config
        if hasattr(agent, 'logger'):
            agent.logger = logger
        if hasattr(agent, 'model_config'):
            agent.model_config = ConfigManager.get_model_config(
                config.get('model_type', 'default')
            )
    
    @staticmethod
    def _get_agent_class(agent_type: str) -> Type[BaseAgent]:
        """
        Dynamically import and return agent class.
        
        Args:
            agent_type: Name of the agent type
            
        Returns:
            Agent class
        """
        # Map agent types to their modules
        agent_mapping = {
            'ArchitectAgent': 'hephaestus.agents.architect',
            'MaestroAgent': 'hephaestus.agents.maestro', 
            'BugHunterAgent': 'hephaestus.agents.bug_hunter',
            'OrganizerAgent': 'hephaestus.agents.organizer',
            'ErrorDetectorAgent': 'hephaestus.agents.error_detector_agent',
            'DependencyFixerAgent': 'hephaestus.agents.dependency_fixer_agent',
            'CycleMonitorAgent': 'hephaestus.agents.cycle_monitor_agent',
        }
        
        if agent_type not in agent_mapping:
            raise ValueError(f"Unknown agent type: {agent_type}")
        
        module_name = agent_mapping[agent_type]
        
        try:
            module = __import__(module_name, fromlist=[agent_type])
            return getattr(module, agent_type)
        except (ImportError, AttributeError) as e:
            raise ImportError(f"Could not import {agent_type} from {module_name}: {e}")


class AgentRegistry:
    """Registry for managing active agent instances."""
    
    def __init__(self):
        self._agents: Dict[str, BaseAgent] = {}
    
    def register_agent(self, name: str, agent: BaseAgent) -> None:
        """Register an agent instance."""
        self._agents[name] = agent
    
    def get_agent(self, name: str) -> Optional[BaseAgent]:
        """Get a registered agent by name."""
        return self._agents.get(name)
    
    def list_agents(self) -> Dict[str, BaseAgent]:
        """Get all registered agents."""
        return self._agents.copy()
    
    def remove_agent(self, name: str) -> Optional[BaseAgent]:
        """Remove and return an agent."""
        return self._agents.pop(name, None)


# Global registry instance
_global_registry = AgentRegistry()

def get_global_registry() -> AgentRegistry:
    """Get the global agent registry."""
    return _global_registry