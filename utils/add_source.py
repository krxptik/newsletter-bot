from models.article import Article
from data.loader import load_sources

def add_source(articles: list[Article], feed_link) -> None:
    source_names = load_sources()
    for article in articles:
        article.source = source_names.get(feed_link, "")
    return
