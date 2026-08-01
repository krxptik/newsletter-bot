import requests
from concurrent.futures import ThreadPoolExecutor, as_completed

import trafilatura
from bs4 import BeautifulSoup

from ._extraction_utils import normalise_trafilatura_result, enrich_extraction_with_ai
from ._ai_fallback import ai_extract
from ._concurrency import domain_semaphore
from ._session_pool import get_session
from ._constants import SCRAPE_WORKERS
from ._fallback_stats import record_attempt

from models import Feed, Article
from shared.safe_request import safe_get
from shared.ai_client import AIClient


def discover_and_scrape(feed_obj: Feed, session: requests.Session, client: AIClient) -> list[Article]:
    """Heuristic mode AND the RSS-broken-recovery path (same subtree,
    called from two trigger points — do not duplicate this logic)."""
    response = safe_get(feed_obj.site_url, session) if feed_obj.site_url else None
    if response is None:
        return []

    soup = BeautifulSoup(response.text, "html.parser")
    candidates = _junk_filtered_links(soup, feed_obj.site_url)

    articles: list[Article] = []
    with ThreadPoolExecutor(max_workers=SCRAPE_WORKERS) as executor:
        futures = {
            executor.submit(_article_from_link, link, feed_obj, client): link
            for link in candidates
        }
        for future in as_completed(futures):
            article = future.result()
            if article and article.is_recent():
                articles.append(article)

    return articles  # [] if nothing found — treated as benign, not a failure


def _article_from_link(link: str, feed_obj: Feed, client: AIClient) -> Article | None:
    record_attempt(link)
    with domain_semaphore(link):
        resp = safe_get(link, get_session())

    if resp is None:
        return None

    result = trafilatura.bare_extraction(
        resp.text,
        include_comments=False,
        favor_precision=True,
        with_metadata=True,
    )
    extracted_text, extracted_title, extracted_date = normalise_trafilatura_result(result)
    extracted_text, extracted_title, extracted_date = enrich_extraction_with_ai(
        resp.text,
        extracted_title,
        extracted_date,
        extracted_text,
        client,
        ai_extract,
        url=link
    )

    if not (extracted_text and extracted_title and extracted_date):
        return None

    return Article(extracted_title, link, extracted_date, extracted_text, feed_obj.name)


def _junk_filtered_links(soup: BeautifulSoup, base_url: str | None) -> list[str]:
    """Return candidate article links while skipping obvious junk and anchors."""
    if not base_url:
        return []

    links: list[str] = []
    seen: set[str] = set()
    for anchor in soup.find_all("a", href=True):
        href_value = anchor.get("href", "")
        href = str(href_value)
        if not href or href.startswith(("#", "mailto:", "tel:")):
            continue

        if href.startswith("/"):
            href = f"{base_url.rstrip('/')}{href}"
        elif not href.startswith(("http://", "https://")):
            continue

        if any(token in href for token in ("/tag/", "/category/", "/author/", "/topic/")):
            continue

        if href.lower().endswith((".pdf", ".zip", ".png", ".jpg", ".jpeg", ".gif", ".svg", ".mp3", ".mp4")):
            continue

        if href not in seen:
            seen.add(href)
            links.append(href)

    return links