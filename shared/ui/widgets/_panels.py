import io
from contextlib import contextmanager, redirect_stdout, ExitStack
from itertools import zip_longest

from . import _gateway
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
    buffer = io.StringIO()

    orig_write = _gateway.write
    orig_apply_margin = _gateway.apply_margin
    orig_divider = screen.divider
    orig_screen_apply_margin = screen.apply_margin

    def tc_write(text: str = "", **kwargs):
        kwargs["width"] = constants.TC_CONTENT_WIDTH
        kwargs["center_margin"] = constants.TC_CENTER_MARGIN
        return orig_write(text, **kwargs)

    def tc_divider(width: int = constants.TC_WIDTH):
        return orig_divider(width, constants.TC_CENTER_MARGIN)

    def tc_gateway_apply_margin(text: str, margin: int = constants.TC_CENTER_MARGIN):
        return orig_apply_margin(text, margin)

    def tc_screen_apply_margin(text: str, margin: int = constants.TC_CENTER_MARGIN):
        return orig_screen_apply_margin(text, margin)

    with ExitStack() as stack:
        # _gateway.write / _gateway.apply_margin: reached by every widget in
        # _semantic.py, since they all call `_gateway.write(...)` directly.
        stack.enter_context(_patched(_gateway, "write", tc_write))
        stack.enter_context(_patched(_gateway, "apply_margin", tc_gateway_apply_margin))
        # screen.divider / screen.apply_margin: screen.py owns its own
        # apply_margin binding (imported from ..text), used inside divider().
        stack.enter_context(_patched(screen, "divider", tc_divider))
        stack.enter_context(_patched(screen, "apply_margin", tc_screen_apply_margin))
        # text_blocks.apply_margin: used internally by format_block() for the
        # per-line margin, called from _gateway.write() via format_block().
        stack.enter_context(_patched(text_blocks, "apply_margin", tc_gateway_apply_margin))
        with redirect_stdout(buffer):
            yield buffer


def two_panels(left: io.StringIO, right: io.StringIO, *, gap: int = constants.GAP) -> None:
    panel_width = constants.TC_WIDTH
    for left_text, right_text in zip_longest(
        left.getvalue().splitlines(), right.getvalue().splitlines(), fillvalue=""
    ):
        _gateway.write(left_text.ljust(panel_width) + " " * gap + right_text, wrap=False, margin=False)
