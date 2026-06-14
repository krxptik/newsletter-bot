import logging
import time

from shared.terminal import divider, clear_terminal, label_line
from app.bootstrap.setup.sender_setup import is_valid_sender_details
from app.bootstrap.setup.env_manager import read_env, write_env

logger = logging.getLogger(__name__)

PAUSE_SHORT = 3


# ===== DISPLAY =====

def _display_sender_menu(email: str, app_password: str) -> None:
    clear_terminal()
    divider()
    print()
    print(label_line("Sender email:", email or "not set"))
    print(label_line("Sender app password:", app_password or "not set"))
    divider(spacing=True)
    print("Options:")
    print("  (1) Edit sender details")
    print("  (2) Back")


# ===== HANDLERS =====

def _edit_sender_details(env_vars: dict) -> None:
    message = "You are now editing your sender details."

    while True:
        clear_terminal()
        divider()
        print()
        print(label_line("Sender email:", env_vars.get("EMAIL_ADDRESS") or "not set"))
        print(label_line("Sender app password:", env_vars.get("EMAIL_APP_PASSWORD") or "not set"))
        divider(spacing=True)
        print(message)

        email_input = input("Please enter your email (type 'back' to cancel).\n> ").strip()
        if email_input.lower() == "back":
            return
        
        app_pw_input = input("Please enter your email app password (type 'back' to cancel).\n> ").strip()
        if app_pw_input.lower() == "back":
            return
        
        if is_valid_sender_details(email_input, app_pw_input):
            env_vars["EMAIL_ADDRESS"] = email_input
            env_vars["EMAIL_APP_PASSWORD"] = app_pw_input
            write_env(env_vars)
            logger.info("New sender credentials accepted and saved")
            print("\nSender details saved.")
            time.sleep(PAUSE_SHORT)
            return
        
        logger.warning("Invalid sender email app password entered")
        message = "Invalid sender details. Please try again."


# ===== ENTRY POINT =====

def run_sender_settings() -> None:
    logger.info("Sender settings opened")
    env_vars = read_env()

    while True:
        _display_sender_menu(env_vars.get("EMAIL_ADDRESS"), env_vars.get("EMAIL_APP_PASSWORD"))
        user_input = input("\n> ").strip()

        if not user_input.isdigit():
            continue

        option = int(user_input)

        if option == 1:
            _edit_sender_details(env_vars)
            env_vars = read_env()  # reload in case it changed
        elif option == 2:
            logger.info("AI settings closed")
            return