from models.article import Article
from datetime import datetime
from bs4 import BeautifulSoup
import feedparser
import time
import logging
logger = logging.getLogger(__name__)

def parse_entry(entry: feedparser.FeedParserDict, rss_obj: dict) -> (Article | None):
    """Parse a single RSS feed entry into an Article object."""
    title = entry.get('title')
    link = entry.get('link')
    pub_date = entry.get('published_parsed')

    if not (title and link and pub_date):
        return None
    
    pub_date = datetime.fromtimestamp(time.mktime(pub_date))
    
    content_html = entry.get('content', [{}])[0].get('value') or entry.get('description')
    if not content_html:
        return None
    
    soup = BeautifulSoup(content_html, 'html.parser')
    content = soup.get_text(strip=True)

    return Article(title, link, pub_date, content, rss_obj['name'])


def process_rss(rss_obj: dict) -> list[Article]:
    """Process a single RSS feed URL and return a list of Article objects."""
    logger.debug(f"Fetching RSS feed: {rss_obj['url']}")
    
    try:
        rss_feed = feedparser.parse(rss_obj['url'])
        logger.debug(f"Feed parsed, {len(rss_feed.entries)} entries found")
    except Exception as e:
        logger.error(f"Failed to parse {rss_obj['url']}: {e}")
        return []
    
    articles = []
    for entry in rss_feed.entries:
        article = parse_entry(entry, rss_obj)
        if article and article.is_recent():
            articles.append(article)
        elif article:
            logger.debug(f"Skipping old article: {entry.get('title', 'Unknown')[:50]}")
    
    logger.info(f"RSS feed '{rss_obj['name']}': {len(articles)} recent articles")
    return articles