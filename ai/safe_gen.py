import time
from google.genai import errors

def safe_generate(func, *args, retries=3, wait=5):
    for attempt in range(retries):
        try:
            return func(*args)
        except errors.ServerError as e:
            print(e)
            print(f"Attempt {attempt+1} failed: {e}. Retrying in {wait}s...")
            time.sleep(wait)
    raise RuntimeError("Max retries reached for AI call.")
