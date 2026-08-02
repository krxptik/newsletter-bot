import io
import sys
from contextlib import contextmanager, redirect_stdout, ExitStack
from itertools import zip_longest

from ._gateway import write
from .. import constants, screen
from ..text import _blocks as text_blocks


@contextmanager
def _patched(obj, name, new_value):
    """Temporarily set obj.name = new_value, restoring it afterward."""
    old_value = getattr(obj, name)
    setattr(obj, name, new_value)
    try:
        yield old_value
    finally:
        setattr(obj, name, old_value)


@contextmanager
def capture_panel():
    module = sys.modules[__name__]
    buffer = io.StringIO()

    orig_write = module.write
    orig_divider = screen.divider
    orig_apply_margin = screen.apply_margin

    def tc_write(text: str = "", **kwargs):
        kwargs["width"] = constants.TC_CONTENT_WIDTH
        kwargs["center_margin"] = constants.TC_CENTER_MARGIN
        return orig_write(text, **kwargs)

    def tc_divider(width: int = constants.TC_WIDTH):
        return orig_divider(width, constants.TC_CENTER_MARGIN)

    def tc_apply_margin(text: str, margin: int = constants.TC_CENTER_MARGIN):
        return orig_apply_margin(text, margin)

    with ExitStack() as stack:
        stack.enter_context(_patched(module, "write", tc_write))
        stack.enter_context(_patched(screen, "divider", tc_divider))
        stack.enter_context(_patched(screen, "apply_margin", tc_apply_margin))
        stack.enter_context(_patched(text_blocks, "apply_margin", tc_apply_margin))
        stack.enter_context(_patched(constants, "CONTENT_WIDTH", constants.TC_CONTENT_WIDTH))
        with redirect_stdout(buffer):
            yield buffer


def two_panels(left: io.StringIO, right: io.StringIO, *, gap: int = constants.GAP) -> None:
    panel_width = constants.TC_WIDTH
    for left_text, right_text in zip_longest(
        left.getvalue().splitlines(), right.getvalue().splitlines(), fillvalue=""
    ):
        write(left_text.ljust(panel_width) + " " * gap + right_text, wrap=False, margin=False)