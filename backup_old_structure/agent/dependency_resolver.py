"""
Dependency Resolver - Agente Autônomo v2.8.1
Implements dependency injection and resolution to reduce tight coupling between components.
"""

import asyncio
import logging
from typing import Dict, Any, Optional, List, Type, TypeVar, Callable, Union
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime
import inspect
from pathlib import Path
import weakref

from agent.interfaces import AgentInterface, AgentRegistry, get_agent_registry


class DependencyScope(Enum):
    """Dependency injection scopes"""
    SINGLETON = "singleton"
    TRANSIENT = "transient"
    REQUEST = "request"


class DependencyType(Enum):
    """Types of dependencies"""
    SERVICE = "service"
    CONFIGURATION = "configuration"
    AGENT = "agent"
    UTILITY = "utility"


@dataclass
class DependencyDefinition:
    """Definition of a dependency"""
    name: str
    dependency_type: DependencyType
    scope: DependencyScope
    factory: Callable
    dependencies: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.now)


class DependencyResolver:
    """Dependency injection container and resolver"""
    
    def __init__(self, logger: logging.Logger):
        self.logger = logger
        self._definitions: Dict[str, DependencyDefinition] = {}
        self._singletons: Dict[str, Any] = {}
        self._request_scope_cache: Dict[str, Any] = {}
        self._agent_registry = get_agent_registry()
        self._resolving: set = set()  # Prevent circular dependencies
        
    def register_service(self, name: str, factory: Callable, 
                        scope: DependencyScope = DependencyScope.SINGLETON,
                        dependencies: Optional[List[str]] = None) -> bool:
        """Register a service dependency"""
        try:
            # Analyze factory function to extract dependencies
            if dependencies is None:
                dependencies = self._extract_dependencies(factory)
            
            definition = DependencyDefinition(
                name=name,
                dependency_type=DependencyType.SERVICE,
                scope=scope,
                factory=factory,
                dependencies=dependencies
            )
            
            self._definitions[name] = definition
            self.logger.info(f"Registered service '{name}' with scope {scope.value}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to register service '{name}': {e}")
            return False
    
    def register_configuration(self, name: str, config: Dict[str, Any]) -> bool:
        """Register a configuration dependency"""
        try:
            definition = DependencyDefinition(
                name=name,
                dependency_type=DependencyType.CONFIGURATION,
                scope=DependencyScope.SINGLETON,
                factory=lambda: config,
                dependencies=[]
            )
            
            self._definitions[name] = definition
            self.logger.info(f"Registered configuration '{name}'")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to register configuration '{name}': {e}")
            return False
    
    def register_agent(self, agent_name: str, agent_factory: Callable,
                      dependencies: Optional[List[str]] = None) -> bool:
        """Register an agent dependency"""
        try:
            if dependencies is None:
                dependencies = self._extract_dependencies(agent_factory)
            
            definition = DependencyDefinition(
                name=agent_name,
                dependency_type=DependencyType.AGENT,
                scope=DependencyScope.SINGLETON,
                factory=agent_factory,
                dependencies=dependencies
            )
            
            self._definitions[agent_name] = definition
            self.logger.info(f"Registered agent '{agent_name}'")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to register agent '{agent_name}': {e}")
            return False
    
    def resolve(self, name: str) -> Any:
        """Resolve a dependency by name"""
        if name in self._resolving:
            raise CircularDependencyError(f"Circular dependency detected for '{name}'")
        
        try:
            definition = self._definitions.get(name)
            if not definition:
                raise DependencyNotFoundError(f"Dependency '{name}' not found")
            
            # Check if already resolved based on scope
            if definition.scope == DependencyScope.SINGLETON:
                if name in self._singletons:
                    return self._singletons[name]
            elif definition.scope == DependencyScope.REQUEST:
                if name in self._request_scope_cache:
                    return self._request_scope_cache[name]
            
            # Resolve dependencies
            self._resolving.add(name)
            resolved_dependencies = {}
            
            for dep_name in definition.dependencies:
                resolved_dependencies[dep_name] = self.resolve(dep_name)
            
            # Create instance
            if definition.dependency_type == DependencyType.CONFIGURATION:
                instance = definition.factory()
            else:
                # For services and agents, pass resolved dependencies
                instance = definition.factory(**resolved_dependencies)
            
            # Store based on scope
            if definition.scope == DependencyScope.SINGLETON:
                self._singletons[name] = instance
            elif definition.scope == DependencyScope.REQUEST:
                self._request_scope_cache[name] = instance
            
            # Register agent in registry if it's an agent
            if (definition.dependency_type == DependencyType.AGENT and 
                isinstance(instance, AgentInterface)):
                self._agent_registry.register_agent(instance)
            
            self._resolving.remove(name)
            self.logger.debug(f"Resolved dependency '{name}'")
            return instance
            
        except Exception as e:
            self._resolving.discard(name)
            self.logger.error(f"Failed to resolve dependency '{name}': {e}")
            raise
    
    def resolve_agent(self, agent_name: str) -> Optional[AgentInterface]:
        """Resolve an agent dependency"""
        try:
            instance = self.resolve(agent_name)
            if isinstance(instance, AgentInterface):
                return instance
            else:
                self.logger.error(f"Resolved instance for '{agent_name}' is not an AgentInterface")
                return None
        except Exception as e:
            self.logger.error(f"Failed to resolve agent '{agent_name}': {e}")
            return None
    
    def resolve_by_capability(self, capability: str) -> List[AgentInterface]:
        """Resolve agents by capability"""
        try:
            # First try to get from registry
            from agent.interfaces import AgentCapability
            try:
                agent_capability = AgentCapability(capability)
                return self._agent_registry.get_agents_with_capability(agent_capability)
            except ValueError:
                # Fallback to string-based capability matching
                agents = []
                for agent in self._agent_registry.get_all_agents():
                    if capability in [c.value for c in agent.capabilities]:
                        agents.append(agent)
                return agents
        except Exception as e:
            self.logger.error(f"Failed to resolve agents by capability '{capability}': {e}")
            return []
    
    def clear_request_scope(self):
        """Clear request-scoped dependencies"""
        self._request_scope_cache.clear()
        self.logger.debug("Cleared request scope cache")
    
    def _extract_dependencies(self, factory: Callable) -> List[str]:
        """Extract dependency names from factory function signature"""
        try:
            sig = inspect.signature(factory)
            dependencies = []
            
            for param_name, param in sig.parameters.items():
                # Skip self, cls, and other special parameters
                if param_name in ['self', 'cls'] or param_name.startswith('_'):
                    continue
                
                # Skip parameters with default values that are not dependencies
                if param.default is not inspect.Parameter.empty:
                    continue
                
                dependencies.append(param_name)
            
            return dependencies
            
        except Exception as e:
            self.logger.warning(f"Could not extract dependencies from factory: {e}")
            return []
    
    def get_registered_dependencies(self) -> Dict[str, DependencyDefinition]:
        """Get all registered dependencies"""
        return self._definitions.copy()
    
    def is_registered(self, name: str) -> bool:
        """Check if a dependency is registered"""
        return name in self._definitions


class CircularDependencyError(Exception):
    """Raised when a circular dependency is detected"""
    pass


class DependencyNotFoundError(Exception):
    """Raised when a dependency is not found"""
    pass


class AgentFactory:
    """Factory for creating and configuring agents with dependency injection"""
    
    def __init__(self, resolver: DependencyResolver, logger: logging.Logger):
        self.resolver = resolver
        self.logger = logger
    
    def create_agent(self, agent_type: str, config: Dict[str, Any]) -> Optional[AgentInterface]:
        """Create an agent with dependency injection"""
        try:
            # Resolve the agent
            agent = self.resolver.resolve_agent(agent_type)
            if not agent:
                self.logger.error(f"Failed to resolve agent '{agent_type}'")
                return None
            
            # Initialize the agent with configuration
            if not asyncio.iscoroutinefunction(agent.initialize):
                # Handle synchronous initialization
                success = agent.initialize(config)
            else:
                # Handle asynchronous initialization
                loop = asyncio.get_event_loop()
                if loop.is_running():
                    # Create a new task for async initialization
                    task = asyncio.create_task(agent.initialize(config))
                    success = loop.run_until_complete(task)
                else:
                    success = loop.run_until_complete(agent.initialize(config))
            
            if not success:
                self.logger.error(f"Failed to initialize agent '{agent_type}'")
                return None
            
            self.logger.info(f"Successfully created and initialized agent '{agent_type}'")
            return agent
            
        except Exception as e:
            self.logger.error(f"Failed to create agent '{agent_type}': {e}")
            return None
    
    def create_agents_by_capability(self, capability: str, config: Dict[str, Any]) -> List[AgentInterface]:
        """Create multiple agents with a specific capability"""
        try:
            agents = self.resolver.resolve_by_capability(capability)
            initialized_agents = []
            
            for agent in agents:
                try:
                    if not asyncio.iscoroutinefunction(agent.initialize):
                        success = agent.initialize(config)
                    else:
                        loop = asyncio.get_event_loop()
                        if loop.is_running():
                            task = asyncio.create_task(agent.initialize(config))
                            success = loop.run_until_complete(task)
                        else:
                            success = loop.run_until_complete(agent.initialize(config))
                    
                    if success:
                        initialized_agents.append(agent)
                    else:
                        self.logger.warning(f"Failed to initialize agent '{agent.name}'")
                        
                except Exception as e:
                    self.logger.error(f"Failed to initialize agent '{agent.name}': {e}")
            
            self.logger.info(f"Created {len(initialized_agents)} agents with capability '{capability}'")
            return initialized_agents
            
        except Exception as e:
            self.logger.error(f"Failed to create agents by capability '{capability}': {e}")
            return []


# Global dependency resolver instance
_dependency_resolver = None

def get_dependency_resolver() -> DependencyResolver:
    """Get the global dependency resolver instance"""
    global _dependency_resolver
    if _dependency_resolver is None:
        logger = logging.getLogger(__name__)
        _dependency_resolver = DependencyResolver(logger)
    return _dependency_resolver 