import math
from typing import Generic, TypeVar

T = TypeVar("T")

class Pager(Generic[T]):
    """Handles pagination for a list of items."""

    def __init__(self, items: list[T], per_page: int) -> None:
        self.items = items
        self.per_page = per_page
        self.page = 1

    @property
    def is_empty(self) -> bool:
        return not self.items

    @property
    def max_page(self) -> int:
        return max(1, math.ceil(len(self.items) / self.per_page))

    def next_page(self) -> None:
        if self.page < self.max_page:
            self.page += 1

    def prev_page(self) -> None:
        if self.page > 1:
            self.page -= 1

    def get_page_items(self) -> tuple[list[T], int]:
        start = (self.page - 1) * self.per_page
        end = start + self.per_page
        return self.items[start:end], start