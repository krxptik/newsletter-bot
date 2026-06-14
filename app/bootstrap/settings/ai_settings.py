import logging
import time

from shared.terminal import divider, label_line, clear_terminal
from app.bootstrap.setup.env_manager import read_env, write_env
from app.bootstrap.setup.ai_setup import validate_api_key

logger = logging.getLogger(__name__)

PAUSE_SHORT = 3


# ===== DISPLAY =====

def _display_ai_menu(api_key: str) -> None:
    clear_terminal()
    divider()
    print()
    print(label_line("Google AI API key:", api_key or "not set"))
    divider(spacing=True)
    print("Options:")
    print("  (1) Edit API key")
    print("  (2) Back")


# ===== HANDLERS =====

def _edit_api_key(env_vars: dict) -> None:
    message = "You are now editing your Google AI API key.\nEnter a new Google AI API key, or type 'back' to cancel."

    while True:
        clear_terminal()
        divider()
        print()
        print(label_line("Current key:", env_vars.get("GOOGLE_AI_API_KEY") or "not set"))
        divider(spacing=True)
        print(message)

        user_input = input("> ").strip()

        if user_input.lower() == "back":
            return

        if validate_api_key(user_input):
            env_vars["GOOGLE_AI_API_KEY"] = user_input
            write_env(env_vars)
            logger.info("API key updated and saved")
            print("\nAPI key saved.")
            time.sleep(PAUSE_SHORT)
            return

        logger.warning("Invalid API key entered")
        message = "Invalid key. Please try again, or type 'back' to cancel."


# ===== ENTRY POINT =====

def run_ai_settings() -> None:
    logger.info("AI settings opened")
    env_vars = read_env()

    while True:
        _display_ai_menu(env_vars.get("GOOGLE_AI_API_KEY", ""))
        user_input = input("\n> ").strip()

        if not user_input.isdigit():
            continue

        option = int(user_input)

        if option == 1:
            _edit_api_key(env_vars)
            env_vars = read_env()  # reload in case it changed
        elif option == 2:
            logger.info("AI settings closed")
            return