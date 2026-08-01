from .. import constants
from ..text import format_block, apply_margin


def write(
        text: str = "", *, 
        wrap: bool = True, 
        margin: bool = True, justify: str = "left", end: str = "\n",
        width: int = constants.CONTENT_WIDTH, center_margin: int = constants.CENTER_MARGIN,
        overflow: str | None = None) -> None:

    render_margin = constants.MARGIN if margin else 0

    if overflow == "truncate":
        text = format_block(
            text,
            width=width,
            wrap=False,
            truncate_lines=True,
            justify=justify,
            margin=render_margin,
        )
    elif overflow == "wrap":
        text = format_block(
            text,
            width=width,
            wrap=True,
            truncate_lines=False,
            justify=justify,
            margin=render_margin,
        )
    elif wrap or margin:
        text = format_block(
            text,
            width=width,
            wrap=wrap,
            justify=justify,
            margin=render_margin
        )

    if center_margin:
        text = apply_margin(text, center_margin)
    print(text, end=end)


def blank(lines: int = 1) -> None:
    print("\n" * (lines - 1))


def m_input(prompt: str = ""):
    """Prompt the user with a standard margined input label.

    The prompt text is padded using the shared UI margin before it is
    displayed and passed to Python's built-in input() function.
    """
    response = input(apply_margin(prompt, constants.MARGIN + constants.CENTER_MARGIN))
    blank()
    return response