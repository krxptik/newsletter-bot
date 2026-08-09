import logging

from ._display import display_article_details, display_article_list, display_all_articles, display_confirm
from ._input_helpers import input_article_selection

from persistence import add_to_blocklist
from shared.core import Pager
from shared.ui import widgets
from shared.prompts import confirmation

logger = logging.getLogger(__name__)
    

def move_article(from_pager: Pager, to_pager: Pager, prompt: str, letters: bool = False, add: bool = True) -> None:
    if from_pager.is_empty:
        logger.warning("No articles to select from.")
        widgets.blank()
        widgets.notify("WARNING: No articles to select from.")
        return

    display_article_list(from_pager, letters=letters)

    selected_article = input_article_selection(from_pager, prompt=prompt, letters=letters)
    if selected_article is None:
        return

    from_pager.items.remove(selected_article)
    to_pager.items.append(selected_article)
    from_pager.page = min(from_pager.page, to_pager.max_page)
    logger.info(f"Article moved: {selected_article.title}")
    widgets.notify(f"Article was {'added to' if add else 'removed from'} the newsletter.")
    return


def view_article(available: Pager, selected: Pager) -> None:
    display_all_articles(available, selected)
    widgets.blank()
    article = input_article_selection(available, selected)
    if article is None:
        return

    display_article_details(article)
    widgets.blank()
    widgets.m_input("Press 'enter' to go back.")


def mark_as_junk(available: Pager) -> None:
    if available.is_empty:
        logger.warning("No articles to select from.")
        widgets.blank()
        widgets.notify("WARNING: No articles to select from.")
        return
    
    display_article_list(available)
    widgets.blank()
    article = input_article_selection(available)
    if article is None:
        return

    display_article_details(article)
    widgets.blank()
    if not confirmation("Mark this article's page as junk? It will never be shown again."):
        return

    add_to_blocklist(article.link)
    available.items.remove(article)
    available.page = min(available.page, available.max_page)
    logger.info(f"Marked as junk: {article.link}")
    widgets.notify("Article marked as junk and will not appear again.")


def confirm_selected(selected: Pager) -> bool:
    if selected.is_empty:
        widgets.notify("ERROR: No articles selected. Please select before finishing.")
        return False
    
    display_confirm(selected)
    if not confirmation("Generate newsletter with these articles?"):
        return False
    
    return True