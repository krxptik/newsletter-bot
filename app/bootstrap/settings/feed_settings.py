import logging

from shared.terminal import display_banner, clear_terminal
from app.bootstrap.feed.feed_operations import handle_feed_type
from app.persistence.feed_store import load_feeds

logger = logging.getLogger(__name__)

PAUSE_SHORT = 3


def _display_feed_settings_menu() -> None:
    clear_terminal()
    display_banner("FEED SETTINGS")
    print()
    print("Options:")
    print("  (1) Edit RSS feeds")
    print("  (2) Edit Non-RSS feeds")
    print("  (3) Back")


def run_feed_settings() -> None:
    logger.info("Feed settings opened")
    feeds = load_feeds()

    while True:
        _display_feed_settings_menu()
        user_input = input("\n> ").strip()

        if not user_input.isdigit():
            continue

        option = int(user_input)

        if option == 1:
            handle_feed_type("RSS", feeds)
        elif option == 2:
            handle_feed_type("NON-RSS", feeds)
        elif option == 3:
            logger.info("Feed settings closed")
            return