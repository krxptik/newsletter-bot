from dotenv import load_dotenv
load_dotenv()
from data.loader import load_feeds
from sources.rss_parser import process_all_rss
from sources.hybrid_parser import process_all_hybrid
from sources.non_rss_parser import process_all_non_rss
from utils.prune import prune_articles
from ai.throttle import throttled_proc
from cli.menu import menu
import pyfiglet
import time

rss_feeds, hybrid_feeds, non_rss_feeds = load_feeds()

# Startup text
print("=========================")
text = "ellie!"
banner = pyfiglet.figlet_format(text)
print(banner[:-1])
print("=========================")
print("\nRunning v0.1.0.\n")

# RSS processing
print("Processing RSS feeds...")
processed_articles = process_all_rss(rss_feeds)
print()

# Hybrid proccessing
print("Processing hybrid feeds...")
processed_articles += process_all_hybrid(hybrid_feeds)      
print()

# Non-RSS processing
print("Processing non-RSS feeds...")
processed_articles += process_all_non_rss(non_rss_feeds)

# Prune used and excess articles (if any)
print("Removing used articles...")
processed_articles = prune_articles(processed_articles, 19)
print(f"Fetched {len(processed_articles)} articles.")
print()

# Summarising and tagging articles
print("Summarising and tagging articles...")
throttled_proc(processed_articles)

print("All articles fully processed and consolidated!")
time.sleep(0.5)
print("Preparing the selection menu...")
time.sleep(3)
selected_articles = menu(processed_articles)
