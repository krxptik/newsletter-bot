from sources.rss_parser import process_rss
from bs4 import BeautifulSoup
import requests
import tqdm

def scrape_content(article):
    r = requests.get(article.link)
    soup = BeautifulSoup(r.text, 'html.parser')

    # Look through soup to find article text
    article_tag = soup.find('article')
    if article_tag:
        paragraphs = article_tag.find_all('p')
    else:
        paragraphs = soup.find_all("p")
    
    # Combine article text
    text = "\n".join(p.get_text(strip=True) for p in paragraphs)
    article.text = text

def process_all_hybrid(hybrid_feeds):
    processed_articles = []
    for feed in tqdm(hybrid_feeds):
        articles = process_rss(feed)
        for article in articles:
            if article.is_recent():
                scrape_content(article)
                processed_articles.append(article)
    return processed_articles