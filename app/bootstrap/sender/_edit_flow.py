import logging

from ._validation import is_valid_sender_details
from ._display import display_sender_details

from app.bootstrap.environment import write_env
from shared.ui import widgets
from shared.prompts import ask

logger = logging.getLogger(__name__)


def prompt_and_save_sender_details(env_vars: dict, *, cancel_word: str | None) -> bool:
    """Prompt until valid sender details are entered (or the user cancels), then persist them.
    Returns True if saved, False if cancelled. Writes to disk itself — callers
    don't need to call write_env afterward."""
    error = ""

    while True:
        display_sender_details(env_vars.get("EMAIL_ADDRESS"), env_vars.get("EMAIL_APP_PASSWORD"))
        widgets.blank()
        if error:
            widgets.text(error)

        email_input = ask("Please enter your email", cancel_word=cancel_word)
        if email_input is None:
            return False

        app_pw_input = ask("Please enter your email app password", cancel_word=cancel_word)
        if app_pw_input is None:
            return False

        if is_valid_sender_details(email_input, app_pw_input):
            env_vars["EMAIL_ADDRESS"] = email_input
            env_vars["EMAIL_APP_PASSWORD"] = app_pw_input
            write_env(env_vars)
            logger.info("New sender credentials accepted and saved")
            widgets.text("Sender details saved.")
            return True

        logger.warning("Invalid sender email/app password entered")
        error = "Invalid sender details."