import logging
import time

import requests

from ._feed_display import render_remove_section, display_feed_data
from ._feed_resolution import resolve_feed
from ._input_helpers import input_url, input_name, input_feed_selection

from app.persistence import save_feeds
from models import Feed
from shared.ui import screen, widgets, PAUSE_SHORT
from shared.prompts import confirmation
from shared.pager import Pager

logger = logging.getLogger(__name__)


# ===== REMOVE FEED =====

def remove_feed(pager: Pager, feeds: list[Feed]) -> None:
    logger.info("Remove feed flow started")

    if not feeds:
        logger.warning("No feeds available to remove")
        widgets.blank()
        widgets.text("WARNING: No feeds to remove.")
        time.sleep(PAUSE_SHORT)
        return

    render_remove_section(pager)

    feed_to_remove = input_feed_selection(feeds)
    if feed_to_remove is None:
        return

    if not confirmation(f"Remove '{feed_to_remove.name}'?"):
        logger.info(f"User cancelled removal of '{feed_to_remove.name}'")
        widgets.text("Removal cancelled.")
        time.sleep(PAUSE_SHORT)
        return

    feeds.remove(feed_to_remove)
    save_feeds(feeds)
    logger.info(f"Feed removed: '{feed_to_remove.name}' ({feed_to_remove.url})")
    widgets.text(f"Feed removed: '{feed_to_remove.name}'")
    time.sleep(PAUSE_SHORT)


# ===== ADD FEED =====

def _is_duplicate(url: str, feeds: list[Feed], name: str | None = None) -> bool:
    duplicate = any(feed.url == url or (name and feed.name == name) for feed in feeds)
    if duplicate:
        widgets.blank()
        widgets.text("ERROR: A feed with that URL or name already exists.")
        time.sleep(PAUSE_SHORT)
    return duplicate


def _build_feed(name: str, feeds: list[Feed], session: requests.Session) -> Feed | None:
    """Collect and resolve everything needed to build a Feed, or None if the user cancels."""
    url_response = input_url("Feed URL:", session)
    if url_response is None:
        return None

    feed_url = url_response.url

    if _is_duplicate(feed_url, feeds, name):
        return None

    resolution = resolve_feed(url_response, session)
    if resolution:
        feed_url, scrape_needed = resolution
        metadata_retrieval = "collect"
        content_retrieval = "scrape" if scrape_needed else "collect"
    else:
        metadata_retrieval = "scrape"
        content_retrieval = "scrape"

    if _is_duplicate(feed_url, feeds):
        return None

    return Feed(
        url=feed_url,
        name=name,
        metadata_retrieval=metadata_retrieval,
        content_retrieval=content_retrieval,
    )


def add_feed(feeds: list[Feed]) -> None:
    logger.info("Add feed flow started")

    widgets.banner("ADD FEED", clear=True)
    widgets.blank()

    new_name = input_name()
    if new_name is None:
        return

    screen.divider()
    widgets.blank()

    with requests.Session() as session:
        feed = _build_feed(new_name, feeds, session)

    if feed is None:
        return

    display_feed_data(feed)
    widgets.blank()

    if not confirmation("Add this feed?"):
        logger.info(f"User declined to add feed: {feed.name}")
        widgets.text("Add feed cancelled.")
        time.sleep(PAUSE_SHORT)
        return

    feeds.append(feed)
    save_feeds(feeds)

    logger.info(f"Feed added: '{feed.name}' — {feed.url}")
    widgets.text(f"Feed added: '{feed.name}'")
    time.sleep(PAUSE_SHORT)


# ===== VIEW FEED =====

def view_feed(feeds: list[Feed]) -> None:
    logger.info("View feed flow started")

    feed = input_feed_selection(feeds)
    if feed is None:
        return
    
    display_feed_data(feed)
    widgets.blank()
    widgets.m_input("Press 'enter' to go back.")