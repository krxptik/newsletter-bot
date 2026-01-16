from urllib.parse import urljoin, urlparse
from bs4 import BeautifulSoup
from datetime import datetime
from models.article import Article
import requests
import re
import tqdm

reference = {
    "https://www.bbc.co.uk/future/tags/language/": r"https:\/\/www\.bbc\.co.uk\/future\/article\/\d{8}.+",
    "https://www.npr.org/sections/publiceditor/140681900/language-media-and-society": r"https:\/\/www\.npr\.org\/sections\/publiceditor\/\d{4}\/\d{2}\/\d{2}\/\d+\/.+",
    "https://www.merriam-webster.com/wordplay": r"https:\/\/www\.merriam-webster\.com\/wordplay\/.+"
}

date_patterns = [
    [r'\d{1,2}(?:st|nd|rd|th) (?:January|February|March|April|May|June|July|August|September|October|November|December) \d{4}', '%d %B %Y'],
    [r'(?:January|February|March|April|May|June|July|August|September|October|November|December) \d{1,2}, \d{4}', '%B %d, %Y'],
    [r'\d{1,2} (?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec) \d{4}', '%d %b %Y']
]

ALLOW_REGEX_FALLBACK = {
    "https://www.merriam-webster.com/wordplay": False,
    "https://www.bbc.co.uk/future/tags/language/": True,
    "https://www.npr.org/sections/publiceditor/140681900/language-media-and-society": True
}

def clean_ordinal_day(date_str):
    # converts '5th January 2026' -> '5 January 2026'
    return re.sub(r'(\d{1,2})(st|nd|rd|th)', r'\1', date_str)

def extract_pub_date(tag, patterns, allow_fallback=True):
    # First check
    date_div = tag.find('div', class_="published_at")
    if date_div:
        raw_text = date_div.get_text(strip=True)
    else:
        if not allow_fallback:
            return None
        raw_text = tag.get_text()

    for pattern in patterns:
        match = re.search(pattern[0], raw_text)
        if match:
            cleaned = clean_ordinal_day(match.group())
            return datetime.strptime(cleaned, pattern[1])
    return None

def process_non_rss(non_rss_feed_link):
    ref_url = reference.get(non_rss_feed_link)
    if not ref_url:
        print("Warning: feed not in reference, no articles extracted.")
        return []
    
    parsed_url = urlparse(non_rss_feed_link)
    domain = f"{parsed_url.scheme}://{parsed_url.netloc}"
    feed_soup = BeautifulSoup(requests.get(non_rss_feed_link).text, 'html.parser')

    article_link_list = []
    
    # Article link collection
    for a in feed_soup.find_all('a'):
        href = a.get('href')
        if not href:
            continue
        
        full_url = urljoin(domain, href)

        if re.match(ref_url, full_url):
            if full_url not in article_link_list:
                article_link_list.append(full_url)

    # Metadata scraping
    entry_list = []

    for link in article_link_list:
        soup = BeautifulSoup(requests.get(link).text, 'html.parser')

        # Collects title, pub_date, and text
        title = soup.find('title').string
        article_tag = soup.find('article')
        if article_tag:
            pub_date = extract_pub_date(article_tag, date_patterns, ALLOW_REGEX_FALLBACK[non_rss_feed_link])
            paragraphs = article_tag.find_all('p')
        else:
            # All article sites contain article tag, so if otherwise, skip.
            continue
            
        text = "\n".join(p.get_text(strip=True) for p in paragraphs)
        
        article = Article(title, link, pub_date, text)
        entry_list.append(article)

    return entry_list

def process_all_non_rss(non_rss_feeds):
    processed_articles = []
    for feed in tqdm(non_rss_feeds):
        articles = process_non_rss(feed)
        for article in articles:
            if article.is_recent():
                processed_articles.append(article)
    return processed_articles