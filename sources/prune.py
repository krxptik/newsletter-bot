from data.loader import load_used_urls
from datetime import datetime
from models.article import Article

def prune(processed_articles: list[Article], max_no: int) -> list[Article]:
    """Prunes used articles and limit number of articles to max_no.
    The limiting of articles is based on publish date or lack thereof.

    Args:
        processed_articles (list[Article]): A list of processed article objects
        max_no (int): The maximum number of articles allowed

    Returns:
        list[Article]: A list of articles that haven't been used. Total count is max_no.
    """
    # --- Remove used articles ---
    used_urls = load_used_urls()
    i = 0
    while i < len(processed_articles):
        if processed_articles[i].link in used_urls:
            processed_articles.pop(i)
        else:
            i += 1

    # --- Limit to 20 or 19 articles ---
    if len(processed_articles) > max_no:
        print("Too many articles retrieved. Pruning excess...")
        processed_articles.sort(
            key=lambda a: a.pub_date or datetime.min, 
            reverse=True
        )
        processed_articles = processed_articles[:max_no]

    return processed_articles