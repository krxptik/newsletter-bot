import logging
from dataclasses import asdict

from path_config import RUNTIME_DIR
from .data_manager import load_file_data, overwrite_file_data
from .feed_store import backfill_site_urls
from .feed_cache_ops import get_or_create_cache
from models import Feed, FeedCache

logger = logging.getLogger(__name__)

FEED_CACHE_FILE = RUNTIME_DIR / "feed_cache.json"


def load_feed_caches(path=FEED_CACHE_FILE) -> list[FeedCache]:
    logger.debug(f"Loading feed cache from {path}")
    data = load_file_data(path, default=[])
    logger.info(f"Loaded {len(data)} feed cache entries")
    return [FeedCache.from_dict(c) for c in data]


def save_feed_caches(caches: list[FeedCache], path=FEED_CACHE_FILE) -> None:
    logger.info(f"Saving {len(caches)} feed cache entries to {path}")
    overwrite_file_data([asdict(c) for c in caches], path)
    logger.debug("Feed cache saved successfully")


def backfill_feed_caches(feeds: list[Feed]) -> list[FeedCache]:
    caches = load_feed_caches()
    before = len(caches)

    for feed in feeds:
        get_or_create_cache(caches, feed)

    if len(caches) != before:
        save_feed_caches(caches)

    return caches


def load_feeds_with_caches() -> tuple[list[Feed], list[FeedCache]]:
    feeds = backfill_site_urls()       # already self-contained: load -> resolve -> save -> return
    caches = backfill_feed_caches(feeds)  # already self-contained: load -> fill gaps -> save -> return
    return feeds, caches