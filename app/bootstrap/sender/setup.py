import logging

from ._edit_flow import prompt_and_save_sender_details
from ._validation import is_valid_sender_details

logger = logging.getLogger(__name__)


def run_sender_setup(env_vars: dict) -> dict:
    logger.info("Running sender setup")
    email = env_vars.get("EMAIL_ADDRESS", "")
    app_password = env_vars.get("EMAIL_APP_PASSWORD", "")

    if is_valid_sender_details(email, app_password):
        logger.info("Existing sender credentials valid — skipping sender setup prompt")
        return env_vars

    logger.info("No valid sender credentials — prompting user")
    prompt_and_save_sender_details(env_vars, cancel_word=None)
    return env_vars