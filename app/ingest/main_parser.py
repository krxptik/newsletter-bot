# Standard library
import logging

# Third-party libraries
import requests
from tqdm import tqdm

# Local application imports
from app.ingest.rss_parser import parse_rss
from app.ingest.non_rss_parser import parse_non_rss

# Module logger
logger = logging.getLogger(__name__)

FEED_PARSERS = {
    "RSS": parse_rss,
    "NON-RSS": parse_non_rss,
}


def parse_all(feeds: list, session: requests.Session) -> list:
    """Parse all feeds and return a flat list of recent Article objects."""
    logger.info(f"parse_all: parsing {len(feeds)} feeds")

    articles = []
    for feed in tqdm(
        feeds, 
        desc="Feed parsing", 
        unit="feed", 
        bar_format="{desc}: {percentage:3.0f}%|{bar}| {n}/{total} {unit}s [{elapsed} elapsed, ~{remaining} left]"
    ):
        name = feed.get("name")
        feed_type = feed.get("type")

        parser = FEED_PARSERS.get(feed_type)
        if parser is None:
            logger.warning(f"parse_all: unknown feed type '{feed_type}' for '{name}' — skipping")
            continue

        try:
            result = parser(feed, session)
            articles.extend(result)
        except Exception as e:
            logger.error(f"parse_all: unhandled error on '{name}': {e}", exc_info=True)

    logger.info(f"parse_all: {len(articles)} total articles across {len(feeds)} feeds")
    return articles