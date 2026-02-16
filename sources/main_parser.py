from sources.rss_parser import process_rss
from sources.hybrid_parser import process_hybrid
from sources.non_rss_parser import process_non_rss
from tqdm import tqdm
import requests

def parse_all(feeds: list, session: requests.Session):
    articles = []

    for feed in tqdm(feeds):
        if feed['type'] == "RSS":
            articles.extend(process_rss(feed))
        elif feed['type'] == "HYBRID":
            articles.extend(process_hybrid(feed, session))
        elif feed['type'] == "NON-RSS":
            articles.extend(process_non_rss(feed, session))

    return articles