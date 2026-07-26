from models import Article
from shared.ui import widgets, screen
from shared.pager import Pager


def display_selection_menu(available: Pager, selected: Pager, options: list[str]) -> None:
    a_items, a_start = available.get_page_items()
    s_items, s_start = selected.get_page_items()
    a_list = [a.name for a in a_items]
    s_list = [s.name for s in s_items]

    screen.clear()
    with widgets.capture_panel() as left:
        widgets.section_header("AVAILABLE ARTICLES")
        widgets.blank()
        widgets.enumerated_list(a_start+1, a_list, empty_message="No available articles.", overflow="truncate")
        widgets.blank()
        if available.max_page > 1:
            widgets.text(f"Page {available.page}/{available.max_page}")

    with widgets.capture_panel() as right:
        widgets.section_header("SELECTED")
        widgets.blank()
        widgets.enumerated_list(s_start+1, s_list, empty_message="No selected articles.", overflow="truncate")
        widgets.blank()
        if selected.max_page > 1:
            widgets.text(f"Page {selected.page}/{selected.max_page}")

    left_text = left.getvalue().splitlines()
    right_text = right.getvalue().splitlines()

    widgets.two_panels(left_text, right_text)

    footer = "\n".join([
        "[<] / [>] to navigate available articles",
        "[<<] / [>>] to navigate selected articles"
    ])
    widgets.blank()
    widgets.options_menu(options, footer=footer)
    widgets.blank()


def display_article_list(pager: Pager, letters: bool = False, empty_message: str = "Nothing to show."):
    items, start = pager.get_page_items()
    item_list = [a.name for a in items]
    screen.divider()
    widgets.blank()
    widgets.enumerated_list(start+1, item_list, letters=letters, empty_message=empty_message)
    widgets.blank()
    screen.divider()
    widgets.blank()
    

def display_article_details(article: Article) -> None:
    pub_date = article.pub_date.strftime('%d/%m/%Y') if article.pub_date else 'Not set'
    tags = ', '.join(article.tags or [])

    screen.divider()
    labels = ["Title:", "Date:", "Source:", "Link:", "Tags:", "Summary:"]
    values = [article.title, pub_date, article.source, article.link, tags, article.summary]
    widgets.label_block(labels, values)
    screen.divider()


def display_confirm(selected: Pager) -> None:
    screen.clear()
    widgets.section_header("SELECTED ARTICLES")
    widgets.enumerated_list(1, selected.items)
    screen.divider()