import logging
import os
from pathlib import Path

from ._state import State
from ._draft import EmailDraft
from ._recipient import RecipientManager, RecipientType

from app.persistence import load_address_book
from app.render import preview_newsletter
from models import AddressBook
from shared.ui import widgets

logger = logging.getLogger(__name__)

EMAIL_BODY = (
    "This email contains HTML elements. "
    "If you are seeing this, the email is not loading properly. "
    "Please view this in a proper email client."
)


class MenuController:
    def __init__(self, subject: str, path: Path, html: str):
        self.state = State.MAIN
        self.path = path

        self.book = AddressBook.from_dict(load_address_book())

        self.draft = EmailDraft(
            subject, 
            os.getenv("EMAIL_ADDRESS"), 
            address_book=self.book
        )

        self.draft.set_text(EMAIL_BODY)
        self.draft.set_html(html) 

        self.recipient_type = None

        self.recipient_manager = RecipientManager(
            self.draft,
            self.book,
        )

    def handle_main_input(self, option: int | None) -> None:
        def confirm_details():
            if self.draft.subject and self.draft.from_ and not self.draft.is_recipients_empty():
                self.state = None
            else:
                widgets.notify("Necessary email details empty, please fill them in.")

        match option:
            case 0: self.state = State.EDIT
            case 1: preview_newsletter(self.path)
            case 2: confirm_details()

    def handle_edit_input(self, option: int | None) -> None:
        match option:
            case 0: self.draft.edit_subject()
            case 1: self._open_recipient(RecipientType.TO)
            case 2: self._open_recipient(RecipientType.CC)
            case 3: self._open_recipient(RecipientType.BCC)
            case 4: self.state = State.MAIN

    def handle_recipient_input(self, label: str) -> None:
        if self.recipient_type is None:
            return
        match label:
            case "Add individual": self.recipient_manager.add_individual(self.recipient_type)
            case "Add group": self.recipient_manager.add_group(self.recipient_type)
            case "Remove individual or group": self.recipient_manager.remove(self.recipient_type)
            case "Edit address book": self.state = State.ADDRESS_BOOK
            case "Back": self.state = State.EDIT

    def result(self):
        return self.draft.em, list(self.draft.to_addrs)

    def _open_recipient(self, recipient_type: RecipientType):
        self.recipient_type = recipient_type
        self.state = State.MANAGE_RECIPIENTS