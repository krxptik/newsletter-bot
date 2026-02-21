from data.loader import load_used_urls
from datetime import datetime
from models.article import Article

def prune(processed_articles: list[Article], max_no: int) -> list[Article]:
    """Prunes used articles and limit number of articles to max_no."""
    used_urls = load_used_urls()

    # --- Remove used articles ---
    filtered = [article for article in processed_articles if article.link not in used_urls]

    # --- Limit to 20 or 19 articles ---
    if len(filtered) > max_no:
        filtered.sort(key=lambda a: a.pub_date or datetime.min, reverse=True)
        return filtered[:max_no]
    
    return filtered