import logging

from path_config import CONFIG_DIR
from models.config import Config
from .data_manager import load_file_data, overwrite_file_data
from .feed_store import load_feeds
from .addrs_book_store import load_address_book

logger = logging.getLogger(__name__)

CONFIG_FILE = CONFIG_DIR / "config.json"


def load_config() -> Config:
    logger.debug(f"Loading config from {CONFIG_FILE}")
    raw = load_file_data(CONFIG_FILE, default={})
    if not isinstance(raw, dict):
        logger.warning(f"Unexpected config format {type(raw).__name__}; using defaults")
        raw = {}

    config = Config(
        ai_ready=raw.get("ai_ready", False),
        sender_ready=raw.get("sender_ready", False),
    )
    refresh_dynamic_flags(config)
    return config


def refresh_dynamic_flags(config: Config) -> None:
    """Recompute feeds_ready/recipients_ready from current data — no staleness possible."""
    config.feeds_ready = bool(load_feeds())
    book = load_address_book()
    config.recipients_ready = bool(book.get("groups") or book.get("ungrouped"))


def save_config(config: Config) -> None:
    logger.debug("Persisting config state")
    overwrite_file_data(
        {"ai_ready": config.ai_ready, "sender_ready": config.sender_ready},
        CONFIG_FILE,
    )