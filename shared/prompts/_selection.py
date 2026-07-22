from enum import Enum, auto

from ._ask import ask
from ._navigation import Navigation


class SelectionResult(Enum):
    CANCELLED = auto()
    INVALID = auto()


def _parse_selection(raw: str, num_options: int) -> int | None:
    """
    Parse a 1-indexed numeric selection.

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


def select_item(
    options: list,
    *,
    prompt: str = "",
    cancel_word: str | None = None,
) -> int | SelectionResult:
    """
    Prompt for a numeric selection against `options` (1-indexed on screen).

    Returns:

    - the zero-based index into `options` for a valid selection
    - SelectionResult.CANCELLED when the user types `cancel_word`
    - SelectionResult.INVALID for invalid input
    """
    raw = ask(prompt, cancel_word=cancel_word)

    if raw is None:
        return SelectionResult.CANCELLED

    parsed = _parse_selection(raw, len(options))

    if parsed is None:
        return SelectionResult.INVALID

    return parsed


def select_with_pagination(
    options: list,
) -> int | Navigation | None:
    """
    Prompt for a numeric selection against `options` (1-indexed on screen).

    Returns:

    - zero-based index into `options`
    - Navigation.NEXT
    - Navigation.PREV
    - None if invalid
    """
    raw = ask()

    match raw.upper():
        case "N":
            return Navigation.NEXT
        case "P":
            return Navigation.PREV

    return _parse_selection(raw, len(options))