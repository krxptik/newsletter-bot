from ._controller import MenuController
from ._state import State
from ._views import show_main_menu, show_edit_menu, show_recipient_menu, show_address_book

from shared.ui import screen


def send_menu(subject, path, html):
    controller = MenuController(subject, path, html)

    while controller.state:
        screen.clear()

        match controller.state:
            case State.MAIN: show_main_menu(controller)
            case State.EDIT: show_edit_menu(controller)
            case State.MANAGE_RECIPIENTS: show_recipient_menu(controller)
            case State.ADDRESS_BOOK: show_address_book(controller)
    
    return controller.result()