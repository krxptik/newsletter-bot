# Standard library
import logging

# Third-party
import requests
from dotenv import load_dotenv

# Local — shared utilities
from shared.logging import setup_logging
from shared.ui import widgets
from shared.exceptions import UserExitError, InsufficientQuotaError
from shared.ai_client import GemmaClient # current model

# Local — version
from version import __version__

# Local — app
from app.persistence import load_feeds_with_caches, match_feeds_to_caches, save_used_urls
from app.bootstrap import start_initialisation
from app.ingest.orchestrator import parse_all
from app.filter.article_limit import retrieve_article_limit
from app.filter.filter_articles import filter_articles
from app.enrich.article_enricher import process_articles
from app.enrich.newsletter_composer import generate_newsletter_metadata
from app.selection.menu import menu
from app.compose.context_builder import generate_context
from app.render.render import render_newsletter, save_newsletter, preview_newsletter
from app.deliver.send_menu import send_menu
from app.deliver.send import send_email


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

        widgets.banner_figlet("ellie!")

        # --- Ingest ---
        feeds, caches = load_feeds_with_caches()
        matched = match_feeds_to_caches(feeds, caches)
        logger.info(f"Loaded {len(feeds)} feeds")
        with requests.Session() as session:
            articles = parse_all(matched, session, ai_client)
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
        widgets.banner_figlet("ellie!")
        logger.info("Generating newsletter title and summary...")
        title, summary = widgets.run_with_spinner(
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

        logger.info("=" * 64)
        logger.info("PROGRAM COMPLETED SUCCESSFULLY".center(64))
        logger.info("=" * 64)

    except UserExitError:
        logger.info("User exited from programme.")
        widgets.blank()
        widgets.text("Program ended.")

    except InsufficientQuotaError as e:
        logger.warning(str(e))
        widgets.blank()
        widgets.text(str(e))
        
    except KeyboardInterrupt:
        logger.warning("Execution interrupted by user (KeyboardInterrupt)")
        widgets.blank()
        widgets.text("Execution interrupted by user")

    except Exception as e:
        logger.exception("Fatal error in main execution")
        widgets.blank()
        widgets.text(f"FATAL ERROR: {e}")
        widgets.text("Check logs for details.")
        raise

if __name__ == "__main__":
    main()