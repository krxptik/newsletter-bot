import io
from contextlib import contextmanager, redirect_stdout
from itertools import zip_longest

from . import _gateway
from .. import constants
from ..render_context import PANEL_RENDER, reset_current_render, set_current_render


@contextmanager
def capture_panel():
    buffer = io.StringIO()
    token = set_current_render(PANEL_RENDER)
    try:
        with redirect_stdout(buffer):
            yield buffer
    finally:
        reset_current_render(token)


def two_panels(left: io.StringIO, right: io.StringIO, *, gap: int = constants.GAP) -> None:
    panel_width = constants.TC_WIDTH
    for left_text, right_text in zip_longest(
        left.getvalue().splitlines(), right.getvalue().splitlines(), fillvalue=""
    ):
        _gateway.write(left_text.ljust(panel_width) + " " * gap + right_text, wrap=False, margin=False)
