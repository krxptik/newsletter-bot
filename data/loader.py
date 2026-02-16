import json
from typing import List, Dict

# ===== FEEDS.JSON FUNCTIONS =====
def load_feeds(path: str = "data/feeds.json") -> List[Dict]:
    with open(path, 'r', encoding='utf-8') as f:
        data = json.load(f)
        return data
        
def save_feeds(feeds: List[Dict], path: str = "data/feeds.json") -> None:
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(feeds, f, indent=4)

# ===== URLS.JSON FUNCTIONS =====
def load_used_urls(path: str = "data/urls.json") -> set[str]:
    with open(path, 'r', encoding='utf-8') as f:
        data = json.load(f)
        return set(data.get("used_urls", []))
    
def save_used_urls(urls: list[str], path="data/urls.json") -> None:
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(
            {'used_urls': list(urls)},
            f,
            indent=4
        )

# ===== TESTING =====
if __name__ == "__main__":
    print(load_feeds())
    save_feeds(load_feeds())