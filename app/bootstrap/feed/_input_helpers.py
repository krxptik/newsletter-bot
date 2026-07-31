import time

import requests

from ._url_tools import is_valid_url_format, normalise_url

from models import Feed
from shared.prompts import ask, select_item, SelectionResult
from shared.ui import widgets, PAUSE_SHORT
from shared.safe_request import safe_get
from shared.pager import Pager


# ===== add_feed INPUT =====

def input_url(prompt: str, session: requests.Session) -> requests.Response | None:
    while True:
        raw = ask(prompt, cancel_word="back")
        if raw is None:
            return None

        if not raw:
            widgets.text("ERROR: Input cannot be empty.")
            widgets.blank()
            time.sleep(PAUSE_SHORT)
            continue
        
        url = normalise_url(raw)
        if not is_valid_url_format(url):
            widgets.text("ERROR: Invalid URL format. Please re-enter.")
            widgets.blank()
            time.sleep(PAUSE_SHORT)
            continue

        response = safe_get(url, session)
        if response is None:
            widgets.text("ERROR: Could not reach that URL. Please check it and try again.")
            time.sleep(PAUSE_SHORT)
            continue

        return response


def input_name() -> str | None:
    while True:
        raw = ask("Feed name:", cancel_word="back")
        if raw is None:
            return None

        if not raw:
            widgets.text("ERROR: Input cannot be empty.")
            time.sleep(PAUSE_SHORT)
            continue

        return raw
    

# ===== remove_feed INPUT =====

def input_feed_selection(pager: Pager) -> Feed | None:
    while True:
        result = select_item(pager, None, prompt="Enter feed number", cancel_word="back")
        
        match result:
            case SelectionResult.CANCELLED:
                return
            case SelectionResult.INVALID:
                widgets.blank()
                widgets.text("ERROR: Invalid input.")
                time.sleep(PAUSE_SHORT)
            case _:
                return result