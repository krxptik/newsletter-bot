import logging

from ._validation import validate_api_key, ApiKeyValidationResult
from ._display import display_ai_details\

from app.bootstrap.environment import write_env
from shared.ui import widgets
from shared.prompts import ask

logger = logging.getLogger(__name__)

_VALIDATION_ERRORS = {
    ApiKeyValidationResult.INVALID: "Invalid API key.",
    ApiKeyValidationResult.UNKNOWN_ERROR: "Unknown error validating the API key.\nSee logs and try again.",
    ApiKeyValidationResult.TEMPORARY_UNAVAILABLE: "Google servers are temporarily unavailable.\nPlease try again later.",
}


def prompt_and_save_api_key(env_vars: dict, *, cancel_word: str | None) -> bool:
    """Prompt until a valid key is entered (or the user cancels), then persist it.
    Returns True if saved, False if cancelled. Writes to disk itself — callers
    don't need to call write_env afterward."""
    error = ""

    while True:
        display_ai_details(env_vars.get("GOOGLE_AI_API_KEY"))
        widgets.blank()
        if error:
            widgets.text(error)

        user_input = ask("Enter a new Google AI API key", cancel_word=cancel_word)
        if user_input is None:
            return False

        result = validate_api_key(user_input)
        if result == ApiKeyValidationResult.VALID:
            env_vars["GOOGLE_AI_API_KEY"] = user_input
            write_env(env_vars)
            logger.info("API key updated and saved")
            widgets.text("API key saved.")
            return True

        error = _VALIDATION_ERRORS.get(result, "Unknown validation result.")