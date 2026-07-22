from typing import overload

from shared.ui import widgets


@overload
def ask(prompt: str = "", *, cancel_word: None = None) -> str: ...


@overload
def ask(prompt: str = "", *, cancel_word: str = "back") -> str | None: ...


def ask(prompt: str = "", *, cancel_word: str | None = None) -> str | None:
    """
    Prompt for a line of input.

    If `prompt` is given, it's rendered above the input line via widgets.write().
    Returns the stripped input, or None if the user types `cancel_word`
    (case-insensitive). Pass cancel_word=None to disable cancellation.
    """
    if prompt:
        widgets.write(prompt, wrap=False)

    if cancel_word is not None:
        widgets.write(f"(Type '{cancel_word}' to cancel)")

    raw = widgets.m_input("> ").strip()

    if cancel_word is not None and raw.lower() == cancel_word.lower():
        return None

    return raw