from enum import Enum, auto
from typing import NamedTuple, Any

from ._ask import ask


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


def select(
    options: list,
    *,
    prompt: str = "",
) -> int | None:
    """
    Prompt for a numeric selection against `options` (1-indexed on screen).

    Returns the zero-based index into `options`, or None if invalid.
    """
    raw = ask(prompt)

    if raw is None:
        return None

    return _parse_selection(raw, len(options))


def _parse_item_selection(
        raw: str, 
        primary: list,
        p_start: int = 1,
        secondary: list | None = None,
        s_start: str = "A") -> Any | None:
    """
    Parse a 1-indexed numeric or alphabetic selection.

    Returns the zero-based index if valid, otherwise None.
    """
    if raw.isdigit():
        idx = int(raw) - p_start

        if 0 <= idx < len(primary):
            return primary[idx]

    elif raw.isalpha() and len(raw) == 1:
        if not secondary:
            return None 
        
        idx = ord(raw.upper()) - ord(s_start.upper())

        if 0 <= idx < len(secondary):
            return secondary[idx]

    return None


def select_item(
    primary: list,
    primary_start: int = 0,
    secondary: list | None = None,
    secondary_start: str = "A",
    prompt: str = "",
    cancel_word: str | None = None,
) -> Any | SelectionResult:
    """
    Prompt for a primary or secondary selection with optional cancellation.

    `primary` is selected by number starting at `primary_start` on screen.
    When `secondary` is provided, alphabetic selections starting at
    `secondary_start` map to that list.

    Returns:

    - the selected item from `primary` or `secondary`
    - SelectionResult.CANCELLED when the user types `cancel_word`
    - SelectionResult.INVALID for invalid input
    """
    raw = ask(prompt, cancel_word=cancel_word)

    if raw is None:
        return SelectionResult.CANCELLED

    parsed = _parse_item_selection(
        raw, 
        primary, primary_start, 
        secondary, secondary_start
    )

    if parsed is None:
        return SelectionResult.INVALID

    return parsed


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