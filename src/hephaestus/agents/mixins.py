"""
Agent Mixins - Reusable components for agent functionality
"""

from typing import Dict, Any, Optional
from abc import ABC
import logging

from hephaestus.utils.config_manager import ConfigManager
from hephaestus.utils.logger_factory import LoggerFactory
from hephaestus.utils.metrics_collector import get_global_metrics_collector
from hephaestus.utils.intelligent_cache import IntelligentCache


class ConfigMixin:
    """Mixin for standardized configuration access."""
    
    def get_agent_config(self) -> Dict[str, Any]:
        """Get configuration for this agent."""
        agent_name = self.__class__.__name__
        return ConfigManager.get_agent_config(agent_name)
    
    def get_model_config(self) -> Dict[str, Any]:
        """Get model configuration for this agent."""
        agent_config = self.get_agent_config()
        model_type = agent_config.get('model_type', 'default')
        return ConfigManager.get_model_config(model_type)
    
    def get_config_value(self, key: str, default: Any = None) -> Any:
        """Get a specific configuration value with fallback."""
        agent_config = self.get_agent_config()
        
        # Support dot notation (e.g., "retry.max_attempts")
        keys = key.split('.')
        value = agent_config
        
        try:
            for k in keys:
                value = value[k]
            return value
        except (KeyError, TypeError):
            return default
    
    def update_config(self, key: str, value: Any):
        """Update a configuration value at runtime."""
        agent_name = self.__class__.__name__
        ConfigManager.update_config(f"agents.{agent_name}.{key}", value)


class LoggerMixin:
    """Mixin for standardized logger setup."""
    
    def setup_logger(self, name: Optional[str] = None, parent_logger: Optional[logging.Logger] = None):
        """Setup logger for this component."""
        component_name = name or self.__class__.__name__
        self.logger = LoggerFactory.get_component_logger(component_name, parent_logger)
    
    def get_agent_logger(self) -> logging.Logger:
        """Get agent-specific logger."""
        agent_name = self.__class__.__name__
        return LoggerFactory.get_agent_logger(agent_name)
    
    def log_operation(self, operation: str, level: int = logging.INFO, **kwargs):
        """Log an operation with standardized format."""
        if hasattr(self, 'logger'):
            extra_info = " ".join([f"{k}={v}" for k, v in kwargs.items()])
            message = f"{operation}"
            if extra_info:
                message += f" ({extra_info})"
            self.logger.log(level, message)


class MetricsMixin:
    """Mixin for standardized metrics collection."""
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.metrics_collector = get_global_metrics_collector()
    
    def record_metric(self, metric_name: str, value: Any, tags: Optional[Dict[str, str]] = None):
        """Record a metric for this agent."""
        agent_name = self.__class__.__name__
        self.metrics_collector.record_service_metric(agent_name, metric_name, value, tags)
    
    def record_operation(self, operation: str, duration: float, success: bool, metadata: Optional[Dict[str, Any]] = None):
        """Record an operation metric."""
        agent_name = self.__class__.__name__
        self.metrics_collector.record_agent_performance(
            agent_name=agent_name,
            operation=operation,
            duration=duration,
            success=success,
            metadata=metadata
        )
    
    def get_agent_metrics(self) -> Dict[str, Any]:
        """Get metrics dashboard for this agent."""
        agent_name = self.__class__.__name__
        return self.metrics_collector.get_agent_dashboard(agent_name)


class CacheMixin:
    """Mixin for standardized caching functionality."""
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Each agent gets its own cache namespace
        agent_name = self.__class__.__name__
        self._cache = IntelligentCache(max_size=100, default_ttl=3600)
        self._cache_prefix = f"{agent_name}:"
    
    def get_cached_result(self, cache_key: str) -> Optional[Any]:
        """Get a cached result."""
        full_key = f"{self._cache_prefix}{cache_key}"
        return self._cache.get(full_key)
    
    def set_cached_result(self, cache_key: str, value: Any, ttl: Optional[int] = None):
        """Set a cached result."""
        full_key = f"{self._cache_prefix}{cache_key}"
        self._cache.set(full_key, value, ttl)
    
    def invalidate_cache(self, cache_key: Optional[str] = None):
        """Invalidate cache entries."""
        if cache_key:
            full_key = f"{self._cache_prefix}{cache_key}"
            self._cache.delete(full_key)
        else:
            # Clear all cache entries for this agent
            self._cache.clear()
    
    def get_cache_stats(self) -> Dict[str, Any]:
        """Get cache statistics."""
        return {
            'cache_size': len(self._cache.cache),
            'max_size': self._cache.max_size,
            'prefix': self._cache_prefix,
        }


class ValidationMixin:
    """Mixin for common validation functionality."""
    
    def validate_required_params(self, params: Dict[str, Any], required: list) -> Optional[str]:
        """Validate that required parameters are present."""
        missing = [param for param in required if param not in params or params[param] is None]
        if missing:
            return f"Missing required parameters: {', '.join(missing)}"
        return None
    
    def validate_param_types(self, params: Dict[str, Any], type_specs: Dict[str, type]) -> Optional[str]:
        """Validate parameter types."""
        for param, expected_type in type_specs.items():
            if param in params and not isinstance(params[param], expected_type):
                return f"Parameter '{param}' must be of type {expected_type.__name__}, got {type(params[param]).__name__}"
        return None
    
    def sanitize_string(self, value: str, max_length: int = 10000) -> str:
        """Sanitize string input."""
        if not isinstance(value, str):
            raise ValueError(f"Expected string, got {type(value)}")
        
        # Truncate if too long
        if len(value) > max_length:
            value = value[:max_length]
        
        # Remove null bytes and other problematic characters
        value = value.replace('\x00', '').strip()
        
        return value


class ErrorHandlingMixin:
    """Mixin for standardized error handling."""
    
    def handle_error(self, error: Exception, operation: str, context: Optional[Dict[str, Any]] = None) -> str:
        """Handle an error with standardized logging and metrics."""
        error_message = f"{operation} failed: {str(error)}"
        
        # Log the error
        if hasattr(self, 'logger'):
            self.logger.error(error_message, exc_info=True)
        
        # Record metric if available
        if hasattr(self, 'record_operation'):
            self.record_operation(operation, 0.0, False, {
                'error': str(error),
                'error_type': error.__class__.__name__,
                'context': context or {}
            })
        
        return error_message
    
    def safe_execute(self, operation_name: str, func, *args, **kwargs):
        """Safely execute a function with error handling."""
        import time
        start_time = time.time()
        
        try:
            result = func(*args, **kwargs)
            duration = time.time() - start_time
            
            # Record success
            if hasattr(self, 'record_operation'):
                self.record_operation(operation_name, duration, True)
            
            return result, None
            
        except Exception as e:
            duration = time.time() - start_time
            error_message = self.handle_error(e, operation_name)
            return None, error_message


class EnhancedAgentMixin(ConfigMixin, LoggerMixin, MetricsMixin, CacheMixin, ValidationMixin, ErrorHandlingMixin):
    """Combined mixin with all agent enhancements."""
    
    def __init__(self, agent_name: Optional[str] = None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Setup logger first
        self.setup_logger(agent_name or self.__class__.__name__)
        
        # Log initialization
        self.logger.info(f"Initializing {self.__class__.__name__} with enhanced capabilities")
        
        # Cache agent config for quick access
        self._agent_config = self.get_agent_config()
        self._model_config = self.get_model_config()
    
    def get_status(self) -> Dict[str, Any]:
        """Get comprehensive status of this agent."""
        return {
            'agent_name': self.__class__.__name__,
            'config': self._agent_config,
            'model_config': self._model_config,
            'metrics': self.get_agent_metrics(),
            'cache_stats': self.get_cache_stats(),
        }
    
    def reload_config(self):
        """Reload configuration and update cached values."""
        ConfigManager.reload_config()
        self._agent_config = self.get_agent_config()
        self._model_config = self.get_model_config()
        self.logger.info("Configuration reloaded")


# Backwards compatibility aliases
AgentMixin = EnhancedAgentMixin