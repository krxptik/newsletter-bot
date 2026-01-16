import json

def load_feeds(path="data/feeds.json"):
    with open(path, 'r', encoding='utf-8') as f:
        data = json.load(f)
        
        rss = data.get('rss_feeds', [])
        hybrid = data.get('hybrid_feeds', [])
        non_rss = data.get('non_rss_feeds', [])

        return rss, hybrid, non_rss
    
def load_used_urls(path="data/urls.json"):
    with open(path, 'r', encoding='utf-8') as f:
        data = json.load(f)
        return set(data.get("used_urls", []))
    
def save_used_urls(urls, path="data/urls.json"):
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(
            {'used_urls': list(urls)},
            f,
            indent=2
        )