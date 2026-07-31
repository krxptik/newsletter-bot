from models import Article
from shared.ui import widgets, screen
from shared.pager import Pager


def _visible_list_height(items: list[str]) -> int:
    return len(items) if items else 1


def _pad_panel_height(current_height: int, target_height: int) -> None:
    if target_height > current_height:
        widgets.blank(target_height - current_height)


def _page_footer(pager: Pager) -> None:
    if pager.max_page > 1:
        widgets.text(f"[Page {pager.page}/{pager.max_page}]")
    else:
        widgets.blank()
    widgets.blank()


def display_all_articles(available: Pager, selected: Pager) -> None:
    a_items, a_start = available.get_page_items()
    s_items, s_start = selected.get_page_items()
    a_list = [a.title for a in a_items]
    s_list = [s.title for s in s_items]
    target_height = max(_visible_list_height(a_list), _visible_list_height(s_list))

    screen.clear()
    with widgets.capture_panel() as left:
        widgets.section_header("AVAILABLE ARTICLES")
        widgets.blank()
        widgets.enumerated_list(a_start+1, a_list, empty_message="No available articles.", overflow="truncate", letters=False)
        _pad_panel_height(_visible_list_height(a_list), target_height)
        widgets.blank()
        _page_footer(available)
        screen.divider()

    with widgets.capture_panel() as right:
        widgets.section_header("SELECTED")
        widgets.blank()
        widgets.enumerated_list(s_start+1, s_list, empty_message="No selected articles.", overflow="truncate")
        _pad_panel_height(_visible_list_height(s_list), target_height)
        widgets.blank()
        _page_footer(selected)
        screen.divider()

    widgets.two_panels(left, right)


def display_options(options: list[str]) -> None:
    footer = "\n".join([
        "[<] / [>] to navigate available articles",
        "[<<] / [>>] to navigate selected articles"
    ])
    widgets.blank()
    widgets.options_menu(options, footer=footer)
    widgets.blank()


def display_article_list(pager: Pager, letters: bool = False, empty_message: str = "Nothing to show."):
    items, start = pager.get_page_items()
    item_list = [a.title for a in items]
    screen.clear()
    screen.divider()
    widgets.blank()
    widgets.enumerated_list(start+1, item_list, letters=letters, empty_message=empty_message)
    widgets.blank()
    screen.divider()
    widgets.blank()
    

def display_article_details(article: Article) -> None:
    pub_date = article.pub_date.strftime('%d/%m/%Y') if article.pub_date else 'Not set'
    tags = ', '.join(article.tags or [])
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