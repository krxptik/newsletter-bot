from data.loader import load_used_urls
from datetime import datetime

def prune_articles(processed_articles):
    # Remove used articles
    used_urls = load_used_urls('used_articles.json')
    i = 0
    while i < len(processed_articles):
        if processed_articles[i].link in used_urls:
            processed_articles.pop(i)
        else:
            i += 1

    # Limit to 20 articles
    if len(processed_articles) > 20:
        print("Too many articles retrieved. Pruning excess...")
        processed_articles.sort(
            key=lambda a: a.pub_date or datetime.min, 
            reverse=True
        )
        processed_articles = processed_articles[:20]

    return processed_articles