from .. import constants
from ..text import format_block, apply_margin
from ..render_context import RenderOptions, current_render


def write(
        text: str = "", *,
        wrap: bool = True,
        margin: bool = True, justify: str = "left", end: str = "\n",
        render: RenderOptions | None = None,
        overflow: str | None = None) -> None:

    render = render or current_render()
    width = render.resolve(render.content_width, constants.CONTENT_WIDTH)
    center_margin = render.resolve(render.center_margin, constants.CENTER_MARGIN)

    render_margin = constants.MARGIN if margin else 0

    truncate = overflow == "truncate"
    wrap_arg = False if truncate else wrap

    text = format_block(
        text,
        width=width,
        wrap=wrap_arg,
        truncate_lines=truncate,
        justify=justify,
        margin=render_margin,
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