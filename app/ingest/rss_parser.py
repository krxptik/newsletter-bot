import logging
import time

import feedparser
import requests
from bs4 import BeautifulSoup
from datetime import datetime

from models.article import Article
from app.ingest.safe_request import safe_get

logger = logging.getLogger(__name__)


# --- Content extraction ---

def _extract_rss_content(entry) -> str | None:
    """Extract and clean article text directly from RSS feed data."""
    content_list = entry.get('content', [{}])
    content_html = content_list[0].get('value') or entry.get('description')
    if not content_html:
        return None
    return BeautifulSoup(content_html, 'html.parser').get_text(strip=True)

def _scrape_url_content(link: str, session: requests.Session) -> str | None:
    """Scrape article body text from a URL."""
    response = safe_get(link, session)
    if response is None:
        logger.debug(f"_scrape_url_content: request failed for {link}")
        return None

    soup = BeautifulSoup(response.text, "html.parser")
    article_tag = soup.find("article")
    paragraphs = article_tag.find_all("p") if article_tag else soup.find_all("p")
    text = "\n".join(p.get_text(strip=True) for p in paragraphs)

    if not text:
        logger.debug(f"_scrape_url_content: no text found at {link}")
        return None

    logger.debug(f"_scrape_url_content: extracted {len(text)} chars from {link}")
    return text


# --- Entry parsing ---

def _extract_entry_fields(entry) -> tuple | None:
    """Pull and validate raw fields from a feed entry. Returns (title, link, pub_date) or None."""
    title = entry.get('title')
    link = entry.get('link')
    pub_date = entry.get('published_parsed')

    missing = [name for name, val in [('title', title), ('link', link), ('date', pub_date)] if not val]
    if missing:
        logger.debug(f"_extract_entry_fields: skipping entry missing {', '.join(missing)}")
        return None

    pub_date = datetime.fromtimestamp(time.mktime(pub_date))
    return title, link, pub_date


def _get_article_content(
    entry,
    link: str,
    feed_obj: dict,
    session: requests.Session | None,
) -> str | None:
    """Get article content via scraping or RSS data, depending on feed config."""
    if feed_obj.get("scrape_content"):
        return _scrape_url_content(link, session)
    return _extract_rss_content(entry)


def parse_entry(
    entry,
    feed_obj: dict,
    session: requests.Session | None = None,
) -> Article | None:
    """Parse a feed entry into an Article, or return None if parsing fails.

    Content is scraped from the article URL if feed_obj has scrape_content=True,
    otherwise it is extracted from the RSS data. A session is required when
    scrape_content=True.
    """
    fields = _extract_entry_fields(entry)
    if fields is None:
        return None
    title, link, pub_date = fields

    content = _get_article_content(entry, link, feed_obj, session)
    if not content:
        logger.debug(f"parse_entry: no content for '{title}' — skipping")
        return None

    return Article(title, link, pub_date, content, source=feed_obj["name"])


# --- Feed processing ---

def parse_rss(feed_obj: dict, session: requests.Session | None = None) -> list[Article]:
    """Process an RSS feed and return recent Article objects.

    Args:
        feed_obj: Feed config dict. Set scrape_content=True to scrape article
                  body text from each article's URL instead of using RSS data.
        session:  A requests.Session. Required when scrape_content=True.
    """
    name = feed_obj.get("name")
    url = feed_obj.get("url", "")
    logger.info(f"parse_rss: fetching '{name}' ({url})")
    
    try:
        rss_feed = feedparser.parse(url)
    except Exception as e:
        logger.error(f"parse_rss: failed to fetch '{name}' ({url}): {e}")
        return []
    
    logger.debug(f"parse_rss: {len(rss_feed.entries)} entries in '{name}'")

    articles = []
    for entry in rss_feed.entries:
        article = parse_entry(entry, feed_obj, session)
        if article is None:
            continue
        if not article.is_recent():
            logger.debug(f"parse_rss: skipping old article '{article.title[:50]}'")
            continue
        articles.append(article)
    
    logger.info(f"parse_rss: {len(articles)} recent articles from '{name}'")
    return articles