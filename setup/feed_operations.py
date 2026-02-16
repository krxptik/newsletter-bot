from setup.ui.input_helpers import get_input_with_back, confirm_action
from setup.validators import is_valid_url, is_unique
from setup.url_helpers import regexify
from setup.ui.display import display_banner, render_feed_section
from data.loader import load_feeds, save_feeds
import time

# ===== CONSTANTS =====

WIDTH = 64

# ===== ADDING HELPER FUNCTIONS =====

def add_non_rss_regex(new_feed: dict) -> bool:
    """Add regex pattern for non-RSS feed with interactive URL examples."""
    print("\n" + "=" * WIDTH)
    print("NON-RSS FEED CONFIGURATION".center(WIDTH))
    print("=" * WIDTH)
    print("\nNon-RSS feeds require a URL pattern to identify articles.")
    print("Please provide two example article URLs from this feed.\n")
    
    url1 = get_input_with_back(
        "Example article URL 1:",
        validator=is_valid_url,
        error_msg="Invalid URL format."
    )
    if url1 is None:
        return False
    
    url2 = get_input_with_back(
        "Example article URL 2:",
        validator=is_valid_url,
        error_msg="Invalid URL format."
    )
    if url2 is None:
        return False
    
    pattern = regexify(url1, url2)
    
    if pattern is None:
        print("\nERROR: URLs must be from the same domain.")
        print("       Please try again with URLs from the same website.")
        time.sleep(3)
        return False
    
    print(f"\nGenerated pattern: {pattern}")
    
    print("\nIs the publish date visible on article pages?")
    print("(This helps the scraper find the publication date)")
    
    allow_fallback = confirm_action("Publish date visible?")
    
    new_feed['article_regex'] = pattern
    new_feed['allow_regex_fallback'] = allow_fallback
    
    return True


def process_add(f_type: str, feeds: list) -> dict | None:
    """Interactive flow to add a new feed with validation and confirmation."""
    display_banner(f"ADD {f_type} FEED")
    
    print(f"You are now adding a {f_type} feed.")
    print("Ensure you have entered the feed details correctly.\n")
    print("=" * WIDTH)
    
    new_feed = {'type': f_type}
    
    new_url = get_input_with_back(
        f"{f_type} feed URL:",
        validator=is_valid_url,
        error_msg="Invalid URL format."
    )
    if new_url is None:
        return None
    
    new_feed['url'] = new_url
    
    new_name = get_input_with_back(
        f"{f_type} feed name:",
        validator=lambda x: len(x.strip()) > 0,
        error_msg="Name cannot be empty."
    )
    if new_name is None:
        return None
    
    new_feed['name'] = new_name
    
    unique, error_msg = is_unique(new_feed, feeds)
    if not unique:
        print(f"\nERROR: {error_msg}")
        time.sleep(3)
        return None
    
    if f_type == "NON-RSS":
        if not add_non_rss_regex(new_feed):
            return None
    
    display_banner("CONFIRM NEW FEED")
    print(f"\nType: {f_type}")
    print(f"Name: {new_feed['name']}")
    print(f"URL:  {new_feed['url']}")
    
    if f_type == "NON-RSS":
        print(f"Pattern: {new_feed.get('article_regex', 'N/A')}")
        print(f"Date fallback: {new_feed.get('allow_regex_fallback', False)}")
    
    if not confirm_action("\nAdd this feed?"):
        print("\nWARNING: Feed not added.")
        time.sleep(2)
        return None
    
    return new_feed


# ===== REMOVE HELPER FUNCTIONS =====

def process_remove(f_type: str, feeds: list, partitioned: dict) -> bool:
    """Remove a feed interactively, returns True if feed was removed."""
    if not partitioned[f_type]:
        print("\nWARNING: No feeds to remove.")
        time.sleep(2)
        return False
    
    print("\nSELECT FEED TO REMOVE:")
    print("=" * WIDTH)
    for i, feed in enumerate(partitioned[f_type], 1):
        print(f"  [{i}] {feed['name']}")
        print(f"      {feed['url']}\n")
    print("=" * WIDTH)
    print("Enter feed number or name (or 'back' to cancel)")
    
    removal_input = input("> ").strip()
    
    if removal_input.lower() == 'back':
        return False
    
    feed_to_remove = None
    
    if removal_input.isdigit():
        idx = int(removal_input) - 1
        if 0 <= idx < len(partitioned[f_type]):
            feed_to_remove = partitioned[f_type][idx]
    else:
        for feed in partitioned[f_type]:
            if feed['name'] == removal_input:
                feed_to_remove = feed
                break
    
    if feed_to_remove:
        if confirm_action(f"Remove '{feed_to_remove['name']}'?"):
            partitioned[f_type].remove(feed_to_remove)
            feeds.remove(feed_to_remove)
            print(f"\nSUCCESS: Removed '{feed_to_remove['name']}'")
            return True
        else:
            print("\nWARNING: Removal cancelled.")
    else:
        print(f"\nERROR: Feed not found: {removal_input}")
    
    time.sleep(2)
    return False


# ===== FEED MANAGEMENT =====

def handle_feed_type(f_type: str, feeds: list, partitioned: dict):
    """Handle add/remove/continue for a single feed type."""
    while True:
        render_feed_section(f_type, partitioned[f_type])
        user_input = input("> ").strip().lower()

        if user_input == "add":
            new_feed = process_add(f_type, feeds)
            
            if new_feed is not None:
                feeds.append(new_feed)
                partitioned[f_type].append(new_feed)
                print("\nSUCCESS: Feed added successfully!")
                time.sleep(2)
            else:
                print("\nWARNING: Add operation cancelled.")
                time.sleep(2)

        elif user_input == "remove":
            process_remove(f_type, feeds, partitioned)

        elif user_input == "continue":
            if confirm_action(f"Confirm {f_type} feeds?"):
                break

        else:
            print("\nERROR: Invalid option. Choose: add, remove, or continue")
            time.sleep(2)


def ensure_feeds():
    """Configure all feed types interactively with add/remove/continue options."""
    feeds = load_feeds()
    
    r_feeds = [feed for feed in feeds if feed['type'] == "RSS"]
    h_feeds = [feed for feed in feeds if feed['type'] == "HYBRID"]
    n_feeds = [feed for feed in feeds if feed['type'] == "NON-RSS"]
    
    partitioned = {
        "RSS": r_feeds,
        "HYBRID": h_feeds,
        "NON-RSS": n_feeds
    }
    
    ordered_types = ("RSS", "HYBRID", "NON-RSS")

    for f_type in ordered_types:
        handle_feed_type(f_type, feeds, partitioned)
    
    save_feeds(feeds)
    print("\nSUCCESS: All feeds saved!")