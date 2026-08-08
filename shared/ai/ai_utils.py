import time
import logging
from enum import Enum, auto
from typing import TYPE_CHECKING

from .ai_client import AIClientError
from .google_errors import index_error_details

if TYPE_CHECKING:
    from .ai_client import AIClient

logger = logging.getLogger(__name__)


class PromptError(Enum):
    QUOTA_EXCEEDED = auto()
    RATE_LIMIT = auto()
    OTHER = auto()


def _identify_client_error(e: AIClientError) -> tuple[PromptError, int | None]:
    cause = getattr(e, '__cause__', None)
    details = getattr(cause, 'details', None) if cause else None

    if not isinstance(details, dict):
        logger.debug("Non-Gemini structured error")
        return (PromptError.OTHER, None)

    entries = index_error_details(details)
    retry = entries.get('RetryInfo')
    quota = entries.get('QuotaFailure', {}).get('violations', [{}])[0]

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
    client: "AIClient",
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