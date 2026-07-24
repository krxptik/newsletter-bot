import logging

from ._display_constants import FEEDS_PER_PAGE
from ._feed_display import render_feed_section
from ._feed_operations import add_feed, remove_feed, view_feed

from app.persistence import load_feeds_with_caches
from models import Feed, FeedCache
from shared.ui import widgets
from shared.prompts import select_with_pagination, confirmation, Navigation
from shared.pager import Pager

logger = logging.getLogger(__name__)


def _handle_user_input(
        user_input: int | Navigation | None, 
        pager: Pager, 
        feeds: list[Feed],
        feed_caches: list[FeedCache]
    ) -> bool:
    match user_input:
        case Navigation.NEXT:
            pager.next_page()
        case Navigation.PREV:
            pager.prev_page()
        case 0:
            add_feed(feeds, feed_caches)
        case 1:
            remove_feed(pager, feeds, feed_caches)
        case 2:
            view_feed(feeds, feed_caches)
        case 3:
            if confirmation("Confirm feeds?"):
                logger.info("Feeds confirmed")
                return True
    return False


def run_feed_manager() -> None:
    logger.info("Running feed manager")
    feeds, feed_caches = load_feeds_with_caches()
    pager = Pager(feeds, FEEDS_PER_PAGE)

    while True:
        options = [
            "Add new feed",
            "Remove existing feed",
            "View feed details",
            "Done",
        ]
        render_feed_section(pager, options)
        widgets.blank()
        
        user_input = select_with_pagination(options)
        should_exit = _handle_user_input(user_input, pager, feeds, feed_caches)

        if should_exit:
            break

    logger.info("Feed manager exited")