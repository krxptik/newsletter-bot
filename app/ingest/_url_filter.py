import re
from typing import TYPE_CHECKING
from urllib.parse import urljoin, urlparse

from shared.core import normalise_path

if TYPE_CHECKING:
    from bs4 import BeautifulSoup

# Path segments that are never article content, regardless of site.
# Matched per-segment (not raw substring) so trailing-slash/no-trailing-slash
# and prefix variants ("about-npr") both match correctly.
JUNK_PATH_KEYWORDS = (
    "tag", "tags", "category", "categories", "author", "authors", "topic", "topics",
    "help", "support", "faq", "contact", "about", "subscribe", "newsletter", "newsletters",
    "search", "sitemap", "account", "notifications", "settings", "login", "signin", "signup",
    "columns", "video"
)

JUNK_DOMAINS = (
    "facebook.com", "twitter.com", "x.com", "instagram.com",
    "linkedin.com", "youtube.com", "tiktok.com", "pinterest.com",
    "reddit.com", "whatsapp.com", "t.me", "threads.net",
)

JUNK_FILE_TYPES = (
    ".pdf", ".zip", ".png", ".jpg", ".jpeg", ".gif", ".svg", ".mp3", ".mp4",
)

JUNK_SUB_DOMAINS = ("help", "account", "search", "support")

# An article-shaped slug has either a long hyphenated title or a numeric
# ID/date somewhere in the path. Nav/tool/account pages ("/games",
# "/settings", "/saved-words") almost never have either, regardless of
# what a given site happens to call them — this generalizes across
# domains where a keyword blocklist can't.
MIN_SLUG_HYPHENS = 2
NUMERIC_ID_RE = re.compile(r"\d{4,}")


def junk_filtered_links(soup: "BeautifulSoup", base_url: str | None, blocklist: dict[str, list[str]]) -> list[str]:
    if not base_url:
        return []

    base_domain = urlparse(base_url).netloc.removeprefix("www.")
    links: list[str] = []
    seen: set[str] = set()

    for anchor in soup.find_all("a", href=True):
        href = str(anchor.get("href", ""))
        if not href or href.startswith(("#", "mailto:", "tel:")):
            continue

        resolved = urljoin(base_url, href)
        parsed = urlparse(resolved)
        domain = parsed.netloc.removeprefix("www.")

        if not _is_same_site(domain, base_domain):
            continue
        if _matches_junk_subdomain(domain, base_domain):
            continue
        if any(junk in domain for junk in JUNK_DOMAINS):
            continue
        if _matches_domain_blocklist(domain, parsed.path, blocklist):
            continue
        if _has_junk_path_segment(parsed.path):
            continue
        if parsed.path.lower().endswith(JUNK_FILE_TYPES):
            continue
        if not _looks_like_article(parsed.path):
            continue

        if resolved not in seen:
            seen.add(resolved)
            links.append(resolved)

    return links


def _is_same_site(domain: str, base_domain: str) -> bool:
    return domain == base_domain or domain.endswith(f".{base_domain}")


def _matches_junk_subdomain(domain: str, base_domain: str) -> bool:
    if domain == base_domain:
        return False
    subdomain_label = domain.removesuffix(f".{base_domain}").split(".")[0]
    return subdomain_label in JUNK_SUB_DOMAINS


def _has_junk_path_segment(path: str) -> bool:
    """Check each path segment against the blocklist individually — catches
    both terminal pages ('/contact', no trailing slash) and prefixed
    variants ('about-npr'), unlike a raw substring-with-slashes check."""
    segments = [s for s in path.lower().split("/") if s]
    return any(
        keyword == segment or keyword in segment.split("-")
        for segment in segments
        for keyword in JUNK_PATH_KEYWORDS
    )


def _looks_like_article(path: str) -> bool:
    """Positive signal: real articles almost always have a long hyphenated
    slug and/or a numeric ID/date in the path. Nav, tool, and account pages
    ('/games', '/settings', '/saved-words') generally have neither — this
    catches site-specific junk pages without needing to name them."""
    last_segment = path.rstrip("/").rsplit("/", 1)[-1]
    if last_segment.count("-") >= MIN_SLUG_HYPHENS:
        return True
    return bool(NUMERIC_ID_RE.search(path))


def _matches_domain_blocklist(domain: str, path: str, blocklist: dict[str, list[str]]) -> bool:
    return normalise_path(path) in blocklist.get(domain, [])