import logging

from ._members import view_group_members

from app.persistence import save_address_book
from models import AddressBook
from shared.email import is_valid_email
from shared.ui import widgets
from shared.prompts import ask, confirmation
from shared.recipient_utils import prompt_group

logger = logging.getLogger(__name__)


def add_group(book: AddressBook) -> None:
    # ===== Group.name =====
    name = ask("Group name:", cancel_word="back")
    if name is None:
        return
    if not name:
        widgets.notify(f"ERROR: Empty user input.")
        return
    if book.group_exists(name):
        widgets.notify(f"ERROR: Group '{name}' already exists.")
        return

    # ===== Group.members =====
    emails_raw = ask("Enter emails separated by commas:", cancel_word="back")
    if emails_raw is None:
        return
    emails = [e.strip() for e in emails_raw.split(",") if e.strip()]

    filtered_emails = [e for e in emails if is_valid_email(e)]
    if not filtered_emails:
        widgets.notify("ERROR: No valid emails entered, group not created.")
        return
    if len(filtered_emails) < len(emails):
        widgets.notify("WARNING: Some invalid emails were entered and not added to the group. Please check.")

    # ===== Add and save group =====
    book.add_group(name, filtered_emails)
    _persist(book)
    logger.info(f"Added group '{name}' with {len(filtered_emails)} member(s)")
    widgets.notify(f"Group '{name}' added.")
    return


def remove_group(book: AddressBook) -> None:
    group = prompt_group(book, "Group number or name to remove:")
    if group is None:
        return

    if not confirmation(f"Remove group '{group.name}'?"):
        widgets.notify("Cancelled.")
        return

    book.remove_group(group)
    _persist(book)
    logger.info(f"Removed group '{group.name}'")
    widgets.notify(f"Group '{group.name}' removed.")
    return


def handle_view_members(book: AddressBook) -> None:
    group = prompt_group(book, "Group number or name to view:")
    if group is None:
        return
    view_group_members(group.name, group.members)


def _persist(book: AddressBook) -> None:
    save_address_book(book.to_dict())