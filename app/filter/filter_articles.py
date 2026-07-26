import logging
from datetime import datetime

from app.persistence import load_used_urls
from models import Article
from shared.ai_client import AIClient
from shared.exceptions import InsufficientQuotaError

logger = logging.getLogger(__name__)


def _retrieve_article_limit(client: AIClient, metadata_requests: int = 1) -> int:
    """Calculate how many articles can be processed given remaining AI quota."""
    remaining = client.remaining_requests()
    logger.debug(f"Remaining AI requests today: {remaining}")

    limit = remaining - metadata_requests

    if limit <= 0:
        logger.error(f"Insufficient quota: {remaining} remaining, {metadata_requests} reserved for metadata")
        raise InsufficientQuotaError("Not enough AI requests remaining today — try again tomorrow.")

    logger.info(f"Article limit set to {limit} ({remaining} remaining, {metadata_requests} reserved for metadata)")
    return limit


def filter_articles(articles: list[Article], client: AIClient, metadata_requests: int = 1) -> list[Article]:
    """Remove already-used articles and cap the list at max_articles."""
    max_articles = _retrieve_article_limit(client, metadata_requests=metadata_requests)
    used_urls = load_used_urls()

    fresh = [a for a in articles if a.link not in used_urls]
    removed = len(articles) - len(fresh)

    if removed:
        logger.info(f"Filtered {removed} already-used articles")

    if len(fresh) > max_articles:
        fresh.sort(key=lambda a: a.pub_date or datetime.min, reverse=True)
        fresh = fresh[:max_articles]
        logger.info(f"Capped to {max_articles} newest articles")

    logger.info(f"Filter complete: {len(fresh)} remain from {len(articles)} total")
    return fresh