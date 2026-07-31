from enum import Enum

from ._draft import EmailDraft, SyncedRecipientList

from app.bootstrap.recipient import display_address_book
from models import AddressBook
from shared.ui import widgets
from shared.prompts import ask
from shared.email import is_valid_email
from shared.recipient_utils import prompt_group


class RecipientType(Enum):
    TO = "to"
    CC = "cc"
    BCC = "bcc"

    
class RecipientManager:
    def __init__(self, draft: EmailDraft, address_book: AddressBook):
        self.draft = draft
        self.book = address_book

    def add_individual(self, recipient_type: RecipientType) -> None:
        email = ask("Email address to add:", cancel_word="back")
        if email is None:
            return

        if not email or not is_valid_email(email):
            widgets.notify(f"ERROR: Invalid email: '{email}'.")
            return

        recipient_list = self.get_recipient_list(recipient_type)
        if email in self.draft.to_addrs or email in recipient_list:
            widgets.notify(f"'{email}' is already a recipient.")
            return

        recipient_list.append(email)

    def add_group(self, recipient_type: RecipientType) -> None:
        display_address_book(self.book, None)
        group = prompt_group(self.book, prompt="Group number or name to add:")
        if group is None:
            return

        recipient_list = self.get_recipient_list(recipient_type)
        if any(entry.upper() == group.name.upper() for entry in recipient_list):
            widgets.notify(f"Group '{group.name}' already in {recipient_type.value.title()}.")
            return

        recipient_list.append(group.name)

    def remove(self, recipient_type: RecipientType) -> None:
        item = ask("Email address or group to remove:", cancel_word="back")
        if item is None:
            return

        recipient_list = self.get_recipient_list(recipient_type)
        if item not in recipient_list:
            widgets.notify(f"'{item}' not found in {recipient_type.value.title()}.")
            return

        recipient_list.remove(item)

    def get_recipient_list(self, recipient_type: RecipientType) -> SyncedRecipientList:
        return getattr(self.draft, recipient_type.value)