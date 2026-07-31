from models import AddressBook, Group
from shared.ui import screen, widgets


def header_str(n: int, group: Group) -> str:
    return f"[{n}] {group.name} ({len(group.members)} member{'s' if len(group.members) != 1 else ''})"


def group_headers(groups: list[Group]) -> list:
    return [
        (header_str(n, group), group.members)
        for n, group in enumerate(groups, 1)
    ]


def display_groups(book: AddressBook, *, clear=False) -> None:
    if clear:
        screen.clear()
    widgets.section_header("GROUPS")
    widgets.blank()
    widgets.tree_list(group_headers(book.groups), empty_message="(none)")
    widgets.blank()


def display_address_book(book: AddressBook, options: list | None = None, clear: bool = True) -> None:
    if clear:
        screen.clear()
    display_groups(book)
    screen.divider()
    widgets.blank()
    if options:
        widgets.options_menu(options)
        widgets.blank()