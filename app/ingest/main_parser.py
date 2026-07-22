# Standard library
import logging

# Third-party libraries
import requests
from tqdm import tqdm

# Local application imports
from models import Feed
from app.ingest.rss_parser import parse_rss
from app.ingest.non_rss_parser import parse_non_rss

# Module logger
logger = logging.getLogger(__name__)


def parse_all(feeds: list[Feed], session: requests.Session) -> list:
    """Parse all feeds and return a flat list of recent Article objects."""
    logger.info(f"parse_all: parsing {len(feeds)} feeds")

    articles = []
    for feed in tqdm(
        feeds,
        desc="Feed parsing",
        unit="feed",
        bar_format="{desc}: {percentage:3.0f}%|{bar}| {n}/{total} {unit}s [{elapsed} elapsed, ~{remaining} left]"
    ):
        try:
            if feed.metadata_retrieval == "collect":
                result = parse_rss(feed, session)
            else:
                result = parse_non_rss(feed, session)
            articles.extend(result)
        except Exception as e:
            logger.error(f"Unhandled error on '{feed.name}': {e}", exc_info=True)

    logger.info(f"{len(articles)} total articles across {len(feeds)} feeds")
    return articles