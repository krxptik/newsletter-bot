import logging
from utils.logging_config import setup_logging

# Set up logging BEFORE any other imports
setup_logging()
logger = logging.getLogger(__name__)

from dotenv import load_dotenv
from setup.run import run_setup
from data.loader import load_feeds
from utils.banner import banner
from utils.safe_gen import safe_gen
from sources.main_parser import parse_all
from sources.prune import prune
from ai.throttle import throttle
from ai.prompt import create_ai_client
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
UI_WIDTH = 60

def main():
    logger.info("=" * UI_WIDTH)
    logger.info("NEWSLETTER BOT STARTED".center(UI_WIDTH))
    logger.info("=" * UI_WIDTH)

    try:
        # Setup
        load_dotenv()
        run_setup()
        load_dotenv()

        ai_client = create_ai_client()

        banner()

        # Load feeds
        logger.info("Loading feeds from configuration...")
        feeds = load_feeds()
        logger.info(f"Loaded {len(feeds)} feeds")

        # Feed processing
        logger.info("Fetching articles from feeds...")
        with requests.Session() as session:
            processed_articles = parse_all(feeds, session)
        logger.info(f"Fetched {len(processed_articles)} articles")

        # Prune
        logger.info("Removing used and excess articles...")
        final_articles = prune(processed_articles, ARTICLE_LIMIT)
        logger.info(f"After pruning: {len(processed_articles)} articles")

        # AI processing
        logger.info("Starting AI summarization and tagging...")
        if not throttle(final_articles):
            logger.error("Daily quota met, AI processing failed")
            print("Daily quota met, failed to perform AI tasks.")
            return
        logger.info("AI processing complete")

        # Selection
        logger.info("Opening article selection menu...")
        selected_articles = menu(processed_articles)
        logger.info(f"User selected {len(selected_articles)} articles")

        # Newsletter generation
        logger.info("Generating newsletter metadata...")
        title, summary = safe_gen(ai_client.final_sum_prompt, selected_articles)
        logger.info(f"Newsletter title: {title}")

        logger.info("Rendering newsletter HTML...")
        context = generate_context(title, summary, selected_articles)
        html = render_newsletter(context)
        path = save_newsletter(html, title)
        logger.info(f"Newsletter saved to: {path}")

        # Email
        logger.info("Configuring email settings...")
        em, to_addrs = send_menu(title, path, html)
        logger.info(f"Email will be sent to {len(to_addrs)} recipients")

        logger.info("Sending email...")
        send_email(em, to_addrs)

        # Cleanup
        logger.info("Saving used article URLs...")
        add_selected(selected_articles)

        logger.info("=" * UI_WIDTH)
        logger.info("PROGRAM COMPLETED SUCCESSFULLY".center(UI_WIDTH))
        logger.info("=" * UI_WIDTH)

    except KeyboardInterrupt:
        logger.warning("User interrupted execution")
        print("\n\nExecution interrupted by user")
    except Exception as e:
        logger.exception("Fatal error in main execution")
        print(f"\n\nFATAL ERROR: {e}")
        print("Check logs for details")
        raise


if __name__ == "__main__":
    main()