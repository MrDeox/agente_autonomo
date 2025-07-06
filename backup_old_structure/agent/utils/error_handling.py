"""
Utilitários para tratamento robusto de erros
"""
import time
import logging
from typing import Any, Callable, Optional, Tuple

def safe_execute(func: Callable, *args, **kwargs) -> Tuple[Any, Optional[str]]:
    """Execute function safely with error handling"""
    try:
        return func(*args, **kwargs), None
    except Exception as e:
        return None, str(e)

def retry_with_backoff(func: Callable, max_retries: int = 3, backoff_factor: int = 2) -> Any:
    """Retry function with exponential backoff"""
    for attempt in range(max_retries):
        try:
            return func()
        except Exception as e:
            if attempt == max_retries - 1:
                raise
            time.sleep(backoff_factor ** attempt)
