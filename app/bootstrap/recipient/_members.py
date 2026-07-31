from shared.pager import Pager
from shared.ui import screen, widgets
from shared.prompts import ask

MEMBERS_PER_PAGE = 10


def view_group_members(name: str, members: list[str]) -> None:
    """Paginated, read-only browse of a group's members."""
    pager = Pager(members, per_page=MEMBERS_PER_PAGE)

    while True:
        widgets.banner(f"GROUP: {name}", clear=True)
        widgets.blank()

        if pager.is_empty:
            widgets.text("(no members)")
        else:
            page_items, start = pager.get_page_items()
            widgets.enumerated_list(start + 1, page_items)
            widgets.blank()
            widgets.write(f"Page {pager.page}/{pager.max_page}", wrap=False)

        widgets.blank()
        screen.divider()
        widgets.blank()
        raw = ask("(N) Next page / (P) Previous page", cancel_word="back")

        if raw is None:
            return

        match raw.strip().upper():
            case "N": pager.next_page()
            case "P": pager.prev_page()