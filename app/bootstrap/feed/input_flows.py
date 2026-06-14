import time

from app.bootstrap.feed.url_tools import is_valid_url, normalise_url, regexify
from shared.terminal import confirmation, divider


# ===== NON-RSS ENRICHMENT =====

def _collect_article_regex() -> str | None:
    while True:
        print("Non-RSS feeds require two example *article* URLs to generate a URL pattern for scraping.")
        print("URLs must be from the same domain.")
        
        url1 = input_url("Example article URL 1:")
        if url1 is None:
            return None

        url2 = input_url("Example article URL 2:")
        if url2 is None:
            return None

        pattern = regexify(url1, url2)
        if pattern is None:
            print("\nERROR: URLs must be from the same domain.")
            print("Please try again with URLs from the same website.")
            time.sleep(3)
            continue

        print(f"\nGenerated pattern: {pattern}")
        return pattern


def collect_non_rss_enrichment() -> dict | None:
    regex = _collect_article_regex()
    if regex is None:
        return None

    divider(single=True, spacing=True)
    print("Some websites display the publish date on the article page itself.")
    print("If visible, it will be used to filter out older articles.")

    fallback = confirmation("Is the publish date visible on article pages?")

    return {
        "article_regex": regex,
        "allow_regex_fallback": fallback
    }


# ===== INPUT HELPERS =====

def input_url(prompt: str) -> str | None:
    print(f"\n{prompt}")
    print("(Type 'back' to cancel)")
    while True:
        raw = input("> ").strip()
        if raw.lower() == 'back':
            return None
        
        url = normalise_url(raw)
        if not is_valid_url(url):
            print("\nERROR: Invalid URL format. Please re-enter.")
            time.sleep(1)
            continue

        return url


def add_name() -> str | None:
    while True:
        print("Feed name:")
        print("(Type 'back' to cancel)")
        raw = input("> ").strip()
        if raw.lower() == 'back':
            return None
        
        if not raw:
            print("ERROR: Input cannot be empty.")
            time.sleep(1)
            continue

        return raw