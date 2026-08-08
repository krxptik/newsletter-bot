from contextvars import ContextVar, Token
from dataclasses import dataclass
from typing import Optional

from .constants import CENTER_MARGIN, CONTENT_WIDTH, TC_CENTER_MARGIN, TC_CONTENT_WIDTH, TC_WIDTH, WIDTH


@dataclass(frozen=True)
class RenderOptions:
    """Explicit rendering options passed through widget call chains.

    Use `content_width` when you mean the width available for body text
    inside margins. `width` is the overall UI width (useful for structural
    elements like dividers). Any field may be None to indicate "no override".
    """
    width: Optional[int] = None
    content_width: Optional[int] = None
    center_margin: Optional[int] = None

    def resolve(self, value: int | None, default: int) -> int:
        return default if value is None else value


DEFAULT_RENDER = RenderOptions(width=WIDTH, content_width=CONTENT_WIDTH, center_margin=CENTER_MARGIN)
PANEL_RENDER = RenderOptions(width=TC_WIDTH, content_width=TC_CONTENT_WIDTH, center_margin=TC_CENTER_MARGIN)

_CURRENT_RENDER: ContextVar[RenderOptions] = ContextVar("current_render", default=DEFAULT_RENDER)


def current_render() -> RenderOptions:
    return _CURRENT_RENDER.get()


def set_current_render(render: RenderOptions) -> Token:
    return _CURRENT_RENDER.set(render)


def reset_current_render(token: Token) -> None:
    _CURRENT_RENDER.reset(token)


__all__ = ["RenderOptions", "DEFAULT_RENDER", "PANEL_RENDER", "current_render", "set_current_render", "reset_current_render"]