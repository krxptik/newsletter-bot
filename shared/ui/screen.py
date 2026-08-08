import os

from .constants import CENTER_MARGIN, WIDTH
from .text import apply_margin
from .render_context import RenderOptions, current_render


def clear() -> None:
    os.system('cls' if os.name == 'nt' else 'clear')


def divider(*, render: RenderOptions | None = None) -> None:
    """A structural rule — always full width, centered in the terminal."""
    render = render or current_render()
    width = render.resolve(render.width, WIDTH)
    center_margin = render.resolve(render.center_margin, CENTER_MARGIN)

    raw_line = "─" * width
    centered_line = apply_margin(raw_line, center_margin)
    print(centered_line)