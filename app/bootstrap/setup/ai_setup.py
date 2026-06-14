import logging
from google import genai
from google.genai.errors import ClientError, ServerError
from shared.terminal import clear_terminal, divider, label_line, center_text

logger = logging.getLogger(__name__)


def validate_api_key(api_key: str) -> bool:
    logger.debug("Validating Google API key")
    try:
        client = genai.Client(api_key=api_key)
        next(client.models.list())
        logger.info("Google API key is valid")
        return True
    except ClientError:
        logger.warning("Google API key validation failed (ClientError)")
        return False
    except ServerError:
        logger.warning("Google servers temporarily unavailable")
        print("\nGemini servers are temporarily unavailable.\nPlease try again shortly.")
        return False


def run_ai_setup(env_vars: dict) -> dict:
    logger.info("Running AI setup")
    api_key = env_vars.get("GOOGLE_AI_API_KEY", "")

    if api_key and validate_api_key(api_key):
        logger.info("Existing API key valid — skipping AI setup prompt")
        return env_vars

    logger.info("No valid API key found — prompting user")
    message = "No valid Google API key found. Please enter a valid key."

    while True:
        clear_terminal()
        divider()
        print()
        print(center_text(label_line("Google API key:", api_key or "not set")))
        divider(spacing=True)
        print(message)

        user_input = input("> ").strip()
        logger.debug("User provided an API key input")

        if validate_api_key(user_input):
            env_vars["GOOGLE_AI_API_KEY"] = user_input
            logger.info("New API key accepted and saved")
            return env_vars

        logger.warning("Entered API key was invalid")
        message = "\nInvalid key. Please try again."