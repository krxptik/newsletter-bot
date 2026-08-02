import logging
import time
from typing import Literal

from ._edit_flow import prompt_and_save_api_key
from ._display import display_ai_details
from app.bootstrap.environment import read_env
from shared.ui import widgets, PAUSE_SHORT
from shared.prompts import select

logger = logging.getLogger(__name__)


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
            break

    logger.info("AI settings closed")


def _handle_user_input(user_input: int | None, env_vars: dict) -> bool:
    match user_input:
        case 0: env_vars = _edit_api_key(env_vars)
        case 1: return True
    return False


def _edit_api_key(env_vars: dict) -> dict:
    if prompt_and_save_api_key(env_vars, cancel_word="back"):
        time.sleep(PAUSE_SHORT)
    return read_env()