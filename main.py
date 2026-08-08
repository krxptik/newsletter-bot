# Standard library
import logging

# Third-party
from dotenv import load_dotenv
from tqdm import tqdm

# Local — shared utilities
from shared.logging import setup_logging
from shared.ui import widgets
from shared.exceptions import UserExitError, InsufficientQuotaError, InternetConnectionError
from shared.ai import GemmaClient # current model

# Local — version
from version import __version__

# Local — app
from app import *


setup_logging()


def main():
    logger = logging.getLogger(__name__)

    try:
        # --- Bootstrap ---
        bootstrap.start_initialisation()
        load_dotenv()
        logger.info("NEWSLETTER BOT STARTED")

        # --- AI client ---
        logger.debug("Initialising AI client")
        ai_client = GemmaClient.from_env()

        widgets.banner_figlet()

        # --- Ingest ---
        tqdm.set_lock(tqdm.get_lock())
        feeds, caches = persistence.load_feeds_with_caches()
        matched = persistence.match_feeds_to_caches(feeds, caches)
        logger.info(f"Loaded {len(feeds)} feeds")
        articles = ingest.parse_all(matched, ai_client)
        logger.info(f"Fetched {len(articles)} articles")

        # --- Filter and Prune ---
        articles = filter.filter_articles(articles, ai_client, 1)
        logger.info(f"After pruning: {len(articles)} articles remain")

        # --- Article AI enrichment ---
        logger.info("Starting AI summarisation and tagging...")
        enriched_articles = enrich.process_articles(ai_client, articles)
        logger.info(f"AI processing complete: {len(enriched_articles)} articles enriched")

        # --- Article selection ---
        logger.info("Opening article selection menu...")
        selected_articles = selection.run_selection_menu(enriched_articles)
        logger.info(f"User selected {len(selected_articles)} articles")

        # --- Newsletter detail generation with AI ---
        widgets.banner_figlet()
        logger.info("Generating newsletter title and summary...")
        title, summary = widgets.run_with_spinner(
            "Generating newsletter...",
            enrich.generate_newsletter_metadata,
            ai_client,
            selected_articles
        )
        logger.info(f"Newsletter title: '{title}'")

        # --- Newsletter editing interface ---
        logger.info("Opening newsletter editing interface...")
        context = compose.generate_context(title, summary, selected_articles)
        modified_context = edit.run_markdown_edit(context)

        # --- Newsletter rendering ---
        logger.info("Rendering newsletter HTML...")
        html = render.render_newsletter(modified_context)
        path = render.save_newsletter(html, title)
        logger.info(f"Newsletter saved to: {path}")

        logger.info("Opening newsletter preview in browser...")
        render.preview_newsletter(path)

        # --- Email sending ---
        logger.info("Opening email send menu...")
        em, to_addrs = deliver.send_menu(title, path, html)
        logger.info(f"Sending email to {len(to_addrs)} recipient(s)...")
        deliver.send_email(em, to_addrs)

        # --- Cleanup ---
        logger.info("Saving used article URLs...")
        persistence.save_used_urls(selected_articles)

        logger.info("=" * 64)
        logger.info("PROGRAM COMPLETED SUCCESSFULLY".center(64))
        logger.info("=" * 64)

    except InternetConnectionError:
        logger.info("User declared Internet connection not working.")
        widgets.blank()
        widgets.text("Program ended")

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