import logging
import time

from ._edit_flow import prompt_and_save_api_key
from ._display import display_ai_details

from app.bootstrap.environment import read_env
from shared.ui import widgets, PAUSE_SHORT
from shared.prompts import select

logger = logging.getLogger(__name__)


def _edit_api_key(env_vars: dict) -> None:
    if prompt_and_save_api_key(env_vars, cancel_word="back"):
        time.sleep(PAUSE_SHORT)


def _handle_user_input(user_input: int | None, env_vars: dict) -> bool:
    match user_input:
        case 0:
            _edit_api_key(env_vars)
            env_vars = read_env()
        case 1:
            logger.info("AI settings closed")
            return True
    return False


def run_ai_settings() -> None:
    logger.info("AI settings opened")
    env_vars = read_env()
    options = ["Edit API key", "Back"]

    while True:
        display_ai_details(env_vars.get("GOOGLE_AI_API_KEY"))
        widgets.blank()
        widgets.options_menu(options)
        widgets.blank()

        user_input = select(options)
        should_exit = _handle_user_input(user_input, env_vars)

        if should_exit:
            return