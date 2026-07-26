import logging
import time

from ._display import display_article_details, display_article_list
from ._input_helpers import input_article_selection

from shared.pager import Pager
from shared.ui import widgets, PAUSE_SHORT

logger = logging.getLogger(__name__)
    

def move_article(from_pager: Pager, to_pager: Pager, prompt: str) -> bool:
    logger.info("Move article flow started")

    if from_pager.is_empty:
        logger.warning("No articles to select from.")
        widgets.blank()
        widgets.text("WARNING: No articles to select from.")
        time.sleep(PAUSE_SHORT)
        return False

    display_article_list(from_pager)

    selected_article = input_article_selection(from_pager, prompt=prompt)
    if selected_article is None:
        return False

    from_pager.items.remove(selected_article)
    to_pager.items.append(selected_article)
    from_pager.page = min(from_pager.page, to_pager.max_page)
    logger.info(f"Article moved: {selected_article.title}")
    return True


def view_article(available: Pager, selected: Pager):
    logger.info("View article flow started")

    article = input_article_selection(available, selected)
    if article is None:
        return

    display_article_details(article)
    widgets.blank()
    widgets.m_input("Press 'enter' to go back.")
    