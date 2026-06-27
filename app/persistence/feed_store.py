import logging
from typing import Any, cast

from config import CONFIG_DIR
from app.persistence.data_manager import load_file_data, overwrite_file_data

logger = logging.getLogger(__name__)

FEEDS_FILE = CONFIG_DIR / "feeds.json"


def load_feeds(path=FEEDS_FILE) -> list[dict]:
    logger.debug(f"Loading feeds from {path}")
    data = load_file_data(path, default=[])
    logger.info(f"Loaded {len(data)} feeds from config")
    return cast(list[dict], data)


def save_feeds(feeds: list[dict], path=FEEDS_FILE) -> None:
    logger.info(f"Saving {len(feeds)} feeds to {path}")
    overwrite_file_data(feeds, path)
    logger.debug("Feeds saved successfully")