from ai.prompt import sum_tag_prompt
from ai.safe_gen import safe_generate
from google.genai.errors import ClientError
from tqdm import tqdm
from models.article import Article
import time

def handle_client_error(e: ClientError) -> bool:
    """
    Handle a ClientError from the AI call.

    Returns:
        bool: True if processing should stop due to daily quota, False otherwise.
    """
    error_block = e.details.get('error', {})
    for entry in error_block.get('details', []):
        type_str = entry.get('@type', '')
        if type_str.endswith('QuotaFailure'):
            if 'PerDay' in entry['violations'][0]['quotaId']:
                return True  # stop processing
        elif type_str.endswith('RetryInfo'):
            retry_delay = int(entry['retryDelay'].rstrip('s'))
            time.sleep(retry_delay + 1)
    return False

def throttle(processed_articles: list[Article], max_attempts: int = 5) -> bool:
    """
    Process a list of articles through the AI summarisation and tagging function,
    handling quota limits and retry delays.

    Args:
        processed_articles (list[Article]): List of Article objects to process.
        max_attempts (int): Max retry attempts per article for transient errors.

    Returns:
        bool: False if daily quota is reached and processing must stop, True if all articles processed successfully.
    """
    for article in tqdm(processed_articles, desc="Summarising and tagging articles"):
        attempts = 0
        while attempts < max_attempts:
            try:
                safe_generate(sum_tag_prompt, article)
                break
            except ClientError as e:
                if handle_client_error(e):
                    return False
            attempts += 1
    return True