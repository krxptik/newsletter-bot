import logging
import time

from .environment import read_env, write_env
from .ai import run_ai_setup
from .sender import run_sender_setup
from .feed import run_feed_manager
from .recipient import run_recipient_manager

from app.persistence import save_config
from models.config import Config
from shared.ui import widgets, PAUSE_SHORT
from shared.prompts import confirmation
from shared.exceptions import UserExitError

logger = logging.getLogger(__name__)


def run_setup_wizard(config: Config) -> None:
    logger.info("Setup wizard started")
    env_vars = read_env()

    widgets.banner("SETUP WIZARD", clear=True)
    widgets.blank()
    message = "\n".join([
        "Before you begin with the setup, please ensure you have the following:",
        "  • A Google AI Studio API key",
        "  • An email app password",
        "  • An email address to send newsletters from",
        "  • A list of feeds with their names and URLs",
        "  • Recipient email addresses (and/or groups)",
        "",
        "For reference:",
        "  • https://aistudio.google.com/app/api-keys",
        "  • https://support.google.com/mail/answer/185833?hl=en",
        "",
        "IMPORTANT NOTES:",
        "  • Double-check all entries during setup.",
        "  • Configuration can be changed at any time in the settings menu.",
    ])
    widgets.text(message)
    widgets.blank()
    if not confirmation("Are you ready to proceed?"):
        raise UserExitError("Exited the program.")

    # --- AI Setup ---
    logger.info(f"AI setup starting in {PAUSE_SHORT}s")
    widgets.notify(f"Loading AI setup in {PAUSE_SHORT} seconds...")

    env_vars = run_ai_setup(env_vars)
    write_env(env_vars)
    config.ai_ready = True
    save_config(config)
    logger.info("AI setup complete")

    widgets.banner("SETUP WIZARD", clear=True)
    widgets.blank()
    widgets.text("AI setup completed (or already configured).")

    # --- Sender Setup ---
    logger.info(f"Sender setup starting in {PAUSE_SHORT}s")
    widgets.notify(f"Loading sender setup in {PAUSE_SHORT} seconds...")

    env_vars = run_sender_setup(env_vars)
    write_env(env_vars)
    config.sender_ready = True
    save_config(config)
    logger.info("Sender setup complete")

    widgets.banner("SETUP WIZARD", clear=True)
    widgets.blank()
    widgets.text("Sender setup completed (or already configured).")

    # --- Feed Setup ---
    logger.info(f"Feed setup starting in {PAUSE_SHORT}s")
    widgets.notify(f"Loading feed setup in {PAUSE_SHORT} seconds...")

    run_feed_manager()
    logger.info("Feed setup complete")

    widgets.banner("SETUP WIZARD", clear=True)
    widgets.blank()
    widgets.text("Feed setup completed.")

    # --- Recipient Setup ---
    logger.info(f"Recipient setup starting in {PAUSE_SHORT}s")
    widgets.notify(f"Loading recipient setup in {PAUSE_SHORT} seconds...")

    run_recipient_manager()
    logger.info("Recipient setup complete")

    widgets.banner("SETUP WIZARD", clear=True)
    widgets.blank()
    widgets.text("Recipient setup completed.")
    widgets.blank()
    widgets.notify("Setup complete!")
    logger.info("Setup wizard finished")