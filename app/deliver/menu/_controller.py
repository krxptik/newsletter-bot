import logging
import os
import time
from email.message import EmailMessage
from pathlib import Path

from app.persistence import load_address_book
from app.render import preview_newsletter
from shared.ui import screen, widgets

from ._state import State

logger = logging.getLogger(__name__)


class MenuHandler:
    def __init__(self, subject: str, path: Path, html: str):
        self.state = State.MAIN
        self.path = path
        self.to_addrs = set()
        self.em = EmailMessage()
        self.current_recipient_type: str | None = None
        self.addrs_names = {
            "To": [],
            "Cc": [],
            "Bcc": [],
        }

        data = load_address_book()
        self.groups = data.get("groups", {})
        self.ungrouped = data.get("ungrouped", [])

        self.em["Subject"] = subject
        self.em["From"] = os.getenv("EMAIL_ADDRESS")
        self.em.set_content(
            "This email contains HTML elements. "
            "If you are seeing this, the email is not loading properly. "
            "Please view this in a proper email client."
        )
        self.em.add_alternative(html, subtype="html")

    def _reload_address_book(self) -> None:
        data = load_address_book()
        self.groups = data.get("groups", {})
        self.ungrouped = data.get("ungrouped", [])
        logger.debug("Address book reloaded into send menu handler")

    def handle_main_input(self, user_input: str) -> None:
        if not user_input.isdigit():
            return
        option = int(user_input)
        if option == 1:
            self.state = State.EDIT
        elif option == 2:
            preview_newsletter(self.path)
        elif option == 3:
            if self.em.get("Subject") and self.em.get("From") and len(self.to_addrs) > 0:
                self.state = None
            else:
                self._show_error("Necessary email details empty, please fill them in.")

    def handle_edit_input(self, user_input: str) -> None:
        if not user_input.isdigit():
            return
        option = int(user_input)
        if option == 1:
            new = widgets.m_input("New subject: ").strip()
            if new:
                self._set_header("Subject", new)
        elif option == 2:
            self.current_recipient_type = "To"
            self.state = State.MANAGE_RECIPIENTS
        elif option == 3:
            self.current_recipient_type = "Cc"
            self.state = State.MANAGE_RECIPIENTS
        elif option == 4:
            self.current_recipient_type = "Bcc"
            self.state = State.MANAGE_RECIPIENTS
        elif option == 5:
            self.state = State.MAIN

    def handle_recipient_input(self, user_input: str) -> None:
        if not user_input.isdigit():
            return
        option = int(user_input)
        if self.current_recipient_type is None:
            return

        recipient_type = self.current_recipient_type
        if option == 1:
            self._add_individual(recipient_type)
        elif option == 2:
            self._add_group(recipient_type)
        elif option == 3:
            self._remove_individual(recipient_type)
        elif option == 4:
            self._remove_group(recipient_type)
        elif option == 5:
            self.state = State.ADDRESS_BOOK
        elif option == 6:
            self.state = State.EDIT

    def _add_individual(self, recipient_type: str) -> None:
        email = widgets.m_input("Email address to add: ").strip()
        if not email:
            return
        if email in self.to_addrs:
            self._show_error(f"'{email}' is already a recipient.")
            return
        self.addrs_names[recipient_type].append(email)
        self._set_header(recipient_type, ", ".join(self.addrs_names[recipient_type]))
        self.to_addrs.add(email)

    def _add_group(self, recipient_type: str) -> None:
        name = widgets.m_input("Group name to add: ").strip().upper()
        if not name:
            return
        addrs = self.groups.get(name)
        if addrs is None:
            self._show_error(f"Group '{name}' not found in address book.")
            return
        if name in self.addrs_names[recipient_type]:
            self._show_error(f"Group '{name}' already in {recipient_type}.")
            return
        self.addrs_names[recipient_type].append(name)
        self._set_header(recipient_type, ", ".join(self.addrs_names[recipient_type]))
        self.to_addrs.update(addrs)

    def _remove_individual(self, recipient_type: str) -> None:
        email = widgets.m_input("Email address to remove: ").strip()
        if email in self.to_addrs:
            self.to_addrs.remove(email)
            self.addrs_names[recipient_type].remove(email)
            self._set_header(recipient_type, ", ".join(self.addrs_names[recipient_type]))
        else:
            self._show_error(f"'{email}' not found in {recipient_type}.")

    def _remove_group(self, recipient_type: str) -> None:
        name = widgets.m_input("Group name to remove: ").strip().upper()
        addrs = self.groups.get(name)
        if addrs is None:
            self._show_error(f"Group '{name}' not found in address book.")
            return
        if name not in self.addrs_names[recipient_type]:
            self._show_error(f"Group '{name}' not in {recipient_type}.")
            return
        self.to_addrs -= set(addrs)
        self.addrs_names[recipient_type].remove(name)
        self._set_header(recipient_type, ", ".join(self.addrs_names[recipient_type]))

    def _show_error(self, message: str) -> None:
        screen.clear()
        print(message)
        print("\nReturning to menu in 3 seconds...")
        time.sleep(3)

    def _set_header(self, header: str, value: str) -> None:
        if header in self.em:
            self.em.replace_header(header, value)
        else:
            self.em[header] = value