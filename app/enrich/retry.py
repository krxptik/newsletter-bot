from shared.ai_client import AIClient, AIClientError
from enum import Enum, auto
import time
import logging

logger = logging.getLogger(__name__)

class PromptError(Enum):
    QUOTA_EXCEEDED = auto()
    RATE_LIMIT = auto()
    OTHER = auto()


def _identify_client_error(e: AIClientError) -> tuple[PromptError, int | None]:
    """Classify AIClientError."""
    cause = getattr(e, '__cause__', None)

    if cause is None or not hasattr(cause, 'details'):
        logger.debug("Non-Gemini structured error")
        return (PromptError.OTHER, None)

    details = getattr(cause, 'details', {})
    if not isinstance(details, dict):
        logger.debug("Non-Gemini structured error")
        return (PromptError.OTHER, None)

    error_block = details.get('error', {})
    quota, retry = {}, {}

    for entry in error_block.get('details', []):
        type_str = entry.get('@type', '')
        if type_str.endswith('QuotaFailure'):
            quota = entry['violations'][0]
        elif type_str.endswith('RetryInfo'):
            retry = entry

    if not retry:
        return (PromptError.OTHER, None)
    if "PerDay" in quota.get('quotaId', ''):
        logger.warning("Daily quota exceeded (Gemini)")
        return (PromptError.QUOTA_EXCEEDED, None)

    retry_delay = int(retry['retryDelay'].rstrip('s'))
    return (PromptError.RATE_LIMIT, retry_delay)

def _handle_client_error(e: AIClientError, attempt: int) -> bool:
    """Return whether to continue retrying."""
    error_type, retry_delay = _identify_client_error(e)

    if error_type == PromptError.QUOTA_EXCEEDED:
        logger.critical("Stopping retries due to daily quota exceeded")
        return False

    if error_type == PromptError.RATE_LIMIT:
        delay = (retry_delay or 0) + 1
        logger.info(f"Rate limited. Sleeping {delay}s")
        time.sleep(delay)
        return True

    # OTHER → exponential backoff
    sleep_time = 2 ** (attempt + 1)
    logger.warning(f"Unknown error. Sleeping {sleep_time}s")
    time.sleep(sleep_time)
    return True


def safe_prompt(
    client: AIClient,
    prompt: str,
    max_attempts: int = 5
) -> tuple[bool, str | None]:

    for attempt in range(max_attempts):
        try:
            response = client.call_api(prompt)
            return (True, response)

        except AIClientError as e:
            logger.warning(f"AIClientError on attempt {attempt + 1}: {e}")

            if not _handle_client_error(e, attempt):
                return (False, None)

    logger.error("All retry attempts exhausted")
    return (False, None)