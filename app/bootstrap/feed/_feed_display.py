from dataclasses import asdict, fields
from datetime import datetime

from models import Feed, FeedCache
from shared.pager import Pager
from shared.ui import widgets, screen

FEED_FIELD_LABELS = {
    "name": "Name:",
    "site_url": "Site URL:",
    "feed_url": "Feed URL:",
}
FEED_CACHE_FIELD_LABELS = {
    "trust_feed_url": "Fetch method:",
    "last_parsed_at": "Last parsed at:",
    "consecutive_failures": "Consecutive failures:",
}
FEED_CACHE_VALUE_TRANSFORMS = {
    "trust_feed_url": lambda x: "Using RSS feed" if x else "RSS unavailable — scraping site directly",
    "last_parsed_at": lambda x: datetime.fromisoformat(x).strftime("%d/%m/%Y") if x else "Never parsed",
    "consecutive_failures": lambda x: None if x == 0 else f"⚠ Failed {x} run{'s in a row' if x != 1 else ''}",
}


# ===== FEED SECTIONS =====

def render_feed_section(pager: Pager, options: list[str]) -> None:
    widgets.banner("LIST OF FEEDS", clear=True)
    widgets.blank()
    _render_feed_list(pager)
    widgets.blank()
    screen.divider()
    widgets.blank()
    widgets.options_menu(
        options,
        footer="[<] / [>] to navigate feeds" if pager.max_page > 1 else None,
    )
    widgets.blank()


def render_remove_section(pager: Pager) -> None:
    widgets.banner("SELECT FEED TO REMOVE", clear=True)
    widgets.blank()
    _render_feed_list(pager)
    widgets.blank()
    screen.divider()
    widgets.blank()


# ===== FEED DISPLAY =====

def _render_feed_list(pager: Pager) -> None:
    feeds, start = pager.get_page_items()
    feed_names = [feed.name for feed in feeds]
    
    widgets.enumerated_list(start + 1, feed_names, empty_message="No feeds configured.")
    widgets.blank()
    if pager.max_page > 1:
        widgets.text(f"Page {pager.page}/{pager.max_page}")


# ===== FEED DATA DISPLAY =====

def _render_feed_section(feed: Feed) -> None:
    data = asdict(feed)
    labels = [FEED_FIELD_LABELS[field.name] for field in fields(feed)]
    values = [data[field.name] if data[field.name] else "not set" for field in fields(feed)]
    widgets.label_block(labels, values)


def _render_feed_cache_section(feed_cache: FeedCache) -> None:
    data = asdict(feed_cache)
    labels_and_values = []

    for field in fields(feed_cache):
        raw_value = data[field.name]
        string_value = FEED_CACHE_VALUE_TRANSFORMS[field.name](raw_value)

        if string_value is None:
            continue

        labels_and_values.append((FEED_CACHE_FIELD_LABELS[field.name], string_value))

    if not labels_and_values:
        widgets.text("Nothing to show.")
        return

    labels, values = zip(*labels_and_values)
    widgets.label_block(list(labels), list(values))


def display_feed_data(feed: Feed, feed_cache: FeedCache | None = None) -> None:
    screen.clear()
    screen.divider()
    widgets.blank()
    _render_feed_section(feed)
    widgets.blank()
    screen.divider()

    if feed_cache is None:
        return

    widgets.blank()
    _render_feed_cache_section(feed_cache)
    widgets.blank()
    screen.divider()
    
