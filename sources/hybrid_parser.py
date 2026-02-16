from models.article import Article
from datetime import datetime
from bs4 import BeautifulSoup
from utils.safe_request import safe_get
import requests
import feedparser
import time

def scrape_content(article: Article, session: requests.Session) -> bool:
    """Scrape the content an article from the website."""
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


def parse_entry(entry, session: requests.Session, hybrid_obj: dict) -> (Article | None):
    """Parse a single Hybrid feed entry into an Article object."""
    title = entry.get('title')
    link = entry.get('link')
    pub_date = entry.get('published_parsed')

    if not (title and link and pub_date):
        return None

    pub_date = datetime.fromtimestamp(time.mktime(pub_date))
    article = Article(title, link, pub_date)
    
    if not scrape_content(article, session):
        return None
    
    article.source = hybrid_obj['name']

    return article


def process_hybrid(hybrid_obj: dict, session: requests.Session) -> list[Article]:
    """Process a single Hybrid feed URL and return a list of Article objects."""
    try:
        rss_feed = feedparser.parse(hybrid_obj['url'])
    except Exception as e:
        return []
    
    articles = [
        article
        for entry in rss_feed.entries
        if (article := parse_entry(entry, session, hybrid_obj)) is not None
        and article.is_recent()
    ]
    
    return articles