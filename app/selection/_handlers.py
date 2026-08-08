import logging

from ._display import display_article_details, display_article_list, display_all_articles, display_confirm
from ._input_helpers import input_article_selection

from shared.core import Pager
from shared.ui import widgets
from shared.prompts import confirmation

logger = logging.getLogger(__name__)
    

def move_article(from_pager: Pager, to_pager: Pager, prompt: str, letters: bool = False, add: bool = True) -> None:
    if from_pager.is_empty:
        logger.warning("No articles to select from.")
        widgets.blank()
        widgets.notify("WARNING: No articles to select from.")
        return

    display_article_list(from_pager, letters=letters)

    selected_article = input_article_selection(from_pager, prompt=prompt, letters=letters)
    if selected_article is None:
        return

    from_pager.items.remove(selected_article)
    to_pager.items.append(selected_article)
    from_pager.page = min(from_pager.page, to_pager.max_page)
    logger.info(f"Article moved: {selected_article.title}")
    widgets.notify(f"Article was {'added to' if add else 'removed from'} the newsletter.")
    return


def view_article(available: Pager, selected: Pager):
    display_all_articles(available, selected)
    widgets.blank()
    article = input_article_selection(available, selected)
    if article is None:
        return

    display_article_details(article)
    widgets.blank()
    widgets.m_input("Press 'enter' to go back.")


def confirm_selected(selected: Pager) -> bool:
    if selected.is_empty:
        widgets.notify("ERROR: No articles selected. Please select before finishing.")
        return False
    
    display_confirm(selected)
    if not confirmation("Generate newsletter with these articles?"):
        return False
    
    return True