from models.article import Article
from datetime import datetime
from bs4 import BeautifulSoup
from tqdm import tqdm
from utils.add_source import add_source
import feedparser
import time

def parse_entry(entry: feedparser.FeedParserDict) -> (Article | None):
    """Parse a single RSS feed entry into an Article object.

    Args:
        entry (feedparser.FeedParserDict): A single entry from an RSS feed.

    Returns:
        (Article | None): Returns an Article object if the entry has valid title, 
        link, publication date, and content. Returns None if any required field is missing
    """
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

    return Article(title, link, pub_date, content)


def process_rss(rss_feed_link: str) -> list[Article]:
    """Process a single RSS feed URL and return a list of Article objects.

    Args:
        rss_feed_link (str): The URL of the RSS feed to process.

    Returns:
        list[Article]: A list of Article objects parsed from the feed. 
        Only includes articles that are recent (according to Article.is_recent()).
    """
    try:
        rss_feed = feedparser.parse(rss_feed_link)
    except Exception as e:
        print(f"Failed to parse {rss_feed_link}: {e}")
        return []
    
    articles = [
        article
        for entry in rss_feed.entries
        if (article := parse_entry(entry)) is not None
        and article.is_recent()
    ]

    add_source(articles, rss_feed_link)

    return articles


def process_all_rss(rss_feeds: list) -> list[Article]:
    """Process a list of RSS feed URLs and return all recent articles.

    Args:
        rss_feeds (list): A list of RSS feed URLs and source name pairs to process.

    Returns:
        list[Article]: A combined list of Article objects from all feeds.
    """
    all_articles = []

    for feed in tqdm(rss_feeds, desc="Processing RSS feeds"):
        articles = process_rss(feed)
        all_articles.extend(articles)

    return all_articles