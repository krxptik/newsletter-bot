from models import AddressBook, Group
from shared.ui import screen, widgets


def header_str(n: int, group: Group) -> str:
    return f"[{n}] {group.name} ({len(group.members)} member{'s' if len(group.members) != 1 else ''})"


def group_headers(groups: list[Group]) -> list:
    return [
        (header_str(n, group), group.members)
        for n, group in enumerate(groups, 1)
    ]


def form_ungrouped(book: AddressBook) -> tuple[list, list]:
    labels, values = [], []
    for n, addr in enumerate(book.ungrouped, book.no_of_groups + 1):
        labels.append(f"[{n}]")
        values.append(addr)
    return labels, values


def display_groups(book: AddressBook, *, clear=False) -> None:
    if clear:
        screen.clear()
    widgets.section_header("GROUPS")
    widgets.blank()
    widgets.tree_list(group_headers(book.groups), empty_message="(none)")
    widgets.blank()


def display_ungrouped(book: AddressBook, clear=False) -> None:
    if clear:
        screen.clear()
    widgets.section_header("UNGROUPED")
    widgets.blank()
    widgets.label_block(*form_ungrouped(book), empty_message="(none)")
    widgets.blank()


def display_address_book(book: AddressBook) -> None:
    screen.clear()
    display_groups(book)
    display_ungrouped(book)
    screen.divider()