"""
Config Manager - Centralized configuration access with caching
"""

from typing import Dict, Any, Optional
import os
from hephaestus.utils.config_loader import load_config


class ConfigManager:
    """Centralized configuration manager with caching and hot reload support."""
    
    _instance: Optional['ConfigManager'] = None
    _config_cache: Dict[str, Any] = {}
    _config_loaded = False
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    @classmethod
    def _ensure_config_loaded(cls):
        """Ensure configuration is loaded."""
        if not cls._config_loaded:
            cls.reload_config()
    
    @classmethod
    def get_agent_config(cls, agent_name: str) -> Dict[str, Any]:
        """
        Get agent-specific configuration with fallback to defaults.
        
        Args:
            agent_name: Name of the agent (e.g., "ArchitectAgent")
            
        Returns:
            Agent configuration dictionary
        """
        cls._ensure_config_loaded()
        
        cache_key = f"agent_{agent_name}"
        if cache_key in cls._config_cache:
            return cls._config_cache[cache_key]
        
        # Load base config
        base_config = cls._config_cache.get('base', {})
        
        # Get agent-specific overrides
        agents_config = base_config.get('agents', {})
        agent_config = agents_config.get(agent_name, {})
        
        # Merge with defaults
        default_agent_config = {
            'model_type': 'architect_default',
            'temperature': 0.4,
            'max_retries': 3,
            'timeout': 60,
            'cache_enabled': True,
            'metrics_enabled': True,
        }
        
        merged_config = {**default_agent_config, **agent_config}
        
        # Cache result
        cls._config_cache[cache_key] = merged_config
        return merged_config
    
    @classmethod
    def get_model_config(cls, model_type: str) -> Dict[str, Any]:
        """
        Get model configuration with fallback handling.
        
        Args:
            model_type: Type of model (e.g., "architect_default")
            
        Returns:
            Model configuration dictionary
        """
        cls._ensure_config_loaded()
        
        cache_key = f"model_{model_type}"
        if cache_key in cls._config_cache:
            return cls._config_cache[cache_key]
        
        base_config = cls._config_cache.get('base', {})
        models_config = base_config.get('models', {})
        
        # Get specific model config
        model_config = models_config.get(model_type, {})
        
        # Fallback to default if not found
        if not model_config and model_type != 'default':
            model_config = models_config.get('architect_default', {})
        
        # Ensure model_config is a dict
        if not isinstance(model_config, dict):
            model_config = {}
        
        # Add default model settings
        default_model_config = {
            'temperature': 0.4,
            'max_tokens': 4096,
            'timeout': 60,
        }
        
        merged_config = {**default_model_config, **model_config}
        
        # Cache result
        cls._config_cache[cache_key] = merged_config
        return merged_config
    
    @classmethod
    def get_service_config(cls, service_name: str) -> Dict[str, Any]:
        """
        Get service-specific configuration.
        
        Args:
            service_name: Name of the service (e.g., "monitoring", "validation")
            
        Returns:
            Service configuration dictionary
        """
        cls._ensure_config_loaded()
        
        cache_key = f"service_{service_name}"
        if cache_key in cls._config_cache:
            return cls._config_cache[cache_key]
        
        base_config = cls._config_cache.get('base', {})
        services_config = base_config.get('services', {})
        service_config = services_config.get(service_name, {})
        
        # Add default service settings
        default_service_config = {
            'enabled': True,
            'timeout': 30,
            'retry_count': 3,
        }
        
        merged_config = {**default_service_config, **service_config}
        
        # Cache result
        cls._config_cache[cache_key] = merged_config
        return merged_config
    
    @classmethod
    def get_config_value(cls, key: str, default: Any = None) -> Any:
        """
        Get a specific configuration value using dot notation.
        
        Args:
            key: Configuration key in dot notation (e.g., "monitoring.refresh_interval")
            default: Default value if key is not found
            
        Returns:
            Configuration value or default
        """
        cls._ensure_config_loaded()
        
        # Split key by dots
        keys = key.split('.')
        
        # Start with base config
        value = cls._config_cache.get('base', {})
        
        # Navigate through the key path
        try:
            for k in keys:
                value = value[k]
            return value
        except (KeyError, TypeError):
            return default
    
    @classmethod
    def get_full_config(cls) -> Dict[str, Any]:
        """Get the full configuration."""
        cls._ensure_config_loaded()
        return cls._config_cache.get('base', {})
    
    @classmethod
    def reload_config(cls):
        """Reload configuration from files."""
        try:
            # Load fresh config
            config = load_config()
            
            # Clear cache and reload
            cls._config_cache.clear()
            cls._config_cache['base'] = config
            cls._config_loaded = True
            
        except Exception as e:
            # If reload fails, keep existing config
            if not cls._config_loaded:
                # First load failed, set empty config
                cls._config_cache['base'] = {}
                cls._config_loaded = True
            
            # You might want to log this error
            print(f"Warning: Failed to reload config: {e}")
    
    @classmethod
    def get_env_config(cls, key: str, default: Any = None) -> Any:
        """
        Get configuration value from environment or config file.
        
        Args:
            key: Environment variable name
            default: Default value if not found
            
        Returns:
            Configuration value
        """
        # Check environment first
        env_value = os.getenv(key)
        if env_value is not None:
            return env_value
        
        # Check config file
        cls._ensure_config_loaded()
        base_config = cls._config_cache.get('base', {})
        
        # Support dot notation (e.g., "api.port")
        keys = key.lower().split('.')
        value = base_config
        
        try:
            for k in keys:
                value = value[k]
            return value
        except (KeyError, TypeError):
            return default
    
    @classmethod
    def update_config(cls, key: str, value: Any) -> None:
        """
        Update a configuration value at runtime.
        
        Args:
            key: Configuration key (supports dot notation)
            value: New value
        """
        cls._ensure_config_loaded()
        
        # Support dot notation
        keys = key.split('.')
        config = cls._config_cache['base']
        
        # Navigate to parent
        for k in keys[:-1]:
            if k not in config:
                config[k] = {}
            config = config[k]
        
        # Set value
        config[keys[-1]] = value
        
        # Clear related cache entries
        cache_keys_to_clear = [k for k in cls._config_cache.keys() if k.startswith(keys[0])]
        for k in cache_keys_to_clear:
            if k != 'base':
                cls._config_cache.pop(k, None)