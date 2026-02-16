from urllib.parse import urljoin, urlparse
from bs4 import BeautifulSoup
from datetime import datetime
from models.article import Article
from utils.datefuncs import clean_ordinal_day
from utils.safe_request import safe_get
import requests
import re


DATE_PATTERNS = [
    [r'\d{1,2}(?:st|nd|rd|th) (?:January|February|March|April|May|June|July|August|September|October|November|December) \d{4}', '%d %B %Y'],
    [r'(?:January|February|March|April|May|June|July|August|September|October|November|December) \d{1,2}, \d{4}', '%B %d, %Y'],
    [r'\d{1,2} (?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec) \d{4}', '%d %b %Y']
]


def extract_pub_date(tag, patterns, allow_fallback: bool = True):
    """Extract publication date from a BeautifulSoup tag using regex patterns."""
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
        date_patterns, allow_fallback: bool,
        nrss_obj: dict) -> (Article | None):
    """Scrape a single article URL and return an Article object."""
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
    
    return Article(title.string, url, pub_date, text, nrss_obj['name'])


def process_non_rss(nrss_obj: dict, session: requests.Session) -> list[Article]:
    """Process a single non-RSS feed and extract all article links."""
    # --- Fetch feed page ---
    parsed_url = urlparse(nrss_obj['url'])
    domain = f"{parsed_url.scheme}://{parsed_url.netloc}"

    response = safe_get(nrss_obj['url'], session)
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
        if re.match(nrss_obj['article_regex'], full_url):
            article_link_list.append(full_url)

    article_link_list = list(set(article_link_list))

    # --- Scrape each article ---
    articles = [
        article
        for link in article_link_list
        if (article := scrape_article(link, session, DATE_PATTERNS, nrss_obj['allow_regex_fallback'], nrss_obj)) is not None
        and article.is_recent()
    ]
    
    return articles