from dotenv import load_dotenv
load_dotenv()
from data.loader import load_feeds
from utils.banner import banner
from sources.rss_parser import process_all_rss
from sources.hybrid_parser import process_all_hybrid
from sources.non_rss_parser import process_all_non_rss
from sources.prune import prune_articles
from ai.throttle import throttle
from ai.safe_gen import safe_generate
from ai.prompt import final_sum_prompt
from cli.menu import menu
from newsletter_email.context import generate_context
from newsletter_email.render import render_newsletter
from newsletter_email.send import send_email
import requests
import time

def main():
    # Load feeds
    rss_feeds, hybrid_feeds, non_rss_feeds = load_feeds()

    # Startup text
    banner()

    # Feed processing
    with requests.Session() as session:
        processed_articles = []
        processed_articles.extend(process_all_rss(rss_feeds))
        processed_articles.extend(process_all_hybrid(hybrid_feeds, session))  
        processed_articles.extend(process_all_non_rss(non_rss_feeds, session))

    # Prune used and excess articles (if any)
    print()
    print("Removing used articles...")
    processed_articles = prune_articles(processed_articles, 19)
    print(f"Fetched {len(processed_articles)} articles.")
    print()

    # Summarising and tagging articles
    print("Summarising and tagging articles...")
    if not throttle(processed_articles):
        print("Daily quota met, failed to perform AI tasks.")
        return

    print("All articles fully processed and consolidated!")
    time.sleep(0.5)
    print("Preparing the selection menu...")
    time.sleep(3)
    selected_articles = menu(processed_articles)
    title, summary = safe_generate(final_sum_prompt, selected_articles)
    context = generate_context(title, summary, selected_articles)
    html = render_newsletter(context)
    send_email(html)


if __name__ == "__main__":
    main()