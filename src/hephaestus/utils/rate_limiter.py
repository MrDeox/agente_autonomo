"""
Rate Limiter - Sistema global de controle de taxa de chamadas à API
"""

import asyncio
import time
import logging
from typing import Dict, Any, Optional
from dataclasses import dataclass
from collections import deque
import threading


@dataclass
class RateLimitConfig:
    """Configuração de rate limiting"""
    max_concurrent_calls: int = 2
    calls_per_minute: int = 30
    retry_delay_seconds: int = 5
    exponential_backoff: bool = True


class RateLimiter:
    """Sistema de rate limiting global para chamadas à API"""
    
    def __init__(self, config: RateLimitConfig, logger: logging.Logger):
        self.config = config
        self.logger = logger.getChild("RateLimiter")
        
        # Semáforo para controlar chamadas simultâneas
        self.concurrent_semaphore = asyncio.Semaphore(config.max_concurrent_calls)
        
        # Controle de chamadas por minuto
        self.call_history = deque()
        self.call_history_lock = threading.Lock()
        
        # Controle de backoff
        self.last_failure_time = 0
        self.consecutive_failures = 0
        self.backoff_lock = threading.Lock()
        
        self.logger.info(f"🚦 Rate limiter initialized: {config.max_concurrent_calls} concurrent, {config.calls_per_minute}/min")
    
    async def acquire_call_slot(self) -> bool:
        """Adquire um slot para fazer uma chamada à API"""
        try:
            # Verificar se não excedemos o limite por minuto
            if not self._can_make_call():
                self.logger.warning("Rate limit exceeded - too many calls per minute")
                return False
            
            # Aguardar semáforo para chamadas simultâneas
            await self.concurrent_semaphore.acquire()
            
            # Registrar chamada
            self._record_call()
            
            return True
            
        except Exception as e:
            self.logger.error(f"Error acquiring call slot: {e}")
            return False
    
    def release_call_slot(self):
        """Libera o slot de chamada"""
        try:
            self.concurrent_semaphore.release()
        except Exception as e:
            self.logger.error(f"Error releasing call slot: {e}")
    
    def _can_make_call(self) -> bool:
        """Verifica se pode fazer uma chamada baseado no limite por minuto"""
        with self.call_history_lock:
            current_time = time.time()
            
            # Remover chamadas antigas (mais de 1 minuto)
            while self.call_history and current_time - self.call_history[0] > 60:
                self.call_history.popleft()
            
            # Verificar se não excedemos o limite
            return len(self.call_history) < self.config.calls_per_minute
    
    def _record_call(self):
        """Registra uma chamada no histórico"""
        with self.call_history_lock:
            self.call_history.append(time.time())
    
    def record_failure(self):
        """Registra uma falha para ajustar backoff"""
        with self.backoff_lock:
            current_time = time.time()
            self.consecutive_failures += 1
            self.last_failure_time = current_time
    
    def record_success(self):
        """Registra um sucesso para resetar backoff"""
        with self.backoff_lock:
            self.consecutive_failures = 0
    
    async def get_backoff_delay(self) -> float:
        """Calcula delay de backoff baseado em falhas consecutivas"""
        if not self.config.exponential_backoff or self.consecutive_failures == 0:
            return self.config.retry_delay_seconds
        
        # Backoff exponencial: 5s, 10s, 20s, 40s, 80s...
        delay = min(
            self.config.retry_delay_seconds * (2 ** (self.consecutive_failures - 1)),
            300  # Máximo 5 minutos
        )
        
        self.logger.info(f"Backoff delay: {delay}s (failures: {self.consecutive_failures})")
        return delay
    
    def get_status(self) -> Dict[str, Any]:
        """Retorna status atual do rate limiter"""
        with self.call_history_lock:
            current_calls = len(self.call_history)
        
        with self.backoff_lock:
            return {
                "concurrent_calls_available": self.concurrent_semaphore._value,
                "calls_in_last_minute": current_calls,
                "max_calls_per_minute": self.config.calls_per_minute,
                "consecutive_failures": self.consecutive_failures,
                "last_failure_time": self.last_failure_time,
                "backoff_active": self.consecutive_failures > 0
            }


# Instância global do rate limiter
_global_rate_limiter: Optional[RateLimiter] = None


def get_global_rate_limiter(config: Dict[str, Any], logger: logging.Logger) -> RateLimiter:
    """Obtém a instância global do rate limiter"""
    global _global_rate_limiter
    
    if _global_rate_limiter is None:
        rate_config = RateLimitConfig(
            max_concurrent_calls=config.get("rate_limiting", {}).get("max_concurrent_llm_calls", 2),
            calls_per_minute=config.get("rate_limiting", {}).get("calls_per_minute", 30),
            retry_delay_seconds=config.get("rate_limiting", {}).get("retry_delay_seconds", 5),
            exponential_backoff=config.get("rate_limiting", {}).get("exponential_backoff", True)
        )
        _global_rate_limiter = RateLimiter(rate_config, logger)
    
    return _global_rate_limiter


async def with_rate_limiting(func, *args, **kwargs):
    """Decorator para aplicar rate limiting a uma função"""
    rate_limiter = get_global_rate_limiter({}, logging.getLogger())
    
    # Aguardar slot disponível
    if not await rate_limiter.acquire_call_slot():
        raise Exception("Rate limit exceeded")
    
    try:
        # Executar função
        result = await func(*args, **kwargs)
        rate_limiter.record_success()
        return result
    except Exception as e:
        rate_limiter.record_failure()
        raise
    finally:
        rate_limiter.release_call_slot() 