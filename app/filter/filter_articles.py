import logging
from datetime import datetime

from models import Article
from app.persistence import load_used_urls

logger = logging.getLogger(__name__)


def filter_articles(articles: list[Article], max_articles: int) -> list[Article]:
    """Remove already-used articles and cap the list at max_articles."""
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