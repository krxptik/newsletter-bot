import re
from urllib.parse import urljoin, urlparse

import requests
import feedparser
from bs4 import BeautifulSoup

from ._url_tools import is_valid_url_format

from shared.safe_request import safe_get

COMMON_FEED_PATHS = [
    "/feed",
    "/rss",
    "/feed.xml",
    "/rss.xml",
    "/atom.xml",
    "/feeds/posts/default",
]
FEED_CONTENT_TYPES = {
    "application/atom",
    "application/atom+xml",
    "application/feed+json",
    "application/json",
    "application/rdf",
    "application/rdf+xml",
    "application/rss",
    "application/rss+xml",
    "application/xml",
    "text/atom",
    "text/atom+xml",
    "text/plain",
    "text/rdf",
    "text/rdf+xml",
    "text/rss",
    "text/rss+xml",
    "text/xml",
}
FEED_URL_HINT_RE = re.compile(
    r"\.(?:atom|rdf|rss|xml)$|"
    r"\b(?:atom|rss)\b|"
    r"\?type=100$|"
    r"feeds/posts/default/?$|"
    r"\?feed=(?:atom|rdf|rss|rss2)|"
    r"feed$",
    re.IGNORECASE,
)
TRUNCATION_MARKERS = [
    "continue reading",
    "read more",
    "read the full",
    "[...]",
]


# ===== FEED DISCOVERY =====

def _find_declared_feed_url(response: requests.Response) -> str | None:
    """Scan an already-fetched response for a declared <link rel="alternate"> feed."""
    soup = BeautifulSoup(response.content, "html.parser")
    for link in soup.find_all("link", rel="alternate"):
        t = str(link.get("type") or "").lower()
        href = str(link.get("href") or "")
        resolved = urljoin(response.url, href)
        if not href:
            continue

        if t in FEED_CONTENT_TYPES or "rss" in t or "atom" in t or FEED_URL_HINT_RE.search(href):
            if is_valid_url_format(resolved):  # syntax only — resolvability checked by _check_url_and_feed next
                return resolved
    return None


def _probe_common_feed_paths(url: str) -> list[str]:
    """Build candidate feed URLs from common conventions (e.g. /feed, /rss.xml)."""
    parsed = urlparse(url)
    base = f"{parsed.scheme}://{parsed.netloc}"
    return [base + path for path in COMMON_FEED_PATHS]


def _check_url_and_feed(
    url: str, session: requests.Session
) -> tuple[requests.Response, feedparser.FeedParserDict] | None:
    """Fetch url and parse it as a feed. Returns (response, feed) only if entries were found."""
    response = safe_get(url, session)
    if response is None:
        return None
    feed = feedparser.parse(response.content)
    if not feed.entries:
        return None
    return response, feed


# ===== SCRAPE DETECTION =====

def _is_truncated(content: str) -> bool:
    content_lower = content.lower()
    if any(marker in content_lower for marker in TRUNCATION_MARKERS):
        return True
    return len(content.strip()) < 200


def _is_scraping_required(feed) -> bool:  # no type hint: pylance mis-narrows `content` in _is_truncated if hinted here
    sample = feed.entries[:3]
    truncated = 0

    for entry in sample:
        content = ""

        if hasattr(entry, "content"):
            content = entry.content[0].value if entry.content else ""
        elif hasattr(entry, "summary"):
            content = entry.summary
        elif hasattr(entry, "description"):
            content = entry.description

        if not content or _is_truncated(content):
            truncated += 1

    return truncated >= 2


# ===== RESOLUTION =====

def resolve_feed(response: requests.Response, session: requests.Session) -> tuple[str, bool] | None:
    """Try to resolve an already-fetched response into a usable RSS/Atom feed.

    Checks the response directly, then scans it for a declared
    <link rel="alternate"> feed, then tries common feed paths on the same
    domain. Assumes `response` is already known to be reachable (fetched by
    the caller); returns None if no feed can be found.

    Returns:
        (feed_url, scrape_required) — feed_url is the resolved feed URL;
        scrape_required is True if the feed's entries look truncated and
        full article content will need to be scraped separately.
    """
    # 1. Check if the response itself is already a valid feed
    feed = feedparser.parse(response.content)
    if feed.entries:
        return response.url, _is_scraping_required(feed)

    # 2. Look for a declared feed in <head>
    declared_url = _find_declared_feed_url(response)
    if declared_url:
        result = _check_url_and_feed(declared_url, session)
        if result:
            feed_response, feed = result
            return feed_response.url, _is_scraping_required(feed)

    # 3. Try common paths
    for candidate in _probe_common_feed_paths(response.url):
        result = _check_url_and_feed(candidate, session)
        if result:
            feed_response, feed = result
            return feed_response.url, _is_scraping_required(feed)

    return None