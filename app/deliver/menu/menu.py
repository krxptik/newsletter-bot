import time

from app.bootstrap.recipient import run_recipient_manager
from pathlib import Path
from shared.ui import screen, widgets

from ._controller import MenuHandler
from ._display import display_address_book, display_details
from ._state import State


# ===== ENTRY POINT =====

def send_menu(subject: str, path: Path, html: str):
    handler = MenuHandler(subject, path, html)

    while handler.state is not None:
        screen.clear()

        if handler.state == State.MAIN:
            display_details(handler.em)
            print("\nOptions:")
            print("  (1) Edit details")
            print("  (2) Preview HTML")
            print("  (3) Submit and send")
            handler.handle_main_input(widgets.m_input("> ").strip())

        elif handler.state == State.EDIT:
            display_details(handler.em)
            print("\nOptions:")
            print("  (1) Edit subject")
            print("  (2) Manage To")
            print("  (3) Manage Cc")
            print("  (4) Manage Bcc")
            print("  (5) Back")
            handler.handle_edit_input(widgets.m_input("> ").strip())

        elif handler.state == State.MANAGE_RECIPIENTS:
            display_details(handler.em)
            display_address_book(handler.groups, handler.ungrouped)
            print(f"Managing: {handler.current_recipient_type}")
            print("\nOptions:")
            print("  (1) Add individual")
            print("  (2) Add group")
            print("  (3) Remove individual")
            print("  (4) Remove group")
            print("  (5) Edit address book")
            print("  (6) Back")
            handler.handle_recipient_input(widgets.m_input("> ").strip())

        elif handler.state == State.ADDRESS_BOOK:
            run_recipient_manager()
            time.sleep(3)
            handler._reload_address_book()
            handler.state = State.MANAGE_RECIPIENTS

    return (handler.em, list(handler.to_addrs))