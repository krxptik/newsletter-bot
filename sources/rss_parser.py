from models.article import Article
from datetime import datetime
from bs4 import BeautifulSoup
import tqdm
import feedparser
import time

def process_rss(rss_feed_link):
    rss_feed = feedparser.parse(rss_feed_link)
    entry_list = []
    
    for entry in rss_feed.entries:

        # Grabs article metadata and puts it into an Article object
        title = entry.get('title')
        link = entry.get('link')
        pub_date = entry.get('published_parsed')
        content_html = entry.get('content')

        # Checks if RSS feed article has the following fields. Otherwise, it discards
        if not title or not link or not pub_date:
            continue

        # Content processing
        if content_html:
            soup = BeautifulSoup(content_html[0]['value'], 'html.parser')
            content = soup.get_text(strip=True)
        else:
            content_html = entry.get('description')
            soup = BeautifulSoup(content_html, 'html.parser')
            content = soup.get_text(strip=True)

        # Date processing
        pub_date = datetime.fromtimestamp(time.mktime(pub_date))

        article = Article(title, link, pub_date, content)
        entry_list.append(article)

    return entry_list

def process_all_rss(rss_feeds):
    processed_articles = []
    for feed in tqdm(rss_feeds):
        articles = process_rss(feed)
        for article in articles:
            if article.is_recent():
                processed_articles.append(article)
    return processed_articles