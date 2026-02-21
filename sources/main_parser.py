from sources.rss_parser import process_rss
from sources.hybrid_parser import process_hybrid
from sources.non_rss_parser import process_non_rss
from tqdm import tqdm
import requests
import logging
logger = logging.getLogger(__name__)

def parse_all(feeds: list, session: requests.Session):
    logger.info(f"Starting to parse {len(feeds)} feeds")
    articles = []
    
    for feed in tqdm(feeds):
        logger.debug(f"Parsing feed: {feed['name']} ({feed['type']})")
        try:
            if feed['type'] == "RSS":
                result = process_rss(feed)
            elif feed['type'] == "HYBRID":
                result = process_hybrid(feed, session)
            elif feed['type'] == "NON-RSS":
                result = process_non_rss(feed, session)
            else:
                logger.warning(f"Unknown feed type: {feed['type']}")
                continue
            
            articles.extend(result)
            logger.info(f"Feed '{feed['name']}': {len(result)} articles")
        except Exception as e:
            logger.error(f"Failed to parse feed '{feed['name']}': {e}", exc_info=True)
    
    logger.info(f"Total articles parsed: {len(articles)}")
    return articles