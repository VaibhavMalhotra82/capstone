import time
import functools
import inspect
import asyncio
from backend.log import logger

def time_it(func):
    """
    Decorator to measure execution time of both sync and async functions.
    """
    if inspect.iscoroutinefunction(func):
        # Async version
        @functools.wraps(func)
        async def async_wrapper(*args, **kwargs):
            start_time = time.perf_counter()
            try:
                result = await func(*args, **kwargs)
            except Exception as e:
                logger.log_error(f"Error in async function '{func.__name__}': {e}")
                raise
            end_time = time.perf_counter()
            logger.log_info(f"Async function '{func.__name__}' executed in {end_time - start_time:.6f} seconds")
            return result
        return async_wrapper
    else:
        # Sync version
        @functools.wraps(func)
        def sync_wrapper(*args, **kwargs):
            start_time = time.perf_counter()
            try:
                result = func(*args, **kwargs)
            except Exception as e:
                logger.log_error(f"Error in function '{func.__name__}': {e}")
                raise
            end_time = time.perf_counter()
            logger.log_info(f"Function '{func.__name__}' executed in {end_time - start_time:.6f} seconds")
            return result
        return sync_wrapper