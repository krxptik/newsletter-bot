import logging

from ._edit_flow import prompt_and_save_api_key
from ._validation import validate_api_key, ApiKeyValidationResult

logger = logging.getLogger(__name__)


def run_ai_setup(env_vars: dict) -> dict:
    logger.info("Running AI setup")
    api_key = env_vars.get("GOOGLE_AI_API_KEY", "")

    if api_key and validate_api_key(api_key) == ApiKeyValidationResult.VALID:
        logger.info("Existing API key valid — skipping AI setup prompt")
        return env_vars

    logger.info("No valid API key found — prompting user")
    prompt_and_save_api_key(env_vars, cancel_word=None)
    return env_vars