from typing import TYPE_CHECKING

from ._display import display_details, display_recipient_detail
from ._state import State

from app.bootstrap.recipient import run_recipient_manager
from shared.ui import widgets
from shared.prompts import select

if TYPE_CHECKING:
    from ._controller import MenuController

MAIN_OPTIONS = ["Edit details", "Preview HTML", "Submit and send"]
EDIT_OPTIONS = ["Edit subject", "Manage 'To'", "Manage 'Cc'", "Manage 'Bcc'", "Back"]
RECIPIENT_OPTIONS = ["Add individual", "Add group", "Remove individual or group", "Edit address book", "Back"]


def show_main_menu(controller: "MenuController") -> None:
    display_details(controller.draft)
    widgets.blank()
    widgets.options_menu(MAIN_OPTIONS)
    widgets.blank()
    controller.handle_main_input(select(MAIN_OPTIONS))


def show_edit_menu(controller: MenuController) -> None:
    display_details(controller.draft)
    widgets.blank()
    widgets.options_menu(EDIT_OPTIONS)
    widgets.blank()
    controller.handle_edit_input(select(EDIT_OPTIONS))


def show_recipient_menu(controller: MenuController) -> None:
    if controller.recipient_type is None:
        controller.state = State.EDIT
        return

    display_recipient_detail(controller.draft, controller.recipient_type)

    is_empty = not controller.recipient_manager.get_recipient_list(controller.recipient_type)
    options = [o for o in RECIPIENT_OPTIONS if not (is_empty and o == "Remove individual or group")]

    widgets.blank()
    widgets.options_menu(options)
    widgets.blank()

    choice = select(options)
    if isinstance(choice, int):
        controller.handle_recipient_input(options[choice])


def show_address_book(controller: MenuController):
    run_recipient_manager(controller.book)
    controller.state = State.MANAGE_RECIPIENTS