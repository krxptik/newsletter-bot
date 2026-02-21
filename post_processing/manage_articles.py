from models.article import Article
from data.loader import load_used_urls, save_used_urls

def add_selected(articles: list[Article]):
    article_links = {article.link for article in articles}
    save_used_urls(article_links)