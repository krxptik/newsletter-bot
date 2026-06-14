import logging
import time

from app.persistence.feed_store import load_feeds
from app.bootstrap.feed.feed_operations import handle_feed_type

logger = logging.getLogger(__name__)


def run_feed_setup() -> None:
    logger.info("Starting feed setup")
    feeds = load_feeds()
    logger.debug(f"Loaded {len(feeds)} existing feeds")

    for f_type in ("RSS", "NON-RSS"):
        logger.info(f"Handling {f_type} feed configuration")
        handle_feed_type(f_type, feeds)
        logger.info(f"{f_type} feed configuration done")

        if f_type == "RSS":
            print("Now loading non-RSS feeds...")
        else:
            print("Consolidating feeds...")
            
        time.sleep(5)

    logger.info(f"All feeds saved ({len(feeds)} total)")
    print("\nSUCCESS: All feeds saved!")