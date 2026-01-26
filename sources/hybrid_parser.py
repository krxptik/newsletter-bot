from models.article import Article
from datetime import datetime
from bs4 import BeautifulSoup
from tqdm import tqdm
from utils.safe_request import safe_get
from utils.add_source import add_source
import requests
import feedparser
import time

def scrape_content(article: Article, session: requests.Session) -> bool:
    """Scrape the content an article from the website.

    Args:
        article (Article): An article object.
        session (requests.Session): Active requests session for connection reuse.
    """
    # --- Ensure working website ---
    response = safe_get(article.link, session)
    if response is None:
        return False

    # --- Find paragraphs ---
    soup = BeautifulSoup(response.text, 'html.parser')
    article_tag = soup.find('article')
    paragraphs = article_tag.find_all('p') if article_tag else soup.find_all('p')
    
    # --- Combine article text ---
    text = "\n".join(p.get_text(strip=True) for p in paragraphs)
    article.text = text
    return True


def parse_entry(entry, session: requests.Session) -> (Article | None):
    """Parse a single Hybrid feed entry into an Article object.

    Args:
        entry (feedparser.FeedParserDict): A single entry from an RSS feed.
        session (requests.Session): Active requests session for connection reuse.

    Returns:
        (Article | None): Returns an Article object if the entry has valid title, 
        link, publication date. Returns None if any required field is missing.
    """
    title = entry.get('title')
    link = entry.get('link')
    pub_date = entry.get('published_parsed')

    if not (title and link and pub_date):
        return None

    pub_date = datetime.fromtimestamp(time.mktime(pub_date))
    article = Article(title, link, pub_date)
    
    if not scrape_content(article, session):
        return None

    return article


def process_hybrid(hybrid_feed_link: str, session: requests.Session) -> list[Article]:
    """Process a single Hybrid feed URL and return a list of Article objects.

    Args:
        hybrid_feed_link (str): The URL of the Hybrid feed to process.
        session (requests.Session): Active requests session for connection reuse.

    Returns:
        list[Article]: A list of Article objects parsed from the feed. 
        Only includes articles that are recent (according to Article.is_recent()).
    """
    try:
        rss_feed = feedparser.parse(hybrid_feed_link)
    except Exception as e:
        return []
    
    articles = [
        article
        for entry in rss_feed.entries
        if (article := parse_entry(entry, session)) is not None
        and article.is_recent()
    ]

    add_source(articles, hybrid_feed_link)
    
    return articles


def process_all_hybrid(hybrid_feeds: list[str], session: requests.Session) -> list[Article]:
    """Process a list of Hybrid feed URLs and return all recent articles.

    Args:
        hybrid_feeds (list[str]): A list of Hybrid feed URLs to process.
        session (requests.Session): Active requests session for connection reuse.

    Returns:
        list[Article]: A combined list of Article objects from all feeds.
    """

    all_articles = []

    for feed in tqdm(hybrid_feeds, desc="Processing hybrid feeds"):
        articles = process_hybrid(feed, session)
        all_articles.extend(articles)

    return all_articles