import asyncio
import functools
import logging
from typing import Callable, Any

logger = logging.getLogger(__name__)

def async_retry(max_retries: int = 3, initial_delay: float = 1.0, backoff_factor: float = 2.0):
    def decorator(func: Callable):
        @functools.wraps(func)
        async def wrapper(*args, **kwargs):
            delay = initial_delay
            last_exception = None
            for attempt in range(max_retries):
                try:
                    return await func(*args, **kwargs)
                except Exception as e:
                    last_exception = e
                    logger.warning(f"Attempt {attempt + 1} failed for {func.__name__}: {e}. Retrying in {delay}s...")
                    await asyncio.sleep(delay)
                    delay *= backoff_factor
            logger.error(f"All {max_retries} attempts failed for {func.__name__}.")
            raise last_exception
        return wrapper
    return decorator
