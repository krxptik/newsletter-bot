from datetime import datetime
from models.article import Article

def generate_context(title, summary, articles: list[Article]):
    return {
        "title": title,
        "date": datetime.now().strftime("%B %d, %Y"),
        "summary": summary,
        "article_rows": [article.to_dict() for article in articles]
    }