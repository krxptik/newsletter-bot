# Standard library
import logging

# Third-party
import requests
from dotenv import load_dotenv

# Local — shared utilities
from shared.logging import setup_logging
from shared.terminal import display_banner_figlet, run_with_spinner, WIDTH

# Local — version
from version import __version__

# Local — app
from app.bootstrap.config_state_handler import start_initialisation
from app.bootstrap.settings_menu import UserExitError
from app.compose.context_builder import generate_context
from app.deliver.send import send_email
from app.deliver.send_menu import send_menu
from shared.ai_client import GemmaClient # current model
from app.enrich.article_enricher import process_articles
from app.enrich.newsletter_composer import generate_newsletter_metadata
from app.ingest.main_parser import parse_all
from app.filter.article_limit import retrieve_article_limit, InsufficientQuotaError
from app.filter.filter_articles import filter_articles
from app.persistence.feed_store import load_feeds
from app.persistence.used_url_store import save_used_urls
from app.render.render import render_newsletter, save_newsletter, preview_newsletter
from app.selection.menu import menu


setup_logging()


def main():
    logger = logging.getLogger(__name__)

    try:
        # --- Bootstrap ---
        start_initialisation()
        load_dotenv()
        logger.info("NEWSLETTER BOT STARTED")

        # --- AI client ---
        logger.debug("Initialising AI client")
        ai_client = GemmaClient.from_env()

        display_banner_figlet("ellie!")
        print(f"\nRunning {__version__}.\n")

        # --- Ingest ---
        feeds = load_feeds()
        logger.info(f"Loaded {len(feeds)} feeds")
        with requests.Session() as session:
            articles = parse_all(feeds, session)
        logger.info(f"Fetched {len(articles)} articles")

        # --- Filter and Prune ---
        limit = retrieve_article_limit(ai_client)
        articles = filter_articles(articles, limit)
        logger.info(f"After pruning: {len(articles)} articles remain")

        # --- AI processing ---
        logger.info("Starting AI summarisation and tagging...")
        enriched_articles = process_articles(ai_client, articles)
        logger.info(f"AI processing complete: {len(enriched_articles)} articles enriched")

        # --- Article selection ---
        logger.info("Opening article selection menu...")
        selected_articles = menu(enriched_articles)
        logger.info(f"User selected {len(selected_articles)} articles")

        # --- Newsletter generation ---
        display_banner_figlet("ellie!")
        print("\nRunning v0.1.1.\n")
        logger.info("Generating newsletter title and summary...")
        title, summary = run_with_spinner(
            "Generating newsletter...",
            generate_newsletter_metadata,
            ai_client,
            selected_articles
        )
        logger.info(f"Newsletter title: '{title}'")

        logger.info("Rendering newsletter HTML...")
        context = generate_context(title, summary, selected_articles)
        html = render_newsletter(context)
        path = save_newsletter(html, title)
        logger.info(f"Newsletter saved to: {path}")

        logger.info("Opening newsletter preview in browser...")
        preview_newsletter(path)

        # --- Email sending ---
        logger.info("Opening email send menu...")
        em, to_addrs = send_menu(title, path, html)
        logger.info(f"Sending email to {len(to_addrs)} recipient(s)...")
        send_email(em, to_addrs)

        # --- Cleanup ---
        logger.info("Saving used article URLs...")
        save_used_urls(selected_articles)

        logger.info("=" * WIDTH)
        logger.info("PROGRAM COMPLETED SUCCESSFULLY".center(WIDTH))
        logger.info("=" * WIDTH)

    except UserExitError:
        logger.info("User exited from main menu")
        print("Program ended.")

    except InsufficientQuotaError as e:
        logger.warning(str(e))
        print(f"\n{e}")
        
    except KeyboardInterrupt:
        logger.warning("Execution interrupted by user (KeyboardInterrupt)")
        print("\nExecution interrupted by user\n")

    except Exception as e:
        logger.exception("Fatal error in main execution")
        print(f"\n\nFATAL ERROR: {e}")
        print("Check logs for details.")
        raise

if __name__ == "__main__":
    main()