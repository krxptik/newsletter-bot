import logging
from datetime import datetime

from ._handlers import move_article, view_article, confirm_selected
from ._display import display_all_articles, display_options
from ._constants import ARTICLES_PER_PAGE

from models import Article
from shared.prompts import select_with_pagination, PaginationSelectResult, Navigation
from shared.pager import Pager
from shared.logging import setup_logging

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
            case False, Navigation.NEXT: available.next_page()
            case False, Navigation.PREV: available.prev_page()
            case True, Navigation.NEXT: selected.next_page()
            case False, Navigation.PREV: selected.prev_page()
        return False

    match user_input.item_index:
        case 0: move_article(available, selected, prompt="Enter article number")
        case 1: move_article(selected, available, prompt="Enter article letter", letters=True)
        case 2: view_article(available, selected)
        case 3: return confirm_selected(selected)
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
        display_all_articles(available, selected)
        display_options(options)

        user_input = select_with_pagination(options, secondary=True)
        should_exit = _handle_user_input(user_input, available, selected)

        if should_exit:
            break

    logger.info("Selection menu exited")
    return selected.items


def _manual_demo_articles() -> list[Article]:
    now = datetime.now()
    return [
        Article(title="Alpha articleasdfffffffffffsadf", link="https://example.com/a", pub_date=now),
        Article(title="Beta article", link="https://example.com/b", pub_date=now),
        Article(title="Gamma article", link="https://example.com/c", pub_date=now),
        Article(title="Delta article", link="https://example.com/d", pub_date=now),
    ]


if __name__ == "__main__":
    setup_logging()
    selected_articles = run_selection_menu(_manual_demo_articles())

    print()
    print("Selected articles:")
    for article in selected_articles:
        print(f"- {article.title}")