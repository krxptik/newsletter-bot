import json

def load_feeds(path: str = "data/feeds.json") -> tuple[dict]:
    with open(path, 'r', encoding='utf-8') as f:
        data = json.load(f)
        
        rss = data.get('rss_feeds', [])
        hybrid = data.get('hybrid_feeds', [])
        non_rss = data.get('non_rss_feeds', [])

        return rss, hybrid, non_rss
    
def load_sources(path: str = "data/feeds.json") -> dict:
    with open(path, 'r', encoding='utf-8') as f:
        data = json.load(f)
        source_names = data.get('source_names', {})
        return source_names
    
def load_used_urls(path: str = "data/urls.json") -> set[str]:
    with open(path, 'r', encoding='utf-8') as f:
        data = json.load(f)
        return set(data.get("used_urls", []))
    
def save_used_urls(urls: list[str], path="data/urls.json") -> None:
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(
            {'used_urls': list(urls)},
            f,
            indent=2
        )

def load_non_rss(path="data/non_rss.json") -> dict:
    with open(path, 'r', encoding="utf-8") as f:
        data = json.load(f)
        return data