from config import DATA_DIR
from typing import List, Dict
import json
import logging
logger = logging.getLogger(__name__)

FEEDS_DIR = DATA_DIR / "feeds.json"
URLS_DIR = DATA_DIR / "urls.json"

# ===== FEEDS.JSON FUNCTIONS =====
def load_feeds(path = FEEDS_DIR) -> List[Dict]:
    logger.debug(f"Loading feeds from {path}")
    try:
        with open(path, 'r', encoding='utf-8') as f:
            data = json.load(f)
            logger.info(f"Loaded {len(data)} feeds")
            return data
    except FileNotFoundError:
        logger.error(f"Feeds file not found: {path}")
        raise
    except json.JSONDecodeError as e:
        logger.error(f"Invalid JSON in feeds file: {e}")
        raise
        
def save_feeds(feeds: List[Dict], path = FEEDS_DIR) -> None:
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(feeds, f, indent=4)

# ===== URLS.JSON FUNCTIONS =====
def load_used_urls(path = URLS_DIR) -> set[str]:
    with open(path, 'r', encoding='utf-8') as f:
        data = json.load(f)
        return set(data)
    
def save_used_urls(urls: set[str], path = URLS_DIR) -> None:
    logger.debug(f"Saving {len(urls)} used URLs")
    
    # Load existing
    try:
        existing = load_used_urls(path)
        logger.debug(f"Loaded {len(existing)} existing URLs")
    except:
        existing = set()
        logger.warning("No existing URLs found, creating new file")
    
    # Merge
    merged = existing | urls
    logger.info(f"Merged URLs: {len(existing)} existing + {len(urls)} new = {len(merged)} total")
    
    with open(path, 'w', encoding='utf-8') as f:
        json.dump({'used_urls': sorted(merged)}, f, indent=4)
    
    logger.debug(f"URLs saved to {path}")