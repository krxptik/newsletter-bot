"""
app/ingest/main_parser.py
--------------------------
Orchestrates parsing across all configured feeds. This file is the single
place where the feed-parsing contract is documented — every parser
function below must honor it.

HOW A FEED IS PARSED
    There is no stored "mode" or "type" field anywhere on Feed or
    FeedCache. Whether a feed is parsed via its RSS feed or via direct
    site scraping is a condition evaluated fresh on every single parse,
    never cached as an attribute of its own:

        uses feedparser (feed_url)     if feed.feed_url and cache.trust_feed_url
        uses direct scrape (site_url)  otherwise

    Do not reintroduce a stored mode/type field for this — it would
    duplicate feed_url/trust_feed_url as a second source of truth that
    could drift out of sync with them. If some future piece of code needs
    to know "which branch is this feed on," compute the condition above;
    don't cache the answer.

    The feedparser branch reads structured entries directly. The
    site-scrape branch fetches feed.site_url, filters candidate <a> links,
    and extracts each one with Trafilatura — falling back to an AI
    extraction call only when Trafilatura's result is missing or too
    short.

    A broken RSS feed (feedparser's bozo flag set, no usable entries) does
    not raise or crash the run — it sets cache.trust_feed_url to False and
    falls through to scraping feed.site_url instead, so a feed self-heals
    into scraping without user intervention. feed_url is never deleted
    when this happens, so the feed could in principle recover back to the
    feedparser branch later if the upstream RSS is fixed — nothing
    currently does this automatically, flipping trust_feed_url back to
    True would need to be a deliberate decision (manual, or a future
    periodic recheck).

    Per-entry content is NEVER decided by a stored flag either. Every
    article, every run, independently checks whether the entry's own text
    is usable (see feed_utils._is_truncated) and falls back to scraping
    that single article's link with Trafilatura if not. A feed that is
    normally full-text but occasionally truncates one article is handled
    correctly by this per-entry check — a feed-level "this feed is always
    truncated" cache flag was deliberately rejected, since the check
    itself is nearly free (no network call) and a cached answer could go
    stale the moment the site's feed behavior changes.

RETURN VALUE CONTRACT
    Every top-level per-feed parser function returns exactly one of:

        list[Article]   Success. Normal case, may be a short list.

        []               Ran fine, nothing to report. Covers: a feed with
                         zero new entries, and site-scrape link discovery
                         finding zero candidate links. Both are treated as
                         benign — NOT logged or surfaced as a failure —
                         since either can be entirely legitimate (a feed
                         that hasn't posted lately, or a page layout that
                         doesn't currently match the link-junk filter).

        None             This feed could not be parsed at all this run and
                         needs attention. Currently the only trigger: RSS
                         is broken (bozo) AND there is no site_url to fall
                         back on, so there is nothing left to try. Callers
                         must NOT treat this the same as [] — it must call
                         cache.mark_parsed(success=False), whereas both
                         success cases above call
                         cache.mark_parsed(success=True).

    This distinction exists so a feed that is silently, permanently broken
    (dead site, credentials issue, etc.) can eventually be surfaced to the
    user via FeedCache.consecutive_failures in the settings health view,
    without every merely-quiet feed being flagged as if something were
    wrong.

AI USAGE
    There is exactly one AI extraction entry point,
    ai_extract(html, need_title, need_date, need_text), used identically
    whether topping up one missing field on an otherwise-good entry or
    building an Article from nothing during site-scrape mode. It is only
    ever called as a last resort after Trafilatura has already failed, to
    protect the daily AI request quota (see shared/ai_client.py's
    GEMINI_LIMITS/GEMMA_LIMITS).
"""

import logging
from concurrent.futures import ThreadPoolExecutor, as_completed

import feedparser

from ._constants import FEEDPARSER_FAIL_COUNT, FEED_WORKERS
from ._rss_entry_parser import entry_to_article
from ._site_scraper import discover_and_scrape
from ._session_pool import get_session
from ._fallback_stats import log_summary, reset
from app.persistence import load_domain_blocklist
from models import Feed, FeedCache, Article
from shared.ai import AIClient
from shared.ui import widgets

logger = logging.getLogger(__name__)


def parse_all(feeds: list[tuple[Feed, FeedCache]], client: AIClient) -> list[Article]:
    """Parse all feeds concurrently and return a flat list of recent Article objects."""
    logger.info(f"parse_all: parsing {len(feeds)} feeds")

    reset()
    blocklist = load_domain_blocklist()
    articles: list[Article] = []
    with ThreadPoolExecutor(max_workers=FEED_WORKERS) as executor:
        futures = {
            executor.submit(_parse_feed_safe, feed_obj, cache, client, blocklist): (feed_obj, cache)
            for feed_obj, cache in feeds
        }

        with widgets.app_tqdm(total=len(feeds), desc="Feed parsing", unit="feed") as pbar:
            for future in as_completed(futures):
                _, cache = futures[future]
                result = future.result()
                if result:
                    articles.extend(result)
                cache.mark_parsed(success=(result is not None))
                pbar.update(1)

    logger.info(f"{len(articles)} total articles across {len(feeds)} feeds")
    log_summary()
    return articles


def _parse_feed_safe(
        feed_obj: Feed, cache: FeedCache, 
        client: AIClient, blocklist: dict[str, list[str]]
    ) -> list[Article] | None:
    """Isolate one feed's failure from the rest of the pool."""
    try:
        return _parse_feed(feed_obj, cache, get_session(), client, blocklist)
    except Exception:
        logger.exception(f"parse_all: unhandled error on '{feed_obj.name}'")
        return None


def _parse_feed(
        feed_obj: Feed, cache: FeedCache, 
        session, client: AIClient, blocklist: dict[str, list[str]]
    ) -> list[Article] | None:
    """Top-level entry point. Derives mode, dispatches, updates cache."""
    if not (feed_obj.feed_url and cache.trust_feed_url):
        return discover_and_scrape(feed_obj, session, client, blocklist)

    feed = feedparser.parse(feed_obj.feed_url)
    if feed.entries:
        return _parse_feedparser_entries(feed.entries, feed_obj, session, client, blocklist)

    if not feed.bozo:
        return []

    if feed_obj.site_url is None:
        logger.error(f"{feed_obj.name}: feed broken, no site_url to recover with")
        cache.trust_feed_url = False
        return None

    cache.trust_feed_url = False
    return discover_and_scrape(feed_obj, session, client, blocklist)


def _parse_feedparser_entries(
        entries, feed_obj: Feed,
        session, client: AIClient, blocklist: dict[str, list[str]]
    ) -> list[Article] | None:
    fail_count = 0
    articles = []
    for entry in entries:
        if fail_count > FEEDPARSER_FAIL_COUNT:
            return discover_and_scrape(feed_obj, session, client, blocklist)
        article = entry_to_article(entry, feed_obj, session, client)
        if article is None:
            fail_count += 1
            continue
        articles.append(article)
    return articles