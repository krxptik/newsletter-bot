import logging
from enum import Enum, auto
from typing import TYPE_CHECKING

from shared.terminal import display_banner_figlet, display_banner, divider, label_block, clear_terminal
from app.bootstrap.settings.ai_settings import run_ai_settings
from app.bootstrap.settings.sender_settings import run_sender_settings
from app.bootstrap.settings.feed_settings import run_feed_settings
from app.bootstrap.recipient_manager import run_recipient_manager

if TYPE_CHECKING:
    from app.bootstrap.config_state_handler import Config

logger = logging.getLogger(__name__)


class UserExitError(Exception):
    """Raised when the user chooses to exit from the main menu."""
    pass


class State(Enum):
    MAIN = auto()
    SETTINGS = auto()


# ===== DISPLAY =====

def _display_main_menu(config: "Config") -> None:
    display_banner_figlet("ellie!")
    _display_config_status(config)
    divider(single=True, spacing=True)
    print("Options:")
    print("  (1) Start")
    print("  (2) Settings")
    print("  (3) Exit")


def _display_settings_menu() -> None:
    clear_terminal()
    display_banner("SETTINGS")
    print()
    print("Options:")
    print("  (1) AI")
    print("  (2) Sender")
    print("  (3) Feeds")
    print("  (4) Recipients")
    print("  (5) Back")


def _display_config_status(config: "Config") -> None:
    ready = "Ready"
    not_ready = "Not ready"

    labels = ["AI:", "Sender:", "Feeds:", "Recipients:"]
    values = [
        ready if config.ai_ready else not_ready,
        ready if config.sender_ready else not_ready,
        ready if config.feeds_ready else not_ready,
        ready if config.recipients_ready else not_ready,
    ]

    print()
    print(label_block(labels, values, justify="right"))


# ===== INPUT HANDLERS =====

def _handle_main_input(user_input: str, state_holder: list) -> None:
    if not user_input.isdigit():
        return
    option = int(user_input)
    if option == 1:
        logger.info("User selected Start")
        state_holder[0] = None
    elif option == 2:
        logger.info("User entered Settings")
        state_holder[0] = State.SETTINGS
    elif option == 3:
        logger.info("User selected Exit")
        raise UserExitError("Exited from main menu.")


def _handle_settings_input(user_input: str, state_holder: list) -> None:
    if not user_input.isdigit():
        return
    option = int(user_input)
    if option == 1:
        run_ai_settings()
    elif option == 2:
        run_sender_settings()
    elif option == 3:
        run_feed_settings()
    elif option == 4:
        run_recipient_manager(title="ADDRESS BOOK SETTINGS")
    elif option == 5:
        state_holder[0] = State.MAIN


# ===== ENTRY POINT =====

def run_main_menu(config: "Config") -> None:
    logger.info("Main menu opened")
    state_holder = [State.MAIN]

    while state_holder[0] is not None:
        if state_holder[0] == State.MAIN:
            _display_main_menu(config)
            _handle_main_input(input("\n> ").strip(), state_holder)
        elif state_holder[0] == State.SETTINGS:
            _display_settings_menu()
            _handle_settings_input(input("\n> ").strip(), state_holder)

    logger.info("Main menu exited — continuing to program")