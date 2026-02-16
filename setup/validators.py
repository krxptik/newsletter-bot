from urllib.parse import urlparse

# ===== FEED VALIDATION FUNCTIONS =====

def is_unique(new_feed: dict, feeds: list) -> tuple[bool, str]:
    """Check if feed is unique by URL and name."""
    for feed in feeds:
        if new_feed['url'] == feed['url']:
            return False, f"Feed URL already exists: {feed['name']}"
        if new_feed['name'] == feed['name']:
            return False, f"Feed name already in use: {feed['name']}"
    
    return True, ""

# ===== URL VALIDATION FUNCTIONS =====

def is_valid_url(url: str):
    url = url.strip()
    if not url.startswith(("http://", "https://")):
        url = "https://" + url

    parsed = urlparse(url)
    return parsed.scheme in ("http", "https") and bool(parsed.netloc)