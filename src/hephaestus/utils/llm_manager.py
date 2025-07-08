"""
LLM Manager - Centralized LLM call management with retry, metrics, and caching
"""

import asyncio
import time
import json
from typing import Dict, Any, Optional, Tuple, List, Callable
from functools import wraps
from contextlib import asynccontextmanager
import logging

from hephaestus.utils.llm_client import call_llm_api, call_llm_with_fallback
from hephaestus.utils.json_parser import parse_json_response
from hephaestus.utils.intelligent_cache import IntelligentCache
from hephaestus.utils.metrics_collector import MetricsCollector


class LLMCallManager:
    """Manages LLM calls with standardized retry, caching, and metrics."""
    
    def __init__(self, model_config: Dict[str, Any], logger: logging.Logger):
        self.model_config = model_config
        self.logger = logger
        self.metrics = MetricsCollector()
        self.cache = IntelligentCache(max_size=1000, default_ttl=3600)
        
        # Default settings
        self.default_settings = {
            'temperature': 0.4,
            'max_retries': 3,
            'timeout': 60,
            'cache_enabled': True,
        }
    
    async def safe_call_with_retry(self, 
                                 prompt: str, 
                                 temperature: float = None,
                                 max_retries: int = None,
                                 fallback_models: List[str] = None,
                                 cache_key: Optional[str] = None,
                                 **kwargs) -> Tuple[Optional[str], Optional[str]]:
        """
        Make an LLM call with retry logic, caching, and metrics.
        
        Args:
            prompt: The prompt to send to the LLM
            temperature: Temperature setting (uses default if None)
            max_retries: Maximum retry attempts (uses default if None)
            fallback_models: List of fallback models to try
            cache_key: Custom cache key (auto-generated if None)
            **kwargs: Additional parameters for LLM call
            
        Returns:
            Tuple of (response, error_message)
        """
        # Use defaults if not provided
        temperature = temperature or self.default_settings['temperature']
        max_retries = max_retries or self.default_settings['max_retries']
        
        # Generate cache key if not provided
        if cache_key is None and self.default_settings['cache_enabled']:
            cache_key = self._generate_cache_key(prompt, temperature, kwargs)
        
        # Check cache first
        if cache_key and self.cache.get(cache_key):
            cached_result = self.cache.get(cache_key)
            self.metrics.record_llm_call(
                model=str(self.model_config),
                prompt_tokens=len(prompt.split()),
                completion_tokens=len(cached_result.split()) if cached_result else 0,
                duration=0.001,  # Cache hit
                success=True,
                cached=True
            )
            return cached_result, None
        
        # Track timing
        start_time = time.time()
        
        # Try primary model with retries
        for attempt in range(max_retries):
            try:
                async with self._call_context(f"llm_call_attempt_{attempt + 1}"):
                    response, error = await self._make_llm_call(prompt, temperature, **kwargs)
                    
                    if response and not error:
                        duration = time.time() - start_time
                        
                        # Cache successful response
                        if cache_key:
                            self.cache.set(cache_key, response)
                        
                        # Record metrics
                        self.metrics.record_llm_call(
                            model=str(self.model_config),
                            prompt_tokens=len(prompt.split()),
                            completion_tokens=len(response.split()),
                            duration=duration,
                            success=True,
                            attempt=attempt + 1
                        )
                        
                        return response, None
                    
                    # Log retry attempt
                    self.logger.warning(f"LLM call attempt {attempt + 1} failed: {error}")
                    
                    if attempt < max_retries - 1:
                        await asyncio.sleep(2 ** attempt)  # Exponential backoff
                        
            except Exception as e:
                self.logger.error(f"LLM call attempt {attempt + 1} exception: {e}")
                if attempt < max_retries - 1:
                    await asyncio.sleep(2 ** attempt)
        
        # Try fallback models if primary failed
        if fallback_models:
            for fallback_model in fallback_models:
                try:
                    self.logger.info(f"Trying fallback model: {fallback_model}")
                    fallback_config = {**self.model_config, 'model': fallback_model}
                    
                    response, error = await self._make_llm_call_with_config(
                        prompt, temperature, fallback_config, **kwargs
                    )
                    
                    if response and not error:
                        duration = time.time() - start_time
                        
                        # Cache successful response
                        if cache_key:
                            self.cache.set(cache_key, response)
                        
                        # Record metrics with fallback flag
                        self.metrics.record_llm_call(
                            model=fallback_model,
                            prompt_tokens=len(prompt.split()),
                            completion_tokens=len(response.split()),
                            duration=duration,
                            success=True,
                            fallback=True
                        )
                        
                        return response, None
                        
                except Exception as e:
                    self.logger.error(f"Fallback model {fallback_model} failed: {e}")
        
        # All attempts failed
        duration = time.time() - start_time
        self.metrics.record_llm_call(
            model=str(self.model_config),
            prompt_tokens=len(prompt.split()),
            completion_tokens=0,
            duration=duration,
            success=False
        )
        
        return None, "All LLM call attempts failed"
    
    async def call_with_json_response(self, 
                                    prompt: str, 
                                    **kwargs) -> Tuple[Optional[Dict[str, Any]], Optional[str]]:
        """
        Make an LLM call expecting a JSON response.
        
        Args:
            prompt: The prompt to send to the LLM
            **kwargs: Additional parameters for LLM call
            
        Returns:
            Tuple of (parsed_json, error_message)
        """
        response, error = await self.safe_call_with_retry(prompt, **kwargs)
        
        if error:
            return None, error
        
        if not response:
            return None, "No response from LLM"
        
        # Parse JSON response
        parsed_json, parse_error = parse_json_response(response, self.logger)
        
        if parse_error:
            self.logger.warning(f"JSON parsing failed: {parse_error}")
            return None, f"JSON parsing failed: {parse_error}"
        
        return parsed_json, None
    
    @asynccontextmanager
    async def _call_context(self, operation_name: str):
        """Context manager for LLM call metrics and error handling."""
        start_time = time.time()
        try:
            yield
        except Exception as e:
            duration = time.time() - start_time
            self.logger.error(f"{operation_name} failed after {duration:.2f}s: {e}")
            raise
        else:
            duration = time.time() - start_time
            self.logger.debug(f"{operation_name} completed in {duration:.2f}s")
    
    async def _make_llm_call(self, prompt: str, temperature: float, **kwargs) -> Tuple[Optional[str], Optional[str]]:
        """Make the actual LLM call."""
        try:
            # Use existing LLM client with correct signature
            return call_llm_with_fallback(
                model_config=self.model_config,
                prompt=prompt,
                temperature=temperature,
                logger=self.logger
            )
        except Exception as e:
            return None, str(e)
    
    async def _make_llm_call_with_config(self, prompt: str, temperature: float, config: Dict[str, Any], **kwargs) -> Tuple[Optional[str], Optional[str]]:
        """Make LLM call with specific config."""
        try:
            return call_llm_with_fallback(
                model_config=config,
                prompt=prompt,
                temperature=temperature,
                logger=self.logger
            )
        except Exception as e:
            return None, str(e)
    
    def _generate_cache_key(self, prompt: str, temperature: float, kwargs: Dict[str, Any]) -> str:
        """Generate a cache key for the LLM call."""
        # Create a hash based on prompt, temperature, and relevant kwargs
        import hashlib
        
        cache_data = {
            'prompt': prompt,
            'temperature': temperature,
            'model': str(self.model_config),
            **{k: v for k, v in kwargs.items() if k in ['max_tokens', 'top_p', 'frequency_penalty']}
        }
        
        cache_string = json.dumps(cache_data, sort_keys=True)
        return hashlib.md5(cache_string.encode()).hexdigest()
    
    def get_metrics_summary(self) -> Dict[str, Any]:
        """Get summary of LLM call metrics."""
        return self.metrics.get_llm_dashboard()
    
    def clear_cache(self):
        """Clear the LLM response cache."""
        self.cache.clear()
    
    def get_cache_stats(self) -> Dict[str, Any]:
        """Get cache statistics."""
        return {
            'cache_size': len(self.cache.cache),
            'max_size': self.cache.max_size,
            'default_ttl': self.cache.default_ttl,
        }


# Decorator for automatic LLM call metrics
def llm_call_with_metrics(func: Callable) -> Callable:
    """Decorator to automatically add metrics to LLM call methods."""
    
    @wraps(func)
    async def wrapper(self, *args, **kwargs):
        operation_name = f"{self.__class__.__name__}.{func.__name__}"
        start_time = time.time()
        
        try:
            result = await func(self, *args, **kwargs)
            duration = time.time() - start_time
            
            # Record success metric
            if hasattr(self, 'metrics_collector'):
                self.metrics_collector.record_agent_performance(
                    agent_name=self.__class__.__name__,
                    operation=func.__name__,
                    duration=duration,
                    success=True
                )
            
            return result
            
        except Exception as e:
            duration = time.time() - start_time
            
            # Record failure metric
            if hasattr(self, 'metrics_collector'):
                self.metrics_collector.record_agent_performance(
                    agent_name=self.__class__.__name__,
                    operation=func.__name__,
                    duration=duration,
                    success=False,
                    metadata={'error': str(e)}
                )
            
            raise
    
    return wrapper


def llm_call_with_retry(max_retries: int = 3, fallback_models: List[str] = None):
    """Decorator to automatically add retry logic to LLM call methods."""
    
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def wrapper(self, *args, **kwargs):
            if hasattr(self, 'llm_manager'):
                # Use the agent's LLM manager
                kwargs['max_retries'] = max_retries
                kwargs['fallback_models'] = fallback_models
            
            return await func(self, *args, **kwargs)
        
        return wrapper
    
    return decorator