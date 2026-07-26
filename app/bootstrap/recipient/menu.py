import logging

from ._display import display_address_book, display_groups, display_ungrouped
from ._handlers import add_group, remove_group, add_ungrouped, remove_ungrouped, handle_view_members

from app.persistence import load_address_book
from models import AddressBook
from shared.ui import widgets, screen
from shared.prompts import select

logger = logging.getLogger(__name__)


def _flow(display_fn, handler_fn, book: AddressBook) -> None:
    display_fn(book, clear=True)
    screen.divider()
    widgets.blank()
    handler_fn(book)
    


def _handle_user_input(user_input: int | None, book: AddressBook) -> bool:
    match user_input:
        case 0:
            _flow(display_groups, add_group, book)
        case 1:
            _flow(display_groups, remove_group, book)
        case 2:
            _flow(display_ungrouped, add_ungrouped, book)
        case 3:
            _flow(display_ungrouped, remove_ungrouped, book)
        case 4:
            _flow(display_groups, handle_view_members, book)
        case 5:
            logger.info("Recipient manager exited")
            return True
    return False


def run_recipient_manager() -> None:
    logger.info(f"Running recipient manager")
    data = load_address_book()
    book = AddressBook.from_dict(data)
    options = [
        "Add group", "Remove group",
        "Add ungrouped recipient", "Remove ungrouped recipient",
        "View group members", "Done",
    ]

    while True:
        display_address_book(book, options)

        user_input = select(options)
        should_exit = _handle_user_input(user_input, book)

        if should_exit:
            break
        
    logger.info("Recipient manager exited")

        
if __name__ == "__main__":
    run_recipient_manager()