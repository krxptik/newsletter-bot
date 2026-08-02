import logging
import time

import requests

from ._feed_display import render_remove_section, display_feed_data
from ._feed_resolution import resolve_feed_urls
from ._input_helpers import input_url, input_name, input_feed_selection
from app.persistence import save_feeds, save_feed_caches, get_or_create_cache, remove_feed_cache
from models import Feed, FeedCache
from shared.ui import screen, widgets, PAUSE_SHORT
from shared.prompts import confirmation
from shared.pager import Pager

logger = logging.getLogger(__name__)


# ===== REMOVE FEED =====

def remove_feed(pager: Pager, feeds: list[Feed], feed_caches: list[FeedCache]) -> None:
    logger.info("Remove feed flow started")

    if not feeds:
        logger.warning("No feeds available to remove")
        widgets.blank()
        widgets.notify("WARNING: No feeds to remove.")
        return

    render_remove_section(pager)

    feed_to_remove = input_feed_selection(pager)
    if feed_to_remove is None:
        return

    if not confirmation(f"Remove '{feed_to_remove.name}'?"):
        logger.info(f"User cancelled removal of '{feed_to_remove.name}'")
        widgets.notify("Removal cancelled.")
        return

    feeds.remove(feed_to_remove)
    remove_feed_cache(feed_caches, feed_to_remove)
    save_feeds(feeds)
    save_feed_caches(feed_caches)
    logger.info(f"Feed removed: '{feed_to_remove.name}' ({feed_to_remove.site_url}, {feed_to_remove.feed_url})")
    widgets.notify(f"Feed removed: '{feed_to_remove.name}'")


# ===== ADD FEED =====

def _is_duplicate(site_url, feed_url, name, feeds) -> bool:
    duplicate = any(
        (site_url is not None and feed.site_url == site_url) or
        (feed_url is not None and feed.feed_url == feed_url) or
        feed.name == name
        for feed in feeds
    )
    if duplicate:
        widgets.blank()
        widgets.notify("ERROR: A feed with that URL or name already exists.")
    return duplicate


def _build_feed(name: str, feeds: list[Feed], session: requests.Session) -> Feed | None:
    """Collect and resolve everything needed to build a Feed, or None if the user cancels."""
    url_response = input_url("Feed URL:", session)
    if url_response is None:
        return None

    site_url, feed_url = resolve_feed_urls(url_response, session)

    if _is_duplicate(site_url, feed_url, name, feeds):
        return None

    return Feed(
        name=name,
        site_url=site_url,
        feed_url=feed_url
    )


def add_feed(feeds: list[Feed], feed_caches: list[FeedCache]) -> None:
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
        widgets.notify("Add feed cancelled.")
        return

    feeds.append(feed)
    get_or_create_cache(feed_caches, feed)
    save_feeds(feeds)
    save_feed_caches(feed_caches)

    logger.info(f"Feed added: '{feed.name}' ({feed.site_url}, {feed.feed_url})")
    widgets.notify(f"Feed added: '{feed.name}'")


# ===== VIEW FEED =====

def view_feed(pager: Pager, feed_caches: list[FeedCache]) -> None:
    logger.info("View feed flow started")

    feed = input_feed_selection(pager)
    if feed is None:
        return

    feed_cache = get_or_create_cache(feed_caches, feed)
    
    display_feed_data(feed, feed_cache)
    widgets.blank()
    widgets.m_input("Press 'enter' to go back.")