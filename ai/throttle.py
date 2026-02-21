from utils.safe_gen import safe_gen
from google.genai.errors import ClientError
from tqdm import tqdm
from models.article import Article
import time
import logging
logger = logging.getLogger(__name__)

def handle_client_error(e: ClientError) -> bool:
    """Handle a ClientError from the AI call."""
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

def throttle(ai_client, processed_articles: list[Article], max_attempts: int = 5) -> bool:
    """Process a list of articles through the AI summarisation and tagging function,
    handling quota limits and retry delays."""
    logger.info(f"Starting AI processing for {len(processed_articles)} articles")
    
    success_count = 0
    fail_count = 0
    
    for article in tqdm(processed_articles, desc="AI Processing"):
        logger.debug(f"Processing: {article.title[:50]}...")
        
        for attempt in range(max_attempts):
            try:
                safe_gen(ai_client.sum_tag_prompt, article)
                success_count += 1
                logger.debug(f"Success on attempt {attempt + 1}")
                break
            except ClientError as e:
                logger.warning(f"ClientError on attempt {attempt + 1}: {e}")
                if handle_client_error(e):
                    logger.error("Daily quota exceeded, stopping AI processing")
                    logger.info(f"Processed {success_count}/{len(processed_articles)} before quota limit")
                    return False
                if attempt == max_attempts - 1:
                    fail_count += 1
                    logger.error(f"Failed after {max_attempts} attempts: {article.title[:50]}")
        
    logger.info(f"AI processing complete: {success_count} success, {fail_count} failed")
    return True