from dataclasses import fields, asdict

from models import Feed
from shared.pager import Pager
from shared.ui import widgets, screen

FEED_FIELD_LABELS = {
    "name": "Name:",
    "url": "URL:",
    "metadata_retrieval": "Metadata retrieval:",
    "content_retrieval": "Content retrieval:",
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
        footer="[N] Next page / [P] Previous page" if pager.max_page > 1 else None,
    )


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


def display_feed_data(feed: Feed) -> None:
    screen.clear()
    data = asdict(feed)
    labels = [FEED_FIELD_LABELS[f.name] for f in fields(feed)]
    values = [data[f.name] for f in fields(feed)]
    screen.divider()
    widgets.blank()
    widgets.label_block(labels, values)
    widgets.blank()
    screen.divider()