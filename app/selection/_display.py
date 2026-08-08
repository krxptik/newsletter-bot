from models import Article
from shared.ui import widgets, screen
from shared.core import Pager


def _list_info(pager: Pager):
    items, start = pager.get_page_items()
    titles = [a.title for a in items]
    list_height = len(titles) if titles else 1
    footer_height = 2 if pager.max_page > 1 else 0
    return titles, start, list_height, footer_height


def _render_panel(title: str, titles: list[str], start: int, pager: Pager, list_height: int, footer_height: int, target_height: int, empty_message: str, letters: bool = False):
    widgets.section_header(title)
    widgets.blank()
    widgets.enumerated_list(start + 1, titles, empty_message=empty_message, overflow="truncate", letters=letters)
    widgets.blank()
    if pager.max_page > 1:
        widgets.text(f"[Page {pager.page}/{pager.max_page}]")
        widgets.blank()
    pad = target_height - (list_height + footer_height)
    if pad > 0:
        widgets.blank(pad)
    screen.divider()


def display_all_articles(available: Pager, selected: Pager) -> None:
    a_titles, a_start, a_list_height, a_footer_height = _list_info(available)
    s_titles, s_start, s_list_height, s_footer_height = _list_info(selected)
    target_height = max(a_list_height + a_footer_height, s_list_height + s_footer_height)

    screen.clear()
    with widgets.capture_panel() as left:
        _render_panel("AVAILABLE ARTICLES", a_titles, a_start, available, a_list_height, a_footer_height, target_height, "No available articles.", letters=False)

    with widgets.capture_panel() as right:
        _render_panel("SELECTED", s_titles, s_start, selected, s_list_height, s_footer_height, target_height, "No selected articles.")

    widgets.two_panels(left, right)


def display_options(options: list[str]) -> None:
    footer = "\n".join([
        "[<] / [>] to navigate available articles",
        "[<<] / [>>] to navigate selected articles",
    ])
    widgets.blank()
    widgets.options_menu(options, footer=footer)
    widgets.blank()


def display_article_list(pager: Pager, letters: bool = False, empty_message: str = "Nothing to show."):
    titles, start, _, _ = _list_info(pager)
    screen.clear()
    screen.divider()
    widgets.blank()
    widgets.enumerated_list(start + 1, titles, letters=letters, empty_message=empty_message)
    widgets.blank()
    screen.divider()
    widgets.blank()


def display_article_details(article: Article) -> None:
    pub_date = article.pub_date.strftime("%d/%m/%Y") if article.pub_date else "Not set"
    tags = ", ".join(article.tags or [])
    labels = ["Title:", "Date:", "Source:", "Link:", "Tags:", "Summary:"]
    values = [article.title, pub_date, article.source, article.link, tags, article.summary]

    screen.clear()
    screen.divider()
    widgets.blank()
    widgets.label_block(labels, values)
    widgets.blank()
    screen.divider()


def display_confirm(selected: Pager) -> None:
    screen.clear()
    widgets.section_header("SELECTED ARTICLES")
    widgets.blank()
    widgets.enumerated_list(1, [a.title for a in selected.items])
    widgets.blank()
    screen.divider()
    widgets.blank()