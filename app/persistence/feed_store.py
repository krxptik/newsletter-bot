import logging
from dataclasses import asdict

from path_config import CONFIG_DIR
from .data_manager import load_file_data, overwrite_file_data
from models import Feed

logger = logging.getLogger(__name__)

FEEDS_FILE = CONFIG_DIR / "feeds.json"


def load_feeds(path=FEEDS_FILE) -> list[Feed]:
    logger.debug(f"Loading feeds from {path}")
    data = load_file_data(path, default=[])
    logger.info(f"Loaded {len(data)} feeds from config")
    return [Feed.from_dict(f) for f in data]


def save_feeds(feeds: list[Feed], path=FEEDS_FILE) -> None:
    logger.info(f"Saving {len(feeds)} feeds to {path}")
    overwrite_file_data([asdict(f) for f in feeds], path)
    logger.debug("Feeds saved successfully")