"""
Performance Package - Agente Autônomo v2.8.1
Provides performance optimization and caching utilities.
"""

from .config_cache import ConfigCache, get_config_cache, cached_config

__all__ = [
    "ConfigCache",
    "get_config_cache",
    "cached_config"
] 