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


def _check_feed_url(
    url: str, session: requests.Session
) -> requests.Response | None:
    """Fetch url and parse it as a feed.

    Returns (response, feed) if the URL resolves to a parseable feed.
    If the feed has no entries, it is still accepted unless feedparser
    reports a bozo parse error.
    """
    response = safe_get(url, session)
    if response is None:
        return None

    feed = feedparser.parse(response.content)
    if feed.entries:
        return response

    if getattr(feed, "bozo", True):  # if not well formed, bozo is 1 (truthy). If bozo doesn't exist (missing XML parser), True.
        return None

    return response


def _extract_site_url_from_feed(feed: feedparser.FeedParserDict) -> str | None:
    """Extract the site URL from a parsed feed's metadata when available."""
    feed_metadata = feed.feed
    if isinstance(feed_metadata, dict):  # to make Pylance happy...
        return feed_metadata.get("link")
    return None


# ===== RESOLUTION =====

def resolve_feed_urls(
    response: requests.Response, session: requests.Session
) -> tuple[str | None, str | None]:
    """Resolve a response into the site URL and the best matching feed URL.

    The function checks the response directly, then scans it for a declared
    <link rel="alternate"> feed, and finally tries common feed paths on the
    same domain. It assumes the input response has already been fetched and
    returns a pair of URLs: the site URL and the resolved feed URL.
    """
    # 1. Check if the response itself is already a valid feed
    feed = feedparser.parse(response.content)
    if feed.entries:
        return _extract_site_url_from_feed(feed), response.url

    # 2. Look for a declared feed in <head>-
    declared_url = _find_declared_feed_url(response)
    if declared_url:
        feed_response = _check_feed_url(declared_url, session)
        if feed_response:
            return response.url, feed_response.url

    # 3. Try common paths
    for candidate in _probe_common_feed_paths(response.url):
        feed_response = _check_feed_url(candidate, session)
        if feed_response:
            return response.url, feed_response.url

    return response.url, None