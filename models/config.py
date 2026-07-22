import logging
from dataclasses import dataclass

from path_config import CONFIG_DIR
from app.persistence import load_file_data, overwrite_file_data, load_feeds, load_address_book

logger = logging.getLogger(__name__)

CONFIG_FILE = CONFIG_DIR / "config.json"


@dataclass
class Config:
    ai_ready: bool = False
    sender_ready: bool = False

    @property
    def feeds_ready(self) -> bool:
        return bool(load_feeds())

    @property
    def recipients_ready(self) -> bool:
        book = load_address_book()
        return bool(book.get("groups") or book.get("ungrouped"))

    def is_complete(self) -> bool:
        return self.ai_ready and self.sender_ready and self.feeds_ready and self.recipients_ready

    def update_config(self) -> None:
        logger.debug("Persisting config state")
        overwrite_file_data(
            {"ai_ready": self.ai_ready, "sender_ready": self.sender_ready},
            CONFIG_FILE,
        )

    def display_data(self) -> list[tuple[str, str]]:
        def _ready(value: bool) -> str:
            return "Ready" if value else "Not ready"
        return [
            ("AI:", _ready(self.ai_ready)),
            ("Sender:", _ready(self.sender_ready)),
            ("Feeds:", _ready(self.feeds_ready)),
            ("Recipients:", _ready(self.recipients_ready))
        ]

    @classmethod
    def load(cls) -> "Config":
        logger.debug(f"Loading config from {CONFIG_FILE}")
        raw = load_file_data(CONFIG_FILE, default={})
        if not isinstance(raw, dict):
            logger.warning(f"Unexpected config format {type(raw).__name__}; using defaults")
            raw = {}
        return cls(
            ai_ready=raw.get("ai_ready", False),
            sender_ready=raw.get("sender_ready", False),
        )