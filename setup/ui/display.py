from utils.clear_terminal import clear_terminal

# ===== DISPLAY FUNCTIONS =====

def display_banner(header: str, width=64):
    """Display centered banner with header text."""
    clear_terminal()
    print()
    print("=" * width)
    print(header.upper().center(width))
    print("=" * width)
    print()


def render_feed_section(f_type: str, feeds: list, width=64):
    """Display feed list and available options for a specific feed type."""
    display_banner(f"{f_type} FEEDS")

    if not feeds:
        print("No feeds configured.\n".center(width))
    else:
        print()
        for i, feed in enumerate(feeds, 1):
            print(f"  [{i}] {feed['name']}")
            print(f"       {feed['url']}\n")

    print("-" * width)
    print("  add      - Add new feed")
    print("  remove   - Remove existing feed")
    print("  continue - Confirm and proceed")
    print("-" * width)