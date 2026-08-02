import logging

from ._display_constants import FEEDS_PER_PAGE
from ._feed_display import render_feed_section
from ._feed_operations import add_feed, remove_feed, view_feed

from app.persistence import load_feeds_with_caches
from models import Feed, FeedCache
from shared.prompts import select_with_pagination, confirmation, PaginationSelectResult, Navigation
from shared.pager import Pager

logger = logging.getLogger(__name__)


def run_feed_manager() -> None:
    logger.info("Running feed manager")
    feeds, feed_caches = load_feeds_with_caches()
    pager = Pager(feeds, FEEDS_PER_PAGE)
    options = [
        "Add new feed",
        "Remove existing feed",
        "View feed details",
        "Done",
    ]
    
    while True:
        render_feed_section(pager, options)
        
        user_input = select_with_pagination(options)
        should_exit = _handle_user_input(user_input, pager, feeds, feed_caches)

        if should_exit:
            break

    logger.info("Feed manager exited")

    
def _handle_user_input(
        user_input: PaginationSelectResult | None,
        pager: Pager, 
        feeds: list[Feed],
        feed_caches: list[FeedCache]
    ) -> bool:
    if user_input is None:
        return False

    if user_input.navigation is not None:
        match user_input.navigation:
            case Navigation.NEXT: pager.next_page()
            case Navigation.PREV: pager.prev_page()
        return False

    match user_input.item_index:
        case 0: add_feed(feeds, feed_caches)
        case 1: remove_feed(pager, feeds, feed_caches)
        case 2: view_feed(pager, feed_caches)
        case 3: return confirmation("Confirm feeds?")
    return False