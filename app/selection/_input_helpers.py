from models import Article
from shared.ui import widgets
from shared.prompts import select_item, SelectionResult
from shared.pager import Pager


def input_article_selection(
        primary: Pager, secondary: Pager | None = None, 
        *, prompt = "Enter article number or letter", letters: bool = False) -> Article | None:

    while True:
        result = select_item(
            primary,
            secondary,
            prompt=prompt,
            cancel_word="back",
            letters=letters
        )

        match result:
            case SelectionResult.CANCELLED: return
            case SelectionResult.INVALID: widgets.notify("ERROR: Invalid input.")
            case _: return result