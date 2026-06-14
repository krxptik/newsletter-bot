import logging
from shared.ai_client import AIClient
from shared.exceptions import InsufficientQuotaError

logger = logging.getLogger(__name__)


def retrieve_article_limit(client: AIClient, metadata_requests: int = 1) -> int:
    """Calculate how many articles can be processed given remaining AI quota."""
    remaining = client.remaining_requests()
    logger.debug(f"Remaining AI requests today: {remaining}")

    limit = remaining - metadata_requests

    if limit <= 0:
        logger.error(f"Insufficient quota: {remaining} remaining, {metadata_requests} reserved for metadata")
        raise InsufficientQuotaError("Not enough AI requests remaining today — try again tomorrow.")

    logger.info(f"Article limit set to {limit} ({remaining} remaining, {metadata_requests} reserved for metadata)")
    return limit