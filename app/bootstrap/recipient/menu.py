import logging

from ._display import display_address_book, display_groups
from ._handlers import add_group, remove_group, handle_view_members

from app.persistence import load_address_book
from models import AddressBook
from shared.ui import widgets, screen
from shared.prompts import select

logger = logging.getLogger(__name__)


def run_recipient_manager(book: AddressBook | None = None) -> None:
    logger.info(f"Running recipient manager")
    book = book or AddressBook.from_dict(load_address_book())
    options = ["Add group", "Remove group", "View group members", "Done"]

    while True:
        display_address_book(book, options)

        user_input = select(options)
        should_exit = _handle_user_input(user_input, book)

        if should_exit:
            break
        
    logger.info("Recipient manager exited")


def _handle_user_input(option: int | None, book: AddressBook) -> bool:
    match option:
        case 0: _flow(add_group, book)
        case 1: _flow(remove_group, book)
        case 2: _flow(handle_view_members, book)
        case 3: return True
    return False


def _flow(handler_fn, book: AddressBook) -> None:
    display_groups(book, clear=True)
    screen.divider()
    widgets.blank()
    handler_fn(book)