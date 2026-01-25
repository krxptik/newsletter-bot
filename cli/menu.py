from datetime import datetime
import os
import math
import time
from typing import List, Optional
from models.article import Article

# --- Constants ---
ARTICLES_PER_PAGE = 5

# --- Menu States ---
STATE_LIST = 1
STATE_ARTICLE_MENU = 2
STATE_DETAILS = 3
STATE_SELECTED_MENU = 4

# --- Helper Functions ---

def clear_terminal() -> None:
    """Clear the terminal screen."""
    os.system('cls' if os.name == 'nt' else 'clear')


def truncate(text: str, width: int) -> str:
    """
    Truncate a string to a maximum width, adding an ellipsis if needed.

    Args:
        text (str): Text to truncate.
        width (int): Maximum width of the string.

    Returns:
        str: Truncated string.
    """
    return text[:width - 1] + "…" if len(text) > width else text


def display_list(articles: List[Article], selected: List[Article], page: int) -> None:
    """
    Display a paginated list of available articles and selected articles.

    Args:
        articles (List[Article]): List of available articles.
        selected (List[Article]): List of selected articles.
        page (int): Current page number.
    """
    max_page = max(1, math.ceil(len(articles) / ARTICLES_PER_PAGE))
    clear_terminal()
    print("Available articles:".ljust(30) + "Selected")
    print(("=" * 25).ljust(30) + ("=" * 20))

    start_idx = (page - 1) * ARTICLES_PER_PAGE
    end_idx = page * ARTICLES_PER_PAGE

    for i in range(start_idx, end_idx):
        article_text, selected_text = "", ""
        if i < len(articles):
            article_text = f"({i+1})".ljust(5) + truncate(articles[i].title, 20).ljust(25)
        if i < len(selected):
            selected_text = f"({chr(ord('A') + i)})".ljust(5) + truncate(selected[i].title, 20)
        print(article_text + selected_text)

    print(f"Page {page} of {max_page}\n")


def display_list_options() -> str:
    """
    Show the input prompt for navigating the list of articles.

    Returns:
        str: User input.
    """
    text = (
        "Options:\n"
        "* Enter an article number.\n"
        "* Enter 'next' or 'prev' to navigate the list\n"
        "* Enter 'done' to create the newsletter\n"
        "> "
    )
    return input(text)


def display_article_menu(title: str) -> Optional[int]:
    """
    Display options for a selected article in the main list.

    Args:
        title (str): Article title.

    Returns:
        Optional[int]: Selected option number, or None if invalid input.
    """
    text = (
        f"You have selected {title}. Would you like to:\n"
        "(1) View the article's details (tags, summary, and link)\n"
        "(2) Put the article in the newsletter\n"
        "(3) Go back\n"
        "> "
    )
    response = input(text)
    if not response.isdigit():
        return None
    return int(response)


def display_selected_menu(title: str) -> Optional[int]:
    """
    Display options for a selected article already in the newsletter.

    Args:
        title (str): Article title.

    Returns:
        Optional[int]: Selected option number, or None if invalid input.
    """
    text = (
        f"You have selected {title}. Would you like to:\n"
        "(1) View the article's details (tags, summary, and link)\n"
        "(2) Remove the article from the newsletter\n"
        "(3) Go back\n"
        "> "
    )
    response = input(text)
    if not response.isdigit():
        return None
    return int(response)


def display_details(article: Article) -> None:
    """
    Display detailed information about a single article.

    Args:
        article (Article): Article object to display.
    """
    pub_date = article.pub_date.strftime('%d/%m/%Y') if article.pub_date else 'None'
    print(
        f"Title: {article.title}\n"
        f"Date: {pub_date}\n"
        f"Source: {article.source}\n"
        f"Link: {article.link}\n"
        f"Tags: {article.tags}\n"
        f"Summary: {article.summary}\n"
    )
    input("Enter any key to go back.\n> ")


def display_confirm(selected: List[Article]) -> str:
    """
    Display a summary of selected articles and ask for confirmation.

    Args:
        selected (List[Article]): List of selected articles.

    Returns:
        str: User input (Y/N).
    """
    clear_terminal()
    print("You have selected:")
    for i, article in enumerate(selected):
        print(f"({i+1}) {article.title}")
    return input("\nProceed to generate the newsletter? (Y/N)\n> ")


# --- Main Menu Function ---

def menu(articles: List[Article]) -> List[Article]:
    """
    Main CLI menu for browsing articles and selecting them for the newsletter.

    Args:
        articles (List[Article]): List of available articles.

    Returns:
        List[Article]: List of articles selected for the newsletter.
    """
    state = STATE_LIST
    page = 1
    selection: Optional[int] = None
    article_menu = True
    selected: List[Article] = []

    while True:
        max_page = max(1, math.ceil(len(articles) / ARTICLES_PER_PAGE))

        if state == STATE_LIST:
            display_list(articles, selected, page)
            option = display_list_options()

            if option == 'next' and page < max_page:
                page += 1
            elif option == 'prev' and page > 1:
                page -= 1
            elif option == 'done':
                if not selected:
                    clear_terminal()
                    print('You have not selected any articles.')
                    print('Returning to main menu in 3 seconds...')
                    time.sleep(3)
                    continue
                if display_confirm(selected).upper() == 'Y':
                    clear_terminal()
                    return selected
            elif option.isdigit():
                state = STATE_ARTICLE_MENU
                selection = int(option) - 1
            elif option.isalpha() and len(option) == 1:
                selection = ord(option.upper()) - ord('A')
                if selection < len(selected):
                    state = STATE_SELECTED_MENU

        elif state == STATE_ARTICLE_MENU:
            clear_terminal()
            article = articles[selection]
            option = display_article_menu(article.title)
            if option is None:
                continue
            if option == 1:
                state = STATE_DETAILS
                article_menu = True
            elif option == 2:
                state = STATE_LIST
                selected.append(articles.pop(selection))
            elif option == 3:
                state = STATE_LIST

        elif state == STATE_SELECTED_MENU:
            clear_terminal()
            article = selected[selection]
            option = display_selected_menu(article.title)
            if option is None:
                continue
            if option == 1:
                state = STATE_DETAILS
                article_menu = False
            elif option == 2:
                state = STATE_LIST
                articles.append(selected.pop(selection))
            elif option == 3:
                state = STATE_LIST

        elif state == STATE_DETAILS:
            clear_terminal()
            article = articles[selection] if article_menu else selected[selection]
            display_details(article)
            state = STATE_ARTICLE_MENU if article_menu else STATE_SELECTED_MENU
