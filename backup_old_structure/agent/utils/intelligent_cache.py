"""
Sistema de cache inteligente para o Hephaestus
"""
import time
import hashlib
from typing import Any, Optional, Dict
from functools import wraps

class IntelligentCache:
    """Cache inteligente com TTL e LRU"""
    
    def __init__(self, max_size: int = 1000, default_ttl: int = 3600):
        self.cache: Dict[str, Dict[str, Any]] = {}
        self.access_times: Dict[str, float] = {}
        self.max_size = max_size
        self.default_ttl = default_ttl
    
    def _generate_key(self, func_name: str, args: tuple, kwargs: dict) -> str:
        """Gerar chave única para cache"""
        key_data = f"{func_name}:{args}:{sorted(kwargs.items())}"
        return hashlib.md5(key_data.encode()).hexdigest()
    
    def get(self, key: str) -> Optional[Any]:
        """Obter valor do cache"""
        if key not in self.cache:
            return None
        
        entry = self.cache[key]
        if time.time() > entry["expires_at"]:
            del self.cache[key]
            del self.access_times[key]
            return None
        
        self.access_times[key] = time.time()
        return entry["value"]
    
    def set(self, key: str, value: Any, ttl: Optional[int] = None) -> None:
        """Definir valor no cache"""
        if len(self.cache) >= self.max_size:
            self._evict_lru()
        
        ttl = ttl or self.default_ttl
        self.cache[key] = {
            "value": value,
            "expires_at": time.time() + ttl
        }
        self.access_times[key] = time.time()
    
    def _evict_lru(self) -> None:
        """Remover item menos recentemente usado"""
        if not self.access_times:
            return
        
        lru_key = min(self.access_times, key=self.access_times.get)
        del self.cache[lru_key]
        del self.access_times[lru_key]

# Cache global
_global_cache = IntelligentCache()

def cached(ttl: int = 3600):
    """Decorator para cache automático"""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            key = _global_cache._generate_key(func.__name__, args, kwargs)
            result = _global_cache.get(key)
            
            if result is None:
                result = func(*args, **kwargs)
                _global_cache.set(key, result, ttl)
            
            return result
        return wrapper
    return decorator
