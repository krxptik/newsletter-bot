import logging

from models.article import Article
from app.persistence.data_manager import load_file_data, overwrite_file_data
from config import RUNTIME_DIR

logger = logging.getLogger(__name__)

URLS_FILE = RUNTIME_DIR / "used_urls.json"


def load_used_urls(path=URLS_FILE) -> set[str]:
    logger.debug(f"Loading used URLs from {path}")
    urls = set(load_file_data(path, default=[]))
    logger.info(f"Loaded {len(urls)} used URLs")
    return urls


def save_used_urls(articles: list[Article], path=URLS_FILE) -> None:
    used_urls = load_used_urls()
    new_urls = {article.link for article in articles}
    merged = used_urls | new_urls
    logger.info(f"Saving {len(merged)} used URLs ({len(new_urls)} new)")
    overwrite_file_data(sorted(merged), path)
    logger.debug(f"Used URLs saved to {path}")