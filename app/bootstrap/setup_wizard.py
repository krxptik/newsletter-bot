import logging
import time
from typing import TYPE_CHECKING

from shared.terminal import display_banner, clear_terminal, confirmation
from app.bootstrap.setup.env_manager import read_env, write_env
from app.bootstrap.setup.ai_setup import run_ai_setup
from app.bootstrap.setup.sender_setup import run_sender_setup
from app.bootstrap.setup.feed_setup import run_feed_setup
from app.bootstrap.recipient_manager import run_recipient_manager
from app.bootstrap.settings_menu import UserExitError

if TYPE_CHECKING:
    from app.bootstrap.config_state_handler import Config

logger = logging.getLogger(__name__)

PAUSE_SHORT = 3


def run_setup_wizard(config: "Config") -> None:
    logger.info("Setup wizard started")
    env_vars = read_env()

    clear_terminal()
    display_banner("SETUP WIZARD")
    print(
        "\nBefore you begin, please ensure you have the following:"
        "\n  • A Google AI Studio API key (https://aistudio.google.com/app/api-keys)"
        "\n  • An email app password (https://support.google.com/mail/answer/185833?hl=en)"
        "\n  • An email address to send newsletters from"
        "\n  • A list of RSS and non-RSS feeds and their URLs"
        "\n  • Recipient email addresses"
        "\n"
        "\nIMPORTANT NOTES:"
        "\n  • Double-check all entries during setup."
        "\n  • Configuration can be changed at any time in the settings menu"
        "\n"
    )
    if not confirmation("Are you ready to proceed?"):
        raise UserExitError("Exited the program.")

    # --- AI Setup ---
    logger.info(f"AI setup starting in {PAUSE_SHORT}s")
    print(f"\nLoading AI setup in {PAUSE_SHORT} seconds...")
    time.sleep(PAUSE_SHORT)

    env_vars = run_ai_setup(env_vars)
    write_env(env_vars)
    config.ai_ready = True
    config.update_config()
    logger.info("AI setup complete")

    clear_terminal()
    display_banner("SETUP WIZARD")
    print("\nAI setup completed (or already configured).")

    # --- Sender Setup ---
    logger.info(f"Sender setup starting in {PAUSE_SHORT}s")
    print(f"Loading sender setup in {PAUSE_SHORT} seconds...")
    time.sleep(PAUSE_SHORT)

    env_vars = run_sender_setup(env_vars)
    write_env(env_vars)
    config.sender_ready = True
    config.update_config()
    logger.info("Sender setup complete")

    clear_terminal()
    display_banner("SETUP WIZARD")
    print("\nSender setup completed (or already configured).")

    # --- Feed Setup ---
    logger.info(f"Feed setup starting in {PAUSE_SHORT}s")
    print(f"Loading feed setup in {PAUSE_SHORT} seconds...")
    time.sleep(PAUSE_SHORT)

    run_feed_setup()
    config.feeds_ready = True
    config.update_config()
    logger.info("Feed setup complete")

    clear_terminal()
    display_banner("SETUP WIZARD")
    print("\nFeed setup completed.")

    # --- Recipient Setup ---
    logger.info(f"Recipient setup starting in {PAUSE_SHORT}s")
    print(f"Loading recipient setup in {PAUSE_SHORT} seconds...")
    time.sleep(PAUSE_SHORT)

    run_recipient_manager(title="ADDRESS BOOK SETUP")
    config.recipients_ready = True
    config.update_config()
    logger.info("Recipient setup complete")

    clear_terminal()
    display_banner("SETUP WIZARD")
    print("\nRecipient setup completed.")
    print("\nSetup complete!")
    time.sleep(PAUSE_SHORT)
    logger.info("Setup wizard finished")