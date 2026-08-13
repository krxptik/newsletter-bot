from shared.core import Pager
from shared.ui import screen, widgets
from shared.prompts import ask

BLOCKLIST_ITEMS_PER_PAGE = 10


def view_domain_blocklist(domain: str, paths: list[str]) -> None:
    """Paginated, read-only browse of a domain's blocked paths."""
    pager = Pager(paths, per_page=BLOCKLIST_ITEMS_PER_PAGE)

    while True:
        widgets.banner(f"DOMAIN: {domain}", clear=True)
        widgets.blank()

        if pager.is_empty:
            widgets.text("(no blocked paths)")
        else:
            page_items, start = pager.get_page_items()
            widgets.enumerated_list(start + 1, page_items)
            widgets.blank()
            widgets.write(f"Page {pager.page}/{pager.max_page}", wrap=False)

        widgets.blank()
        screen.divider()
        widgets.blank()

        if pager.max_page <= 1:
            widgets.m_input("Press 'enter' to go back.")
            return 

        raw = ask("(N) Next page / (P) Previous page", cancel_word="back")
        if raw is None:
            return

        match raw.strip().upper():
            case "N": pager.next_page()
            case "P": pager.prev_page()
