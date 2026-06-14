import math

from models.article import Article
from app.selection.constants import ARTICLES_PER_PAGE


class Pager:
    """Handles pagination for a list of items."""

    def __init__(self, items: list[Article], per_page: int = ARTICLES_PER_PAGE):
        self.items = items
        self.per_page = per_page
        self.page = 1

    @property
    def is_empty(self) -> bool:
        return len(self.items) == 0

    @property
    def max_page(self) -> int:
        return max(1, math.ceil(len(self.items) / self.per_page))

    def next_page(self) -> None:
        if self.page < self.max_page:
            self.page += 1

    def prev_page(self) -> None:
        if self.page > 1:
            self.page -= 1

    def get_page_items(self) -> tuple[list[Article], int]:
        """Returns (items_on_page, start_index)."""
        start = (self.page - 1) * self.per_page
        end = start + self.per_page
        return self.items[start:end], start