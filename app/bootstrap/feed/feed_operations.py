import logging
import time

import feedparser

from app.bootstrap.feed.cli_render import render_feed_section, render_remove_section, display_feed_data
from app.bootstrap.feed.input_flows import input_url, add_name, collect_non_rss_enrichment
from app.bootstrap.feed.feed_utils import is_scraping_required, validate_unique_feed
from app.persistence.feed_store import save_feeds
from shared.terminal import confirmation, display_banner, clear_terminal, divider

logger = logging.getLogger(__name__)

PAUSE_SHORT = 1


# ===== OPERATIONS =====

# --- remove_feed helper ---

def _input_feed_selection(typed_feeds: list) -> dict | None:
    print("Enter feed number:")
    print("(Type 'back' to cancel)")
    while True:
        raw = input("> ").strip()

        if raw.lower() == "back":
            return None

        if not raw.isdigit():
            print("\nERROR: Please enter a number.")
            time.sleep(PAUSE_SHORT)
            continue

        idx = int(raw) - 1
        if idx < 0 or idx >= len(typed_feeds):
            logger.warning("Invalid feed selection.")
            print("\nERROR: Invalid selection.")
            time.sleep(PAUSE_SHORT)
            continue

        return typed_feeds[idx]


def remove_feed(f_type: str, feeds: list) -> None:
    logger.info(f"Remove feed flow started for type: {f_type}")
    typed_feeds = [feed for feed in feeds if feed["type"] == f_type]

    if not typed_feeds:
        logger.warning(f"No {f_type} feeds available to remove")
        print("\nWARNING: No feeds to remove.")
        time.sleep(PAUSE_SHORT)
        return

    render_remove_section(f_type, typed_feeds)

    feed_to_remove = _input_feed_selection(typed_feeds)
    if feed_to_remove is None:
        return

    if not confirmation(f"Remove '{feed_to_remove['name']}'?"):
        logger.info(f"User cancelled removal of '{feed_to_remove['name']}'")
        print("\nRemoval cancelled.")
        time.sleep(PAUSE_SHORT)
        return

    feeds.remove(feed_to_remove)
    save_feeds(feeds)
    logger.info(f"Feed removed: '{feed_to_remove['name']}' ({feed_to_remove.get('url')})")


# --- add_feed helpers ---

def _input_feed_url(f_type: str, new_feed: dict) -> str | None:
    while True:
        new_url = input_url("Feed URL:")
        if new_url is None:
            return None

        if f_type == "RSS":
            feed = feedparser.parse(new_url)
            if not feed.entries:
                logger.warning(f"URL is not a valid RSS/Atom feed: {new_url}")
                print("\nERROR: URL is not a valid RSS/Atom feed. Please try another URL.")
                time.sleep(PAUSE_SHORT)
                continue

            if is_scraping_required(feed):
                new_feed["scrape_content"] = True
                logger.info(f"Scraping required for: {new_url}")
                print("\nNote: This feed provides partial content — article content will be fetched automatically.")
                time.sleep(PAUSE_SHORT)

        new_feed["url"] = new_url
        logger.debug(f"Feed URL accepted: {new_url}")
        return new_url


def _input_feed_name(new_feed: dict, feeds: list) -> str | None:
    while True:
        new_name = add_name()
        if new_name is None:
            return None

        new_feed["name"] = new_name
        error = validate_unique_feed(new_feed, feeds)
        if error:
            logger.warning(f"Feed validation failed: {error}")
            print(f"\nERROR: {error}")
            time.sleep(PAUSE_SHORT)
            continue

        logger.debug(f"Feed name accepted: {new_name}")
        return new_name


def add_feed(f_type: str, feeds: list) -> None:
    logger.info(f"Add feed flow started for type: {f_type}")
    clear_terminal()
    display_banner("ADD FEED")
    new_feed: dict = {"type": f_type}

    if _input_feed_url(f_type, new_feed) is None:
        return

    divider(single=True, spacing=True)

    if _input_feed_name(new_feed, feeds) is None:
        return

    divider(single=True, spacing=True)

    if f_type == "NON-RSS":
        non_rss_data = collect_non_rss_enrichment()
        if non_rss_data is None:
            logger.debug("User cancelled during non-RSS enrichment")
            return
        new_feed.update(non_rss_data)
        logger.debug("Non-RSS enrichment data collected")

    clear_terminal()
    divider()
    display_feed_data(new_feed)
    divider()

    if not confirmation("Add this feed?"):
        logger.info(f"User declined to add feed: {new_feed['name']}")
        print("\nWARNING: Feed not added.")
        time.sleep(PAUSE_SHORT)
        return

    feeds.append(new_feed)
    save_feeds(feeds)
    logger.info(f"Feed added: '{new_feed['name']}' ({f_type}) — {new_feed['url']}")


# ===== ORCHESTRATION =====

def handle_feed_type(f_type: str, feeds: list) -> None:
    logger.info(f"Entering feed management for: {f_type}")

    while True:
        typed_feeds = [feed for feed in feeds if feed["type"] == f_type]
        render_feed_section(f_type, typed_feeds)
        user_input = input("\n> ").strip()

        if not user_input.isdigit():
            continue

        option = int(user_input)

        if option == 1:
            add_feed(f_type, feeds)
        elif option == 2:
            remove_feed(f_type, feeds)
        elif option == 3:
            if confirmation(f"Confirm {f_type} feeds?"):
                logger.info(f"{f_type} feeds confirmed")
                break

    logger.info(f"Feed management loop exited for: {f_type}")