import logging
from enum import Enum, auto
from email.message import EmailMessage
import os
import time

from shared.terminal import clear_terminal, divider, display_banner, label_line
from app.render.render import preview_newsletter
from app.persistence.email_addrs_store import load_address_book
from app.bootstrap.recipient_manager import run_recipient_manager

logger = logging.getLogger(__name__)


class State(Enum):
    MAIN = auto()
    EDIT = auto()
    MANAGE_RECIPIENTS = auto()
    ADDRESS_BOOK = auto()


class MenuHandler:
    def __init__(self, subject: str, path: str, html: str):
        self.state = State.MAIN
        self.path = path
        self.to_addrs = set()
        self.em = EmailMessage()
        self.current_recipient_type: str | None = None
        self.addrs_names = {
            "To": [],
            "Cc": [],
            "Bcc": []
        }

        data = load_address_book()
        self.groups = data.get("groups", {})
        self.ungrouped = data.get("ungrouped", [])

        self.em['Subject'] = subject
        self.em['From'] = os.getenv("EMAIL_ADDRESS")
        self.em.set_content(
            "This email contains HTML elements. "
            "If you are seeing this, the email is not loading properly. "
            "Please view this in a proper email client."
        )
        self.em.add_alternative(html, subtype='html')

    # --- Reload address book after external edits ---

    def _reload_address_book(self) -> None:
        data = load_address_book()
        self.groups = data.get("groups", {})
        self.ungrouped = data.get("ungrouped", [])
        logger.debug("Address book reloaded into send menu handler")

    # --- Main menu ---

    def handle_main_input(self, user_input: str) -> None:
        if not user_input.isdigit():
            return
        option = int(user_input)
        if option == 1:
            self.state = State.EDIT
        elif option == 2:
            preview_newsletter(self.path)
        elif option == 3:
            if self.em.get('Subject') and self.em.get('From') and len(self.to_addrs) > 0:
                self.state = None
            else:
                self._show_error('Necessary email details empty, please fill them in.')

    # --- Edit menu ---

    def handle_edit_input(self, user_input: str) -> None:
        if not user_input.isdigit():
            return
        option = int(user_input)
        if option == 1:
            new = input("New subject: ").strip()
            if new:
                self._set_header('Subject', new)
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

    # --- Recipient management menu ---

    def handle_recipient_input(self, user_input: str) -> None:
        if not user_input.isdigit():
            return
        option = int(user_input)
        rt = self.current_recipient_type
        if option == 1:
            self._add_individual(rt)
        elif option == 2:
            self._add_group(rt)
        elif option == 3:
            self._remove_individual(rt)
        elif option == 4:
            self._remove_group(rt)
        elif option == 5:
            self.state = State.ADDRESS_BOOK
        elif option == 6:
            self.state = State.EDIT

    # --- Add / remove ---

    def _add_individual(self, recipient_type: str) -> None:
        email = input("Email address to add: ").strip()
        if not email:
            return
        if email in self.to_addrs:
            self._show_error(f"'{email}' is already a recipient.")
            return
        self.addrs_names[recipient_type].append(email)
        self._set_header(recipient_type, ', '.join(self.addrs_names[recipient_type]))
        self.to_addrs.add(email)

    def _add_group(self, recipient_type: str) -> None:
        name = input("Group name to add: ").strip().upper()
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
        self._set_header(recipient_type, ', '.join(self.addrs_names[recipient_type]))
        self.to_addrs.update(addrs)

    def _remove_individual(self, recipient_type: str) -> None:
        email = input("Email address to remove: ").strip()
        if email in self.to_addrs:
            self.to_addrs.remove(email)
            self.addrs_names[recipient_type].remove(email)
            self._set_header(recipient_type, ', '.join(self.addrs_names[recipient_type]))
        else:
            self._show_error(f"'{email}' not found in {recipient_type}.")

    def _remove_group(self, recipient_type: str) -> None:
        name = input("Group name to remove: ").strip().upper()
        addrs = self.groups.get(name)
        if addrs is None:
            self._show_error(f"Group '{name}' not found in address book.")
            return
        if name not in self.addrs_names[recipient_type]:
            self._show_error(f"Group '{name}' not in {recipient_type}.")
            return
        self.to_addrs -= set(addrs)
        self.addrs_names[recipient_type].remove(name)
        self._set_header(recipient_type, ', '.join(self.addrs_names[recipient_type]))

    # --- Helpers ---

    def _show_error(self, message: str) -> None:
        clear_terminal()
        print(message)
        print("\nReturning to menu in 3 seconds...")
        time.sleep(3)

    def _set_header(self, header: str, value: str) -> None:
        if header in self.em:
            self.em.replace_header(header, value)
        else:
            self.em[header] = value


# ===== DISPLAY =====

def _display_address_book(groups: dict, ungrouped: list) -> None:
    print("Address book:")
    if groups:
        for name, members in groups.items():
            print(f"  [{name}] — {len(members)} member(s)")
            for m in members:
                print(f"    - {m}")
    else:
        print("  (no groups)")

    if ungrouped:
        print("\n  Ungrouped:")
        for addr in ungrouped:
            print(f"    - {addr}")
    else:
        print("  (no ungrouped recipients)")

    divider(spacing=True)


def display_details(em: EmailMessage) -> None:
    clear_terminal()
    display_banner("EMAIL DETAILS")
    print()
    print(label_line("Subject:", str(em.get('Subject'))))
    print(label_line("From:", str(em.get('From'))))
    print(label_line("To:", str(em.get('To'))))
    print(label_line("Cc:", str(em.get('Cc'))))
    print(label_line("Bcc:", str(em.get('Bcc'))))
    divider(spacing=True)


# ===== ENTRY POINT =====

def send_menu(subject: str, path: str, html: str):
    handler = MenuHandler(subject, path, html)

    while handler.state is not None:
        clear_terminal()

        if handler.state == State.MAIN:
            display_details(handler.em)
            print("\nOptions:")
            print("  (1) Edit details")
            print("  (2) Preview HTML")
            print("  (3) Submit and send")
            handler.handle_main_input(input("\n> ").strip())

        elif handler.state == State.EDIT:
            display_details(handler.em)
            print("\nOptions:")
            print("  (1) Edit subject")
            print("  (2) Manage To")
            print("  (3) Manage Cc")
            print("  (4) Manage Bcc")
            print("  (5) Back")
            handler.handle_edit_input(input("\n> ").strip())

        elif handler.state == State.MANAGE_RECIPIENTS:
            display_details(handler.em)
            _display_address_book(handler.groups, handler.ungrouped)
            print(f"Managing: {handler.current_recipient_type}")
            print("\nOptions:")
            print("  (1) Add individual")
            print("  (2) Add group")
            print("  (3) Remove individual")
            print("  (4) Remove group")
            print("  (5) Edit address book")
            print("  (6) Back")
            handler.handle_recipient_input(input("\n> ").strip())

        elif handler.state == State.ADDRESS_BOOK:
            run_recipient_manager(title="EDIT ADDRESS BOOK")
            time.sleep(3)
            handler._reload_address_book()
            handler.state = State.MANAGE_RECIPIENTS

    return (handler.em, list(handler.to_addrs))