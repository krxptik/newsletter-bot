from collections.abc import Sequence
from enum import Enum, auto
from typing import Any, NamedTuple, TypeVar, overload

from ._ask import ask
from shared.pager import Pager


PrimaryItem = TypeVar("PrimaryItem")
SecondaryItem = TypeVar("SecondaryItem")
PageItem = TypeVar("PageItem")


class SelectionResult(Enum):
    CANCELLED = auto()
    INVALID = auto()


class Navigation(Enum):
    NEXT = auto()
    PREV = auto()


class PaginationSelectResult(NamedTuple):
    secondary: bool = False
    item_index: int | None = None
    navigation: Navigation | None = None


def select(
    options: Sequence[Any],
    *,
    prompt: str = "",
) -> int | None:
    """
    Prompt for a 1-indexed numeric selection against `options`.

    Returns the zero-based index into `options`, or None if the input is not a
    valid number for the current option list.
    """
    raw = ask(prompt)

    if raw is None:
        return None

    return _parse_selection(raw, len(options))


@overload
def select_item(
    primary: Pager[PrimaryItem],
    secondary: None,
    prompt: str = "",
    cancel_word: str | None = None,
    letters: bool = False,
) -> PrimaryItem | SelectionResult:
    ...


@overload
def select_item(
    primary: Pager[PrimaryItem],
    secondary: Pager[SecondaryItem],
    prompt: str = "",
    cancel_word: str | None = None,
    letters: bool = False,
) -> PrimaryItem | SecondaryItem | SelectionResult:
    ...


def select_item(
    primary: Pager[Any],
    secondary: Pager[Any] | None,
    prompt: str = "",
    cancel_word: str | None = None,
    letters: bool = False,
) -> Any | SelectionResult:
    """
    Prompt for a primary or secondary selection with optional cancellation.

    In single-list mode, `primary` can be selected by number or, when
    `letters=True`, by letter.

    In dual-list mode, numbers map to `primary` and letters map to `secondary`.

    Returns:

    - the selected item from `primary` or `secondary`
    - SelectionResult.CANCELLED when the user types `cancel_word`
    - SelectionResult.INVALID for invalid input or out-of-range selection
    """
    raw = ask(prompt, cancel_word=cancel_word)
    if raw is None:
        return SelectionResult.CANCELLED

    primary_items, primary_start = primary.get_page_items()

    if secondary is None:
        # Single-list mode: use the caller's chosen numeric or alphabetic mode.
        return _select_from_page_items(raw, primary_items, primary_start, letters=letters)

    secondary_items, secondary_start = secondary.get_page_items()

    # Dual-list mode: numbers select from the primary list.
    if raw.isdigit():
        return _select_from_page_items(raw, primary_items, primary_start, letters=False)

    # Dual-list mode: letters select from the secondary list.
    return _select_from_page_items(raw, secondary_items, secondary_start, letters=True)


def select_with_pagination(
    options: list,
    secondary: bool = False,
) -> PaginationSelectResult | None:
    """
    Prompt for a numeric selection or a pagination command.

    `secondary` indicates whether a second list is present. Pagination uses
    `>`/`<` for the primary list and `>>`/`<<` when a second list is available,
    so the commands do not overlap with numeric selection.

    Returns:
    - PaginationSelectResult(secondary=False, item_index=<index>) for a primary
      selection
    - PaginationSelectResult(secondary=False, navigation=Navigation.NEXT |
      Navigation.PREV) for primary pagination
    - PaginationSelectResult(secondary=True, navigation=Navigation.NEXT |
      Navigation.PREV) for secondary pagination when `secondary` is True
    - None if invalid
    """
    raw = ask()
    if raw is None:
        return None

    command = raw.upper()

    if command == ">":
        return PaginationSelectResult(navigation=Navigation.NEXT)
    if command == "<":
        return PaginationSelectResult(navigation=Navigation.PREV)

    if secondary:
        if command == ">>":
            return PaginationSelectResult(secondary=True, navigation=Navigation.NEXT)
        if command == "<<":
            return PaginationSelectResult(secondary=True, navigation=Navigation.PREV)

    if raw.isdigit():
        idx = _parse_selection(raw, len(options))
        if idx is not None:
            return PaginationSelectResult(item_index=idx)

    return None


def _select_from_page_items(
    raw: str,
    items: list[PageItem],
    start: int,
    *,
    letters: bool,
) -> PageItem | SelectionResult:
    """
    Resolve a raw response against a single pager page.

    Returns the selected page item or SelectionResult.INVALID if the response
    cannot be mapped to an item on the current page.
    """
    # Numeric mode uses 1-indexed list positions from the current page.
    if not letters:
        if not raw.isdigit():
            return SelectionResult.INVALID

        idx = int(raw) - start - 1
    # Letter mode maps A, B, C... to the current page offset.
    else:
        if not (raw.isalpha() and len(raw) == 1):
            return SelectionResult.INVALID

        idx = ord(raw.upper()) - ord("A") - start

    if 0 <= idx < len(items):
        return items[idx]

    return SelectionResult.INVALID


def _parse_selection(raw: str, num_options: int) -> int | None:
    """
    Parse a numeric selection displayed to the user as 1-indexed.

    Returns the zero-based index if valid, otherwise None.
    """
    if not raw.isdigit():
        return None

    idx = int(raw) - 1

    if 0 <= idx < num_options:
        return idx

    return None