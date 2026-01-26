from google.genai import errors
from typing import Callable, Any
import time

def safe_gen(func: Callable[..., Any], *args: Any, retries: int = 3, wait: int = 5) -> Any:
    """
    Safely execute an AI function call with retry logic on server errors.

    Args:
        func (Callable[..., Any]): The AI function to call.
        *args (Any): Arguments to pass to the function.
        retries (int): Number of retry attempts on server errors.
        wait (int): Seconds to wait between retries.

    Returns:
        Any: The result of `func(*args)` if successful.

    Raises:
        RuntimeError: If maximum retries are reached.
    """

    for attempt in range(retries):
        try:
            return func(*args)
        except errors.ServerError as e:
            time.sleep(wait)
    raise RuntimeError("Max retries reached for AI call.")
