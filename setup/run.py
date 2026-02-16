from setup.ui.display import display_banner
from setup.env_config import ensure_env
from setup.feed_operations import ensure_feeds
import time

# ===== CONSTANTS =====

WIDTH = 64


# ===== MAIN SETUP FUNCTION =====

def run_setup():
    """Main setup orchestration function for environment and feed configuration."""
    display_banner("NEWSLETTER BOT SETUP")

    print("\nBefore you begin:\n")
    print("  • Ensure all fields are entered correctly.")
    print("  • Completed sections cannot be revisited.")
    print("  • Restart the program if changes are required.")

    print("\n" + "-" * WIDTH)
    print("Loading environment variable setup in 10 seconds...".center(WIDTH))
    print("-" * WIDTH + "\n")

    time.sleep(10)

    display_banner("NEWSLETTER BOT SETUP")
    ensure_env()
    print("Environment variables all accounted for.")
    print("Loading feed setup in 5 seconds...")
    time.sleep(5)

    display_banner("NEWSLETTER BOT SETUP")
    ensure_feeds()
    print("Feed configuration complete.")
    print("Setup finished!")
    time.sleep(3)