from urllib.parse import urljoin, urlparse
from bs4 import BeautifulSoup
from datetime import datetime
from models.article import Article
from data.loader import load_non_rss
from utils.datefuncs import clean_ordinal_day
from utils.safe_request import safe_get
from utils.add_source import add_source
from tqdm import tqdm
import requests
import re


NON_RSS_CONFIG = load_non_rss()
DATE_PATTERNS = [
    [r'\d{1,2}(?:st|nd|rd|th) (?:January|February|March|April|May|June|July|August|September|October|November|December) \d{4}', '%d %B %Y'],
    [r'(?:January|February|March|April|May|June|July|August|September|October|November|December) \d{1,2}, \d{4}', '%B %d, %Y'],
    [r'\d{1,2} (?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec) \d{4}', '%d %b %Y']
]


def extract_pub_date(tag, patterns, allow_fallback: bool = True):
    """Extract publication date from a BeautifulSoup tag using regex patterns.

    Args:
        tag: BeautifulSoup tag to search for date information.
        patterns: List of [regex_pattern, strptime_format] pairs.
        allow_fallback (bool): If True, search entire tag text when div not found.

    Returns:
        datetime | None: Parsed publication date or None if not found.
    """
    # --- Check for dedicated date div ---
    date_div = tag.find('div', class_="published_at")
    if date_div:
        raw_text = date_div.get_text(strip=True)
    else:
        if not allow_fallback:
            return None
        raw_text = tag.get_text()

    # --- Match against date patterns ---
    for pattern in patterns:
        match = re.search(pattern[0], raw_text)
        if match:
            cleaned = clean_ordinal_day(match.group())
            return datetime.strptime(cleaned, pattern[1])
    return None


def scrape_article(
        url: str, session: requests.Session, 
        date_patterns, allow_fallback: bool) -> (Article | None):
    """Scrape a single article URL and return an Article object.

    Args:
        url (str): The article URL to scrape.
        session (requests.Session): Active requests session for connection reuse.
        date_patterns: List of regex patterns for date extraction.
        allow_fallback (bool): Whether to allow fallback date extraction.

    Returns:
        (Article | None): Article object if scraping succeeds, None otherwise.
    """
    # --- Fetch article page ---
    response = safe_get(url, session)
    if response is None:
        return None
    
    soup = BeautifulSoup(response.text, 'html.parser')
    
    # --- Extract title ---
    title = soup.find('title')
    if title is None:
        return None
    
    # --- Extract article content ---
    article_tag = soup.find('article')
    if not article_tag:
        return None
    
    pub_date = extract_pub_date(article_tag, date_patterns, allow_fallback)
    paragraphs = article_tag.find_all('p')
    text = "\n".join(p.get_text(strip=True) for p in paragraphs)
    
    return Article(title.string, url, pub_date, text)


def process_non_rss(non_rss_feed_link: str, session: requests.Session) -> list[Article]:
    """Process a single non-RSS feed and extract all article links.

    Args:
        non_rss_feed_link (str): URL of the non-RSS feed to process.
        session (requests.Session): Active requests session for connection reuse.

    Returns:
        list[Article]: List of Article objects extracted from the feed.
    """
    # --- Non-RSS feed pre-processing ---
    feed_var = NON_RSS_CONFIG.get(non_rss_feed_link)
    if not feed_var:
        return []
     
    REF_URL = feed_var["article_regex"]
    REGEX_FALLBACK = feed_var["allow_regex_fallback"]

    # --- Fetch feed page ---
    parsed_url = urlparse(non_rss_feed_link)
    domain = f"{parsed_url.scheme}://{parsed_url.netloc}"

    response = safe_get(non_rss_feed_link, session)
    if response is None:
        return []

    feed_soup = BeautifulSoup(response.text, 'html.parser')

    # --- Article link collection ---
    article_link_list = []
    
    for anchor in feed_soup.find_all('a'):
        href = anchor.get('href')
        if not href:
            continue
        
        full_url = urljoin(domain, href)
        if re.match(REF_URL, full_url):
            article_link_list.append(full_url)

    article_link_list = list(set(article_link_list))

    # --- Scrape each article ---
    articles = [
        article
        for link in article_link_list
        if (article := scrape_article(link, session, DATE_PATTERNS, REGEX_FALLBACK)) is not None
        and article.is_recent()
    ]

    add_source(articles, non_rss_feed_link)
    
    return articles


def process_all_non_rss(non_rss_feeds: list[str], session: requests.Session) -> list[Article]:
    """Process a list of non-RSS feed URLs and return all recent articles.

    Args:
        non_rss_feeds (list[str]): A list of non-RSS feed URLs to process.
        session (requests.Session): Active requests session for connection reuse.

    Returns:
        list[Article]: A combined list of Article objects from all feeds.
    """

    with requests.Session() as session:
        all_articles = []

        for feed in tqdm(non_rss_feeds, desc="Processing non-RSS feeds"):
            articles = process_non_rss(feed, session)
            all_articles.extend(articles)

        return all_articles