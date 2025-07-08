"""
Enhanced Base Agent - Modern base class with all mixins and utilities
"""

import asyncio
import time
from typing import Dict, Any, Optional, Tuple
from abc import ABC, abstractmethod

from hephaestus.agents.base import BaseAgent
from hephaestus.agents.mixins import EnhancedAgentMixin
from hephaestus.utils.llm_manager import LLMCallManager, llm_call_with_metrics, llm_call_with_retry


class EnhancedBaseAgent(EnhancedAgentMixin, BaseAgent, ABC):
    """
    Enhanced base agent with all modern capabilities:
    - Dependency injection
    - Automatic logger setup
    - Metrics collection
    - Caching
    - Configuration management
    - Standardized LLM calls
    """
    
    def __init__(self, agent_name: Optional[str] = None, **kwargs):
        """
        Initialize enhanced agent with automatic setup.
        
        Args:
            agent_name: Name of the agent (defaults to class name)
            **kwargs: Additional initialization parameters
        """
        # Initialize base classes
        agent_name = agent_name or self.__class__.__name__
        
        # Filter kwargs for BaseAgent (only accepts logger)
        base_kwargs = {k: v for k, v in kwargs.items() if k == 'logger'}
        
        # Initialize with proper MRO using super()
        super().__init__(
            name=agent_name,
            capabilities=self.get_default_capabilities(),
            **base_kwargs
        )
        
        # Override BaseAgent logger with enhanced logger
        self.logger = self.get_agent_logger()
        
        # Setup LLM manager
        self._setup_llm_manager()
        
        # Register with monitoring dashboard
        self._register_with_dashboard()
        
        # Log successful initialization
        self.logger.info(f"Enhanced {agent_name} initialized successfully")
    
    def _setup_llm_manager(self):
        """Setup LLM manager with agent configuration."""
        model_config = self.get_model_config()
        self.llm_manager = LLMCallManager(model_config, self.logger)
        
        self.logger.debug(f"LLM Manager initialized with model: {model_config}")
    
    def _register_with_dashboard(self):
        """Register this agent with the monitoring dashboard."""
        try:
            from hephaestus.monitoring import get_unified_dashboard
            dashboard = get_unified_dashboard()
            dashboard.register_agent(self.name, "enhanced")
        except Exception as e:
            self.logger.debug(f"Could not register with dashboard: {e}")
    
    @abstractmethod
    def get_default_capabilities(self) -> list:
        """Get default capabilities for this agent type."""
        pass
    
    @llm_call_with_metrics
    async def llm_call(self, prompt: str, **kwargs) -> Tuple[Optional[str], Optional[str]]:
        """
        Make an LLM call with automatic metrics and retry.
        
        Args:
            prompt: The prompt to send to the LLM
            **kwargs: Additional parameters for LLM call
            
        Returns:
            Tuple of (response, error_message)
        """
        # Get agent-specific settings
        config = self.get_agent_config()
        
        # Merge with kwargs
        call_params = {
            'temperature': config.get('temperature', 0.4),
            'max_retries': config.get('max_retries', 3),
            'fallback_models': config.get('fallback_models', []),
            **kwargs
        }
        
        return await self.llm_manager.safe_call_with_retry(prompt, **call_params)
    
    @llm_call_with_metrics  
    async def llm_call_json(self, prompt: str, **kwargs) -> Tuple[Optional[Dict[str, Any]], Optional[str]]:
        """
        Make an LLM call expecting a JSON response.
        
        Args:
            prompt: The prompt to send to the LLM
            **kwargs: Additional parameters for LLM call
            
        Returns:
            Tuple of (parsed_json, error_message)
        """
        # Get agent-specific settings
        config = self.get_agent_config()
        
        # Merge with kwargs
        call_params = {
            'temperature': config.get('temperature', 0.4),
            'max_retries': config.get('max_retries', 3),
            'fallback_models': config.get('fallback_models', []),
            **kwargs
        }
        
        return await self.llm_manager.call_with_json_response(prompt, **call_params)
    
    async def execute_with_metrics(self, operation_name: str, operation_func, *args, **kwargs):
        """
        Execute an operation with automatic metrics collection.
        
        Args:
            operation_name: Name of the operation for metrics
            operation_func: Function to execute
            *args, **kwargs: Arguments for the function
            
        Returns:
            Result of the operation
        """
        start_time = time.time()
        
        try:
            if asyncio.iscoroutinefunction(operation_func):
                result = await operation_func(*args, **kwargs)
            else:
                result = operation_func(*args, **kwargs)
            
            duration = time.time() - start_time
            self.record_operation(operation_name, duration, True)
            
            return result
            
        except Exception as e:
            duration = time.time() - start_time
            error_message = self.handle_error(e, operation_name)
            self.record_operation(operation_name, duration, False, {'error': error_message})
            raise
    
    def get_enhanced_status(self) -> Dict[str, Any]:
        """Get comprehensive enhanced status."""
        base_status = self.get_status()  # From BaseAgent
        enhanced_status = EnhancedAgentMixin.get_status(self)  # From mixin
        
        # Merge statuses
        return {
            **base_status,
            **enhanced_status,
            'llm_manager_stats': self.llm_manager.get_cache_stats() if hasattr(self, 'llm_manager') else {},
            'enhanced_features': {
                'metrics_enabled': True,
                'caching_enabled': True,
                'auto_retry_enabled': True,
                'config_hot_reload': True,
            }
        }
    
    async def validate_and_execute(self, 
                                 operation_name: str,
                                 params: Dict[str, Any],
                                 required_params: list,
                                 operation_func,
                                 *args, **kwargs):
        """
        Validate parameters and execute operation with full error handling.
        
        Args:
            operation_name: Name of the operation
            params: Parameters to validate
            required_params: List of required parameter names
            operation_func: Function to execute after validation
            *args, **kwargs: Arguments for the operation function
            
        Returns:
            Tuple of (result, error_message)
        """
        # Validate required parameters
        validation_error = self.validate_required_params(params, required_params)
        if validation_error:
            self.logger.error(f"{operation_name}: {validation_error}")
            return None, validation_error
        
        # Execute with metrics
        try:
            result = await self.execute_with_metrics(operation_name, operation_func, *args, **kwargs)
            return result, None
        except Exception as e:
            return None, str(e)
    
    async def cached_operation(self, 
                             cache_key: str,
                             operation_func,
                             ttl: Optional[int] = None,
                             *args, **kwargs):
        """
        Execute operation with caching.
        
        Args:
            cache_key: Key for caching the result
            operation_func: Function to execute
            ttl: Time to live for cache entry
            *args, **kwargs: Arguments for the operation function
            
        Returns:
            Result of the operation (from cache or fresh execution)
        """
        # Check cache first
        cached_result = self.get_cached_result(cache_key)
        if cached_result is not None:
            self.logger.debug(f"Cache hit for key: {cache_key}")
            return cached_result
        
        # Execute operation
        if asyncio.iscoroutinefunction(operation_func):
            result = await operation_func(*args, **kwargs)
        else:
            result = operation_func(*args, **kwargs)
        
        # Cache result
        self.set_cached_result(cache_key, result, ttl)
        self.logger.debug(f"Cached result for key: {cache_key}")
        
        return result


class SimpleEnhancedAgent(EnhancedBaseAgent):
    """Simple enhanced agent for testing purposes."""
    
    def get_default_capabilities(self) -> list:
        return ['basic_operations']
    
    async def execute(self, objective: str) -> Tuple[bool, Optional[str]]:
        """Simple execute implementation for testing."""
        self.logger.info(f"Executing: {objective}")
        return True, None