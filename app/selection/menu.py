from enum import Enum, auto
import time

from models import Article
from shared.ui import widgets
from shared.terminal import clear_terminal, display_banner, center_text
from shared.pager import Pager
from app.selection.display import confirm_selection, display_article_details, display_list
from app.selection.constants import ARTICLES_PER_PAGE


class State(Enum):
    LIST = auto()
    ARTICLE_MENU = auto()


class MenuHandler:
    def __init__(self, articles: list[Article]):
        self.available = Pager(articles, ARTICLES_PER_PAGE)
        self.selected = Pager([], ARTICLES_PER_PAGE)
        self.state = State.LIST
        self.current_article: Article | None = None
        self.from_selected = False

    # --- List input ---

    def handle_list_input(self, user_input: str) -> None:
        cmd = user_input.upper().strip()

        if cmd == 'N':
            self.available.next_page()
        elif cmd == 'P':
            self.available.prev_page()
        elif cmd == 'NS':
            self.selected.next_page()
        elif cmd == 'PS':
            self.selected.prev_page()
        elif cmd == '0':
            self._handle_done()
        elif cmd.isdigit():
            self._select_available(int(cmd) - 1)
        elif cmd.isalpha() and len(cmd) == 1:
            self._select_from_selected(ord(cmd) - ord('A'))

    def _select_available(self, idx: int) -> None:
        page_items, start = self.available.get_page_items()
        page_idx = idx - start
        if 0 <= page_idx < len(page_items):
            self.current_article = page_items[page_idx]
            self.from_selected = False
            self.state = State.ARTICLE_MENU

    def _select_from_selected(self, idx: int) -> None:
        page_items, start = self.selected.get_page_items()
        page_idx = idx - start
        if 0 <= page_idx < len(page_items):
            self.current_article = page_items[page_idx]
            self.from_selected = True
            self.state = State.ARTICLE_MENU

    def _handle_done(self) -> None:
        if self.selected.is_empty:
            self._show_error("No articles selected!")
        elif confirm_selection(self.selected):
            self.state = None

    # --- Article menu input ---

    def handle_article_menu(self, user_input: str) -> None:
        if not user_input.isdigit():
            return
        option = int(user_input)
        if option == 1:
            if self.from_selected:
                self._move_article(self.selected, self.available)
                self._show_feedback("Article removed from newsletter.")
            else:
                self._move_article(self.available, self.selected)
                self._show_feedback("Article added to newsletter.")
            self.state = State.LIST
        elif option == 2:
            self.state = State.LIST

    # --- Helpers ---

    def _move_article(self, from_pager: Pager, to_pager: Pager) -> None:
        if self.current_article in from_pager.items:
            from_pager.items.remove(self.current_article)
            to_pager.items.append(self.current_article)
            from_pager.page = min(from_pager.page, from_pager.max_page)

    def _show_error(self, message: str) -> None:
        clear_terminal()
        display_banner(message)
        print("Returning to menu in 2 seconds...")
        time.sleep(2)

    def _show_feedback(self, message: str) -> None:
        clear_terminal()
        print(message)
        time.sleep(1)


# ===== MENU ENTRY POINT =====

def menu(articles: list[Article]) -> list[Article]:
    handler = MenuHandler(articles)

    while handler.state is not None:
        clear_terminal()

        if handler.state == State.LIST:
            display_list(handler.available, handler.selected)

            page_items, start = handler.available.get_page_items()
            end = start + len(page_items)

            print("\n")
            top_msg = f"Select: ({start+1}-{end}) available  |  (A-E) selected"
            options_length = len(top_msg)
            print(center_text(top_msg))
            print(center_text(f"{'Navigate: N / P  |  NS / PS':<{options_length}}"))
            print(center_text(f"{'Continue: (0)':<{options_length}}"))
            handler.handle_list_input(widgets.m_input("> ").strip())

        elif handler.state == State.ARTICLE_MENU:
            assert handler.current_article is not None
            action = "Remove from" if handler.from_selected else "Add to"
            display_article_details(handler.current_article)
            print(f"(1) {action} newsletter")
            print("(2) Go back")
            handler.handle_article_menu(widgets.m_input("> ").strip())

    return handler.selected.items