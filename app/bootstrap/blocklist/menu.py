import logging

from ._display import display_blocklist
from ._handlers import handle_view_blocklist, remove_domain, remove_path

from app.persistence import load_domain_blocklist
from shared.ui import widgets, screen
from shared.prompts import select

logger = logging.getLogger(__name__)


def run_blocklist_manager() -> None:
    logger.info("Running blocklist manager")
    blocklist = load_domain_blocklist()
    options = ["Remove domain", "Remove path", "View domain blocklist", "Done"]

    while True:
        display_blocklist(blocklist, options)

        user_input = select(options)
        should_exit = _handle_user_input(user_input, blocklist)

        if should_exit:
            break

    logger.info("Blocklist manager exited")


def _handle_user_input(option: int | None, blocklist: dict[str, list[str]]) -> bool:
    match option:
        case 0: _flow(remove_domain, blocklist)
        case 1: _flow(remove_path, blocklist)
        case 2: _flow(handle_view_blocklist, blocklist)
        case 3: return True
    return False


def _flow(handler_fn, blocklist: dict[str, list[str]]) -> None:
    display_blocklist(blocklist, clear=True)
    screen.divider()
    widgets.blank()
    handler_fn(blocklist)