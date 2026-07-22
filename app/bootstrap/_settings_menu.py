import logging
from enum import Enum, auto

from .ai import run_ai_settings
from .feed import run_feed_manager
from .recipient import run_recipient_manager
from .sender import run_sender_settings

from models.config import Config
from shared.ui import widgets, screen
from shared.prompts import select
from shared.exceptions import UserExitError

logger = logging.getLogger(__name__)


class State(Enum):
    MAIN = auto()
    SETTINGS = auto()


MENU_OPTIONS = {
    State.MAIN: ["Start", "Settings", "Exit"],
    State.SETTINGS: ["AI", "Sender", "Feeds", "Recipients", "Back"],
}


def _display_menu(title: str, options: list[str], config: Config | None = None) -> None:
    if config is None:
        widgets.banner(title, clear=True)
        widgets.blank()
        widgets.options_menu(options)
        return

    widgets.banner_figlet(title)
    widgets.blank()
    widgets.dot_leader_list(config.display_data())
    widgets.blank()
    screen.divider()
    widgets.blank()
    widgets.options_menu(options)


def _handle_main_input(option: int | None) -> State | None:
    match option:
        case 0:
            logger.info("User selected Start")
            return None
        case 1:
            logger.info("User entered Settings")
            return State.SETTINGS
        case 2:
            logger.info("User selected Exit")
            raise UserExitError("Exited from main menu.")
    return State.MAIN


def _handle_settings_input(option: int | None) -> State:
    match option:
        case 0:
            run_ai_settings()
        case 1:
            run_sender_settings()
        case 2:
            run_feed_manager()
        case 3:
            run_recipient_manager()
        case 4:
            return State.MAIN
    return State.SETTINGS


def run_main_menu(config: Config) -> None:
    logger.info("Main menu opened")
    state = State.MAIN

    while state is not None:
        options = MENU_OPTIONS[state]
        if state == State.MAIN:
            _display_menu("ellie!", options, config)
            widgets.blank()
            state = _handle_main_input(select(options))
        else:
            _display_menu("SETTINGS", options)
            widgets.blank()
            state = _handle_settings_input(select(options))

    logger.info("Main menu exited — continuing to program")