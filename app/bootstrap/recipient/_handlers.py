import logging
import time

from ._members import view_group_members

from app.persistence import save_address_book
from models import AddressBook
from shared.email import is_valid_email
from shared.ui import widgets, PAUSE_SHORT
from shared.prompts import ask, confirmation

logger = logging.getLogger(__name__)


def _persist(book: AddressBook) -> None:
    save_address_book(book.to_dict())


def _notify(message: str) -> None:
    widgets.text(message)
    time.sleep(PAUSE_SHORT)


def _prompt_group(book: AddressBook, prompt: str = "Group number or name:") -> tuple[str, int] | None:
    raw = ask(prompt, cancel_word="back")
    if not raw:
        return None
    result = book.resolve_group(raw)
    if result is None:
        _notify(f"ERROR: Group not found: '{raw}'.")
        return None
    return result


def add_group(book: AddressBook) -> bool:
    # ===== Group.name =====
    name = ask("Group name:", cancel_word="back")
    if not name:
        return False
    if book.group_exists(name):
        _notify(f"ERROR: Group '{name}' already exists.")
        return False

    # ===== Group.members =====
    emails_raw = ask("Enter emails separated by commas:", cancel_word="back")
    if emails_raw is None:
        return False
    emails = [e.strip() for e in emails_raw.split(",") if e.strip()]

    filtered_emails = [e for e in emails if is_valid_email(e)]
    if not filtered_emails:
        _notify("ERROR: No valid emails entered, group not created.")
        return False
    if len(filtered_emails) < len(emails):
        _notify("WARNING: Some invalid emails were entered and not added to the group. Please check.")

    # ===== Add and save group =====
    book.add_group(name, filtered_emails)
    _persist(book)
    logger.info(f"Added group '{name}' with {len(filtered_emails)} member(s)")
    _notify(f"Group '{name}' added.")
    return True


def remove_group(book: AddressBook) -> bool:
    result = _prompt_group(book, "Group number or name to remove:")
    if result is None:
        return False
    name, index = result

    if not confirmation(f"Remove group '{name}'?"):
        _notify("Cancelled.")
        return False

    book.remove_group(index)
    _persist(book)
    logger.info(f"Removed group '{name}'")
    _notify(f"Group '{name}' removed.")
    return True


def add_ungrouped(book: AddressBook) -> None:
    email = ask("Email to add:", cancel_word="back")
    if email is None:
        return
    if not email or not is_valid_email(email):
        _notify(f"ERROR: Invalid email: '{email}'.")
        return
    if book.ungrouped_exists(email):
        _notify(f"ERROR: '{email}' already in ungrouped.")
        return
    
    book.add_ungrouped(email)
    _persist(book)
    logger.info(f"Added ungrouped recipient '{email}'")
    _notify(f"'{email}' added.")


def remove_ungrouped(book: AddressBook) -> None:
    raw = ask("Number or email to remove:", cancel_word="back")
    if not raw:
        return
    
    email = book.resolve_ungrouped(raw)
    if email is None:
        _notify(f"ERROR: Not found in ungrouped: '{raw}'.")
        return
    
    book.remove_ungrouped(email)
    _persist(book)
    logger.info(f"Removed ungrouped recipient '{email}'")
    _notify(f"'{email}' removed.")


def handle_view_members(book: AddressBook) -> None:
    result = _prompt_group(book, "Group number or name to view:")
    if result is None:
        return
    name, index = result
    view_group_members(name, book.groups[index].members)