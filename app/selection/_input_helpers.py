import time

from models import Article
from shared.ui import widgets, PAUSE_SHORT
from shared.prompts import select_item, SelectionResult
from shared.pager import Pager


def input_article_selection(
        primary: Pager, secondary: Pager | None = None, 
        *, prompt = "Enter article number or letter") -> Article | None:
    p_items, p_start = primary.get_page_items()
    s_items, s_start = secondary.get_page_items() if secondary else (None, 0)

    while True:
        result = select_item(
            p_items, p_start, 
            s_items, chr(ord("A") + s_start),
            prompt=prompt,
            cancel_word="back"
        )

        match result:
            case SelectionResult.CANCELLED:
                return
            case SelectionResult.INVALID:
                widgets.blank()
                widgets.text("ERROR: Invalid input.")
                time.sleep(PAUSE_SHORT)
            case _:
                return result