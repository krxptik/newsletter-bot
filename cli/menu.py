from utils.clear_terminal import clear_terminal
from enum import Enum, auto
from typing import List, Optional
from models.article import Article
import math
import time

# Constants 
LIST_NO_WIDTH = 5
ARTICLES_PER_PAGE = 5
LIST_WIDTH = 25
LIST_SPACING = 5

# Enums 
class State(Enum):
    LIST = auto()
    ARTICLE_MENU = auto()
    SELECTED_MENU = auto()
    DETAILS = auto()

class Action(Enum):
    VIEW_DETAILS = 1
    ADD_TO_NEWSLETTER = 2
    REMOVE_FROM_NEWSLETTER = 2
    GO_BACK = 3

# Pager class 
class Pager:
    """Handles pagination for a list of items."""
    def __init__(self, items: List[Article], per_page: int = ARTICLES_PER_PAGE):
        self.items = items
        self.per_page = per_page
        self.page = 1

    def next_page(self) -> None:
        if self.page < self.max_page:
            self.page += 1

    def prev_page(self) -> None:
        if self.page > 1:
            self.page -= 1

    @property
    def is_empty(self) -> bool:
        return len(self.items) == 0

    @property
    def max_page(self) -> int:
        return max(1, math.ceil(len(self.items) / self.per_page))

    def get_page_items(self) -> tuple[List[Article], int]:
        """Returns (items_on_page, start_index)."""
        start = (self.page - 1) * self.per_page
        end = start + self.per_page
        return self.items[start:end], start

# Display Functions 
def truncate(text: str, width: int) -> str:
    """Truncate text with ellipsis if too long."""
    return text[:width - 1] + "…" if len(text) > width else text

def formatted_row(left: str, right: str) -> str:
    return left.ljust(LIST_WIDTH) + (" " * LIST_SPACING) + right

def display_list(available: Pager, selected: Pager) -> None:
    """Display two-column list of available and selected articles."""

    clear_terminal()
    print(formatted_row("Available articles", "Selected"))
    print(formatted_row(("=" * LIST_WIDTH), ("=" * LIST_WIDTH)))

    a_items, a_start = available.get_page_items()
    s_items, s_start = selected.get_page_items()

    for i in range(ARTICLES_PER_PAGE):
        left, right = "", ""

        if i < len(a_items):
            num = f"({a_start + i + 1})".ljust(LIST_NO_WIDTH)
            title = truncate(a_items[i].title, LIST_WIDTH - LIST_NO_WIDTH)
            left = num + title

        if i < len(s_items):
            letter = f"({chr(ord('A') + s_start + i)})".ljust(LIST_NO_WIDTH)
            title = truncate(s_items[i].title, LIST_WIDTH - LIST_NO_WIDTH)
            right = letter + title

        print(formatted_row(left, right))

    print(formatted_row(f"Page {available.page}/{available.max_page}",
                        f"Page {selected.page}/{selected.max_page}"))

def display_article_options(article: Article, is_selected: bool = False) -> None:
    """Display menu options for an article."""
    action = "Remove from" if is_selected else "Add to"
    print(f"\nSelected: {article.title}\n")
    print(f"(1) View details")
    print(f"(2) {action} newsletter")
    print(f"(3) Go back")

def display_details(article: Article) -> None:
    """Show full article details."""
    pub_date = article.pub_date.strftime('%d/%m/%Y') if article.pub_date else 'Unknown'
    
    print(f"{'='*60}")
    print(f"Title: {article.title}")
    print(f"Date: {pub_date}")
    print(f"Source: {article.source}")
    print(f"Link: {article.link}")
    print(f"{'='*60}")
    print(f"\nTags: {', '.join(article.tags)}")
    print(f"\nSummary:\n{article.summary}")
    print(f"\n{'='*60}")
    input("\nPress Enter to go back... ")

def confirm_selection(selected: Pager) -> bool:
    """Show confirmation screen and return True if user confirms."""
    clear_terminal()
    print("You have selected:")
    for i, article in enumerate(selected.items, 1):
        print(f"({i}) {article.title}")
    
    print(f"\n{'='*60}")
    response = input("\nGenerate newsletter? (Y/N): ").strip().upper()
    return response == 'Y'

# Handler functions
class MenuHandler:
    """Handles menu state and transitions."""

    def __init__(self, articles):
        self.available = Pager(articles)
        self.selected = Pager([])
        self.state = State.LIST
        self.current_article: Optional[Article] = None
        self.from_selected = False

    def handle_list_input(self, user_input: str) -> None:
        """Handle input when in list view."""
        cmd = user_input.upper().strip()

        # Navigation commands
        if cmd in ('NEXT', 'NEXT A', 'N A', 'NA'):
            self.available.next_page()
        elif cmd in ('PREV', 'PREV A', 'P A', 'PA'):
            self.available.prev_page()
        elif cmd in ('NEXT S', 'N S', 'NS'):
            self.selected.next_page()
        elif cmd in ('PREV S', 'P S', 'PS'):
            self.selected.prev_page()

        # Selection from available list
        elif cmd.isdigit():
            idx = int(cmd) - 1
            if 0 <= idx < len(self.available.items):
                self.current_article = self.available.items[idx]
                self.from_selected = False
                self.state = State.ARTICLE_MENU

        # Selection from selected list
        elif cmd.isalpha() and len(cmd) == 1:
            idx = ord(cmd) - ord('A')
            if 0 <= idx < len(self.selected.items):
                self.current_article = self.selected.items[idx]
                self.from_selected = True
                self.state = State.SELECTED_MENU

        # Done command
        elif cmd == 'DONE':
            if self.selected.is_empty:
                self._show_error("No articles selected!")
            elif confirm_selection(self.selected):
                self.state = None

    def handle_article_menu(self, user_input: str) -> None:
        """Handle input in article menu."""
        if not user_input.isdigit():
            return
            
        option = int(user_input)

        if option == Action.VIEW_DETAILS.value:
            self.state = State.DETAILS
        elif option == Action.ADD_TO_NEWSLETTER.value:
            self._move_article(self.available, self.selected)
            self.state = State.LIST
        elif option == Action.GO_BACK.value:
            self.state = State.LIST

    def handle_selected_menu(self, user_input: str) -> None:
        """Handle input in selected article menu."""
        if not user_input.isdigit():
            return
            
        option = int(user_input)

        if option == Action.VIEW_DETAILS.value:
            self.state = State.DETAILS
        elif option == Action.REMOVE_FROM_NEWSLETTER.value:
            self._move_article(self.selected, self.available)
            self.state = State.LIST
        elif option == Action.GO_BACK.value:
            self.state = State.LIST

    def _move_article(self, from_pager: Pager, to_pager: Pager) -> None:
        """Move current article from one pager to another."""
        if self.current_article in from_pager.items:
            from_pager.items.remove(self.current_article)
            to_pager.items.append(self.current_article)

    def _show_error(self, message: str) -> None:
        """Display error message temporarily."""
        clear_terminal()
        print(f"{message}")
        print("Returning to menu in 3 seconds...")
        time.sleep(3)
        
# Main menu 
def menu(articles: List[Article]) -> List[Article]:
    """Interactive menu for selecting newsletter articles."""
    handler = MenuHandler(articles)

    while handler.state is not None:
        clear_terminal()

        if handler.state == State.LIST:
            display_list(handler.available, handler.selected)
            print("\nOptions:")
            print("  [number] - Select available article  |  [letter] - Select newsletter article")
            print("  NEXT A / PREV A - Navigate available  |  NEXT S / PREV S - Navigate selected")
            print("  DONE - Generate newsletter")
            user_input = input("> ").strip()
            handler.handle_list_input(user_input)

        elif handler.state in (State.ARTICLE_MENU, State.SELECTED_MENU):
            is_selected = (handler.state == State.SELECTED_MENU)
            display_article_options(handler.current_article, is_selected)
            user_input = input("> ").strip()

            if is_selected:
                handler.handle_selected_menu(user_input)
            else:
                handler.handle_article_menu(user_input)

        elif handler.state == State.DETAILS:
            display_details(handler.current_article)
            # Return to previous menu
            handler.state = State.SELECTED_MENU if handler.from_selected else State.ARTICLE_MENU

    return handler.selected.items