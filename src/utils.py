# src/utils.py

import logging
import asyncio
from tenacity import retry, stop_after_attempt, wait_fixed, retry_if_exception_type

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def get_logger(name):
    return logging.getLogger(name)

@retry(stop=stop_after_attempt(5), wait=wait_fixed(2), retry=retry_if_exception_type(Exception))
async def safe_async_call(func, *args, **kwargs):
    """
    A decorator for safe asynchronous function calls with retries.
    Adjust retry conditions based on specific API error types (e.g., rate limits).
    """
    try:
        return await func(*args, **kwargs)
    except Exception as e:
        get_logger(__name__).error(f"Error during async call: {e}")
        raise # Re-raise to trigger tenacity retry