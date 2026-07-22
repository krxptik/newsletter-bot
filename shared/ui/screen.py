import os

from .constants import CENTER_MARGIN, WIDTH
from .text import apply_margin


def clear() -> None:
    os.system('cls' if os.name == 'nt' else 'clear')


def divider(width: int = WIDTH) -> None:
    """A structural rule — always full width, centered in the terminal."""
    raw_line = "─" * width
    centered_line = apply_margin(raw_line, CENTER_MARGIN)
    print(centered_line)