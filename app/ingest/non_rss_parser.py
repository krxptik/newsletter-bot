import logging
import re
from datetime import datetime
from urllib.parse import urljoin, urlparse

import requests
from bs4 import BeautifulSoup

from models import *
from shared.datefuncs import clean_ordinal_day
from shared.safe_request import safe_get

logger = logging.getLogger(__name__)


DATE_PATTERNS = [
    (r"\d{1,2}(?:st|nd|rd|th) (?:January|February|March|April|May|June|July|August|September|October|November|December) \d{4}", "%d %B %Y"),
    (r"(?:January|February|March|April|May|June|July|August|September|October|November|December) \d{1,2}, \d{4}", "%B %d, %Y"),
    (r"\d{1,2} (?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec) \d{4}", "%d %b %Y"),
]



# --- Date extraction ---

def _find_date_text(tag, pub_date_visible: bool) -> str | None:
    """Get the raw text to search for a date within a tag."""
    date_div = tag.find("div", class_="published_at")
    if date_div:
        return date_div.get_text(strip=True)
    if pub_date_visible:
        return tag.get_text()
    logger.debug("No date div found and fallback is disabled")
    return None


def _parse_date_from_text(raw_text: str) -> datetime | None:
    """Try each DATE_PATTERN against raw_text and return the first match."""
    for pattern, fmt in DATE_PATTERNS:
        match = re.search(pattern, raw_text)
        if not match:
            continue
        cleaned = clean_ordinal_day(match.group())
        try:
            return datetime.strptime(cleaned, fmt)
        except ValueError as e:
            logger.debug(f"strptime failed for '{cleaned}': {e}")
    return None


def extract_pub_date(tag, pub_date_visible: bool = True) -> datetime | None:
    """Extract publication date from a BeautifulSoup tag using regex patterns."""
    raw_text = _find_date_text(tag, pub_date_visible)
    if raw_text is None:
        return None
    date = _parse_date_from_text(raw_text)
    if date is None:
        logger.debug("No date pattern matched")
    return date


# --- Article scraping ---

def _extract_article_body(article_tag) -> str:
    """Extract plain text from all <p> tags within an article element."""
    paragraphs = article_tag.find_all("p")
    return "\n".join(p.get_text(strip=True) for p in paragraphs)


def scrape_article(
    url: str,
    session: requests.Session,
    pub_date_visible: bool,
    source_name: str,
) -> Article | None:
    """Scrape a single article URL and return an Article, or None if scraping fails."""
    logger.debug(f"Fetching {url}")

    response = safe_get(url, session)
    if response is None:
        logger.debug(f"Request failed for {url}")
        return None

    soup = BeautifulSoup(response.text, "html.parser")

    title_tag = soup.find("title")
    if title_tag is None:
        logger.debug(f"No <title> tag at {url}")
        return None

    title_text = title_tag.get_text(strip=True)
    if not title_text:
        logger.debug(f"Empty title at {url}")
        return None

    article_tag = soup.find("article")
    if not article_tag:
        logger.debug(f"No <article> tag at {url}")
        return None

    pub_date = extract_pub_date(article_tag, pub_date_visible)
    if pub_date is None:
        logger.debug(f"No publication date found at {url}")

    text = _extract_article_body(article_tag)
    return Article(title_text, url, pub_date, text, source_name)


# --- Feed processing ---

def _collect_article_links(feed_soup, article_regex: str, domain: str) -> list[str]:
    """Find and deduplicate article links on a feed page matching article_regex."""
    links = set()
    for anchor in feed_soup.find_all("a"):
        href = anchor.get("href")
        if not href:
            continue
        full_url = urljoin(domain, href)
        if re.match(article_regex, full_url):
            links.add(full_url)
    return list(links)


def parse_non_rss(feed_obj: Feed, session: requests.Session) -> list[Article]:
    """Scrape a non-RSS feed page and return recent Article objects."""
    name = feed_obj.name
    url = feed_obj.url

    if not name:
        logger.warning("Missing feed name; returning []")
        return []

    if not url:
        logger.warning("Missing feed url for '%s'; returning []", name)
        return []

    logger.info(f"Fetching '{name}' ({url})")

    parsed_url = urlparse(url)
    domain = f"{parsed_url.scheme}://{parsed_url.netloc}"

    response = safe_get(url, session)
    if response is None:
        logger.warning(f"Could not fetch feed page {url}")
        return []

    feed_soup = BeautifulSoup(response.text, "html.parser")
    article_links = _collect_article_links(feed_soup, feed_obj.article_regex or "", domain)
    logger.debug(f"{len(article_links)} unique links found on '{name}'")

    pub_date_visible = feed_obj.pub_date_visible
    articles = []
    for link in article_links:
        article = scrape_article(link, session, pub_date_visible, name)
        if article is None:
            continue
        if not article.is_recent():
            logger.debug(f"Skipping old article '{article.title[:50]}'")
            continue
        articles.append(article)

    logger.info(f"{len(articles)} recent articles from '{name}'")
    return articles

if __name__ == "__main__":
    import requests
    import trafilatura
    
    def scrape_article_traf(url, session, source_name):
        response = safe_get(url, session)
        if response is None:
            return None

        result = trafilatura.bare_extraction(
            response.text,
            include_comments=False,
            with_metadata=True,
            favor_precision=True,
        )

        if result is None or not result.text:
            return None

        title = result.title
        body = result.text
        pub_date = result.date  # usually a string like "2026-07-15" or None

        return Article(title or url, url, pub_date, body, source_name)
    
    with requests.Session() as session:
        art = scrape_article_traf("https://www.bbc.co.uk/future/tags/language/", session, source_name="meow")
        print(art)
        print(art.title)
        print(art.link)
        print(art.pub_date)
        print(art.text)
        print(art.source)
        print(art.summary)
        print(art.tags)