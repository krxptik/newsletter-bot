import time
import logging

from ._handlers import move_article, view_article
from ._display import display_confirm, display_selection_menu
from ._constants import ARTICLES_PER_PAGE

from models import Article
from shared.ui import widgets, PAUSE_SHORT
from shared.prompts import confirmation, select_with_pagination, PaginationSelectResult, Navigation
from shared.pager import Pager

logger = logging.getLogger(__name__)


def _handle_user_input(
        user_input: PaginationSelectResult | None,
        available: Pager,
        selected: Pager
    ) -> bool:
    if user_input is None:
        return False

    if user_input.navigation is not None:
        match user_input.secondary, user_input.navigation:
            case False, Navigation.NEXT:
                available.next_page()
            case False, Navigation.PREV:
                available.prev_page()
            case True, Navigation.NEXT:
                selected.next_page()
            case False, Navigation.PREV:
                selected.prev_page()
        return False

    match user_input.item_index:
        case 0:
            success = move_article(available, selected, prompt="Enter article number")
            if success:
                widgets.text("Article was added to the newsletter.")
                time.sleep(PAUSE_SHORT)
        case 1:
            success = move_article(selected, available, prompt="Enter article letter")
            if success:
                widgets.text("Article was added to the newsletter.")
                time.sleep(PAUSE_SHORT)
        case 2:
            view_article(available, selected)
        case 3:
            display_confirm(selected)
            if confirmation("Generate newsletter with these articles?"):
                logger.info("Selected articles confirmed")
                return True
    return False


# ===== MENU ENTRY POINT =====

def run_selection_menu(articles: list[Article]) -> list[Article]:
    logger.info("Running selection menu")
    available = Pager(articles, ARTICLES_PER_PAGE)
    selected = Pager([], ARTICLES_PER_PAGE)
    options = [
        "Add article to selected", 
        "Remove selected article", 
        "View article details",
        "Done",
    ]

    while True:
        display_selection_menu(available, selected, options)

        user_input = select_with_pagination(options, secondary=True)
        should_exit = _handle_user_input(user_input, available, selected)

        if should_exit:
            break

    logger.info("Selection menu exited")
    return selected.items