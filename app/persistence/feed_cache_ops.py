import logging
from models import Feed, FeedCache

logger = logging.getLogger(__name__)


def get_or_create_cache(caches: list[FeedCache], feed: Feed) -> FeedCache:
    """Return the cache entry for this feed, creating one if absent."""
    for cache in caches:
        if cache.name == feed.name:
            return cache

    logger.info(f"No cache entry for '{feed.name}' — creating one")
    entry = FeedCache(name=feed.name, trust_feed_url=bool(feed.feed_url))
    caches.append(entry)
    return entry


def match_feeds_to_caches(feeds: list[Feed], caches: list[FeedCache]) -> list[tuple[Feed, FeedCache]]:
    """Return a list of (feed, cache) pairs matched by feed name."""
    cache_by_name = {cache.name: cache for cache in caches}
    pairs: list[tuple[Feed, FeedCache]] = []

    for feed in feeds:
        cache = cache_by_name[feed.name]
        pairs.append((feed, cache))

    return pairs


def remove_feed_cache(caches: list[FeedCache], feed: Feed) -> None:
    """Remove the cache entry matching this feed's name, if present."""
    match = next((c for c in caches if c.name == feed.name), None)
    if match is None:
        logger.warning(f"No cache entry found for '{feed.name}' — nothing to remove")
        return
    caches.remove(match)
    logger.info(f"Removed cache entry for '{feed.name}'")


