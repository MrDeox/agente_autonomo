"""
Configuration Cache - Agente Autônomo v2.8.1
Implements intelligent caching for configuration to reduce memory allocations and improve performance.
"""

import logging
import threading
import time
import hashlib
import json
from typing import Dict, Any, Optional, List, Tuple
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from pathlib import Path
import weakref
from functools import lru_cache

from agent.utils.intelligent_cache import IntelligentCache


@dataclass
class ConfigCacheEntry:
    """Configuration cache entry"""
    config_hash: str
    config_data: Dict[str, Any]
    created_at: datetime
    last_accessed: datetime
    access_count: int = 0
    size_bytes: int = 0
    dependencies: List[str] = field(default_factory=list)
    is_valid: bool = True


class ConfigCache:
    """Intelligent configuration cache with memory management"""
    
    def __init__(self, max_size_mb: int = 100, logger: logging.Logger = None):
        self.logger = logger or logging.getLogger(__name__)
        self.max_size_bytes = max_size_mb * 1024 * 1024
        self.current_size_bytes = 0
        
        # Thread-safe cache storage
        self._cache: Dict[str, ConfigCacheEntry] = {}
        self._cache_lock = threading.RLock()
        
        # File watchers for config changes
        self._file_watchers: Dict[str, float] = {}
        self._watcher_lock = threading.RLock()
        
        # Performance metrics
        self._metrics = {
            "hits": 0,
            "misses": 0,
            "evictions": 0,
            "total_requests": 0
        }
        self._metrics_lock = threading.RLock()
        
        # LRU cache for frequently accessed configs
        self._lru_cache = IntelligentCache(max_size=100, default_ttl=3600)
        
        self.logger.info(f"🔧 ConfigCache initialized with {max_size_mb}MB limit")
    
    def get_config(self, config_path: str, force_reload: bool = False) -> Optional[Dict[str, Any]]:
        """Get configuration from cache or load from file"""
        try:
            self._update_metrics("total_requests")
            
            if force_reload:
                return self._load_and_cache_config(config_path)
            
            # Check LRU cache first
            lru_key = f"lru_{config_path}"
            cached_config = self._lru_cache.get(lru_key)
            if cached_config:
                self._update_metrics("hits")
                return cached_config
            
            # Check main cache
            with self._cache_lock:
                if config_path in self._cache:
                    entry = self._cache[config_path]
                    if self._is_entry_valid(entry, config_path):
                        # Update access info
                        entry.last_accessed = datetime.now()
                        entry.access_count += 1
                        
                        # Move to LRU cache for faster access
                        self._lru_cache.set(lru_key, entry.config_data)
                        
                        self._update_metrics("hits")
                        return entry.config_data
                    else:
                        # Entry is invalid, remove it
                        self._remove_entry(config_path)
            
            # Load and cache config
            return self._load_and_cache_config(config_path)
            
        except Exception as e:
            self.logger.error(f"Error getting config for {config_path}: {e}")
            return None
    
    def _load_and_cache_config(self, config_path: str) -> Optional[Dict[str, Any]]:
        """Load configuration from file and cache it"""
        try:
            # Load config from file
            config_data = self._load_config_file(config_path)
            if not config_data:
                self._update_metrics("misses")
                return None
            
            # Calculate config hash and size
            config_hash = self._calculate_config_hash(config_data)
            size_bytes = self._calculate_config_size(config_data)
            
            # Check if we need to evict entries
            self._ensure_cache_space(size_bytes)
            
            # Create cache entry
            entry = ConfigCacheEntry(
                config_hash=config_hash,
                config_data=config_data,
                created_at=datetime.now(),
                last_accessed=datetime.now(),
                access_count=1,
                size_bytes=size_bytes,
                dependencies=self._extract_dependencies(config_data)
            )
            
            # Store in cache
            with self._cache_lock:
                self._cache[config_path] = entry
                self.current_size_bytes += size_bytes
            
            # Store in LRU cache
            lru_key = f"lru_{config_path}"
            self._lru_cache.set(lru_key, config_data)
            
            # Update file watcher
            self._update_file_watcher(config_path)
            
            self.logger.debug(f"Cached config {config_path} ({size_bytes} bytes)")
            return config_data
            
        except Exception as e:
            self.logger.error(f"Error loading config {config_path}: {e}")
            return None
    
    def _load_config_file(self, config_path: str) -> Optional[Dict[str, Any]]:
        """Load configuration from file"""
        try:
            import yaml
            
            path = Path(config_path)
            if not path.exists():
                self.logger.warning(f"Config file not found: {config_path}")
                return None
            
            with open(path, 'r', encoding='utf-8') as f:
                if path.suffix.lower() in ['.yaml', '.yml']:
                    return yaml.safe_load(f)
                elif path.suffix.lower() == '.json':
                    return json.load(f)
                else:
                    # Try YAML first, then JSON
                    try:
                        f.seek(0)
                        return yaml.safe_load(f)
                    except:
                        f.seek(0)
                        return json.load(f)
                        
        except Exception as e:
            self.logger.error(f"Error loading config file {config_path}: {e}")
            return None
    
    def _calculate_config_hash(self, config_data: Dict[str, Any]) -> str:
        """Calculate hash of configuration data"""
        try:
            config_str = json.dumps(config_data, sort_keys=True)
            return hashlib.sha256(config_str.encode()).hexdigest()
        except Exception:
            return str(hash(str(config_data)))
    
    def _calculate_config_size(self, config_data: Dict[str, Any]) -> int:
        """Calculate approximate size of configuration data in bytes"""
        try:
            config_str = json.dumps(config_data)
            return len(config_str.encode('utf-8'))
        except Exception:
            return 1024  # Default size estimate
    
    def _extract_dependencies(self, config_data: Dict[str, Any]) -> List[str]:
        """Extract file dependencies from configuration"""
        dependencies = []
        
        def extract_paths(obj, path=""):
            if isinstance(obj, dict):
                for key, value in obj.items():
                    current_path = f"{path}.{key}" if path else key
                    if isinstance(value, str) and any(ext in value.lower() for ext in ['.yaml', '.yml', '.json']):
                        dependencies.append(value)
                    elif isinstance(value, (dict, list)):
                        extract_paths(value, current_path)
            elif isinstance(obj, list):
                for i, item in enumerate(obj):
                    current_path = f"{path}[{i}]"
                    if isinstance(item, str) and any(ext in item.lower() for ext in ['.yaml', '.yml', '.json']):
                        dependencies.append(item)
                    elif isinstance(item, (dict, list)):
                        extract_paths(item, current_path)
        
        extract_paths(config_data)
        return dependencies
    
    def _is_entry_valid(self, entry: ConfigCacheEntry, config_path: str) -> bool:
        """Check if cache entry is still valid"""
        try:
            # Check if file has been modified
            path = Path(config_path)
            if not path.exists():
                return False
            
            file_mtime = path.stat().st_mtime
            if config_path in self._file_watchers:
                if file_mtime > self._file_watchers[config_path]:
                    return False
            
            # Check dependencies
            for dep_path in entry.dependencies:
                dep_path_obj = Path(dep_path)
                if dep_path_obj.exists():
                    dep_mtime = dep_path_obj.stat().st_mtime
                    if dep_path in self._file_watchers:
                        if dep_mtime > self._file_watchers[dep_path]:
                            return False
            
            return True
            
        except Exception as e:
            self.logger.error(f"Error checking entry validity: {e}")
            return False
    
    def _update_file_watcher(self, config_path: str):
        """Update file modification time watcher"""
        try:
            path = Path(config_path)
            if path.exists():
                with self._watcher_lock:
                    self._file_watchers[config_path] = path.stat().st_mtime
        except Exception as e:
            self.logger.error(f"Error updating file watcher: {e}")
    
    def _ensure_cache_space(self, required_bytes: int):
        """Ensure there's enough space in cache"""
        try:
            while self.current_size_bytes + required_bytes > self.max_size_bytes:
                # Find least recently used entry
                lru_entry = None
                lru_path = None
                oldest_access = datetime.now()
                
                with self._cache_lock:
                    for path, entry in self._cache.items():
                        if entry.last_accessed < oldest_access:
                            oldest_access = entry.last_accessed
                            lru_entry = entry
                            lru_path = path
                
                if lru_entry and lru_path:
                    self._remove_entry(lru_path)
                else:
                    # No entries to evict, but still not enough space
                    self.logger.warning("Cache full but no entries to evict")
                    break
                    
        except Exception as e:
            self.logger.error(f"Error ensuring cache space: {e}")
    
    def _remove_entry(self, config_path: str):
        """Remove entry from cache"""
        try:
            with self._cache_lock:
                if config_path in self._cache:
                    entry = self._cache[config_path]
                    self.current_size_bytes -= entry.size_bytes
                    del self._cache[config_path]
                    
                    # Remove from LRU cache
                    lru_key = f"lru_{config_path}"
                    self._lru_cache.delete(lru_key)
                    
                    self._update_metrics("evictions")
                    self.logger.debug(f"Evicted config {config_path}")
                    
        except Exception as e:
            self.logger.error(f"Error removing cache entry: {e}")
    
    def _update_metrics(self, metric: str):
        """Update performance metrics"""
        with self._metrics_lock:
            if metric in self._metrics:
                self._metrics[metric] += 1
    
    def invalidate_config(self, config_path: str):
        """Invalidate a specific configuration"""
        try:
            self._remove_entry(config_path)
            self.logger.info(f"Invalidated config {config_path}")
        except Exception as e:
            self.logger.error(f"Error invalidating config {config_path}: {e}")
    
    def clear_cache(self):
        """Clear entire cache"""
        try:
            with self._cache_lock:
                self._cache.clear()
                self.current_size_bytes = 0
            
            self._lru_cache.clear()
            
            with self._watcher_lock:
                self._file_watchers.clear()
            
            self.logger.info("Cache cleared")
        except Exception as e:
            self.logger.error(f"Error clearing cache: {e}")
    
    def get_cache_stats(self) -> Dict[str, Any]:
        """Get cache statistics"""
        try:
            with self._metrics_lock:
                metrics = self._metrics.copy()
            
            with self._cache_lock:
                cache_size = len(self._cache)
                total_size_mb = self.current_size_bytes / (1024 * 1024)
            
            hit_rate = 0
            if metrics["total_requests"] > 0:
                hit_rate = metrics["hits"] / metrics["total_requests"]
            
            return {
                "cache_size": cache_size,
                "total_size_mb": round(total_size_mb, 2),
                "max_size_mb": round(self.max_size_bytes / (1024 * 1024), 2),
                "hit_rate": round(hit_rate, 3),
                "metrics": metrics,
                "lru_cache_size": self._lru_cache.size(),
                "file_watchers": len(self._file_watchers)
            }
        except Exception as e:
            self.logger.error(f"Error getting cache stats: {e}")
            return {}
    
    def cleanup_expired_entries(self):
        """Clean up expired cache entries"""
        try:
            now = datetime.now()
            expired_paths = []
            
            with self._cache_lock:
                for path, entry in self._cache.items():
                    # Remove entries older than 24 hours
                    if (now - entry.created_at) > timedelta(hours=24):
                        expired_paths.append(path)
                
                for path in expired_paths:
                    self._remove_entry(path)
            
            if expired_paths:
                self.logger.info(f"Cleaned up {len(expired_paths)} expired entries")
                
        except Exception as e:
            self.logger.error(f"Error cleaning up expired entries: {e}")


# Global config cache instance
_config_cache = None

def get_config_cache(max_size_mb: int = 100, logger: logging.Logger = None) -> ConfigCache:
    """Get the global configuration cache instance"""
    global _config_cache
    if _config_cache is None:
        _config_cache = ConfigCache(max_size_mb, logger)
    return _config_cache


# Decorator for caching config loading
def cached_config(ttl_seconds: int = 3600):
    """Decorator to cache configuration loading"""
    def decorator(func):
        @lru_cache(maxsize=128)
        def wrapper(*args, **kwargs):
            return func(*args, **kwargs)
        return wrapper
    return decorator 