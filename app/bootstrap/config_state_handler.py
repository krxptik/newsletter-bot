import logging

from app.persistence.data_manager import load_file_data, overwrite_file_data
from config import CONFIG_DIR
from app.bootstrap.setup_wizard import run_setup_wizard
from app.bootstrap.settings_menu import run_main_menu

logger = logging.getLogger(__name__)

CONFIG_FILE = CONFIG_DIR / "config.json"


class UserExitError(Exception):
    """Raised when the user chooses to exit from the main menu."""
    pass


class Config:
    def __init__(self):
        logger.debug(f"Loading config from {CONFIG_FILE}")
        raw = load_file_data(CONFIG_FILE)
        self.ai_ready = raw.get("ai_ready", False)
        self.sender_ready = raw.get("sender_ready", False)
        self.feeds_ready = raw.get("feeds_ready", False)
        self.recipients_ready = raw.get("recipients_ready", False)
        logger.debug(
            f"Config loaded — ai_ready={self.ai_ready}, "
            f"sender_ready={self.sender_ready}, feeds_ready={self.feeds_ready}, "
            f"recipients_ready={self.recipients_ready}"
        )

    def is_complete(self) -> bool:
        return (
            self.ai_ready
            and self.sender_ready
            and self.feeds_ready
            and self.recipients_ready
        )

    def update_config(self) -> None:
        logger.debug("Persisting config state")
        overwrite_file_data(self._compile_data(), CONFIG_FILE)

    def _compile_data(self) -> dict:
        return {
            "ai_ready": self.ai_ready,
            "sender_ready": self.sender_ready,
            "feeds_ready": self.feeds_ready,
            "recipients_ready": self.recipients_ready,
        }


def start_initialisation() -> None:
    logger.info("Starting initialisation")
    config = Config()

    if config.is_complete():
        logger.info("Config complete — skipping setup wizard")
        run_main_menu(config)
    else:
        logger.info("Config incomplete — launching setup wizard")
        run_setup_wizard(config)
        run_main_menu(config)

    logger.info("Initialisation complete")