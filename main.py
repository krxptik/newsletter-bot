from dotenv import load_dotenv
from setup.run import run_setup

load_dotenv()
run_setup()
load_dotenv()

from data.loader import load_feeds
from utils.banner import banner
from utils.safe_gen import safe_gen
from sources.main_parser import parse_all
from sources.prune import prune
from ai.throttle import throttle
from ai.prompt import final_sum_prompt
from cli.menu import menu
from post_processing.context import generate_context
from post_processing.manage_articles import add_selected
from post_processing.render import render_newsletter
from post_processing.render import save_newsletter
from post_processing.send_menu import send_menu
from post_processing.send import send_email
import requests
import time

ARTICLE_LIMIT = 19

def main():
    banner()

    # Load feeds
    feeds = load_feeds()

    # Feed processing
    with requests.Session() as session:
        processed_articles = parse_all(feeds)

    # Prune used and excess articles (if any)
    print()
    print("Removing used articles...")
    processed_articles = prune(processed_articles, ARTICLE_LIMIT)
    print(f"Fetched {len(processed_articles)} articles.")
    print()

    # Summarising and tagging articles
    print("Summarising and tagging articles...")
    if not throttle(processed_articles):
        print("Daily quota met, failed to perform AI tasks.")
        return
    print("All articles fully processed and consolidated!")

    # Selection menu
    time.sleep(1)
    print("Preparing the selection menu...")
    time.sleep(2)
    selected_articles = menu(processed_articles)
    print("Article selection complete!")

    # Newsletter metadata
    print("Generating newsletter title and introduction...")
    title, summary = safe_gen(final_sum_prompt, selected_articles)
    print("Complete!")

    # Newsletter rendering and saving
    print("Rendering newsletter...")
    context = generate_context(title, summary, selected_articles)
    html = render_newsletter(context)
    path = save_newsletter(html, title)
    print("Complete!")

    # Email menu
    time.sleep(1)
    print("Preparing the email menu...")
    time.sleep(2)
    em, to_addrs = send_menu(title, path, html)
    print("Email details confirmed!")

    # Send email
    send_email(em, to_addrs)

    # Final post-processing
    add_selected(selected_articles)


if __name__ == "__main__":
    pass