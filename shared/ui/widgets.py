"""
widgets.py — the trunk.

Composes screen primitives and text transforms into semantic UI pieces
(banners, menus, lists) and enforces the one thing worth centralizing:
that written output is wrapped and margined by default.
"""

from . import constants, screen
from .text import format_block, wrap_text, dot_leader_line, label_line, apply_margin, tree_lines


# ===== OUTPUT GATEWAY =====

def write(text: str = "", *, wrap: bool = True, margin: bool = True,
          justify: str = "left", end: str = "\n") -> None:
    if wrap or margin:
        text = format_block(
            text,
            width=constants.CONTENT_WIDTH,
            wrap=wrap,
            justify=justify,
            margin=constants.MARGIN if margin else 0,
        )
    if constants.CENTER_MARGIN:
        text = apply_margin(text, constants.CENTER_MARGIN)
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


# ===== WIDGETS =====

def text(message: str, *, justify: str = "left") -> None:
    """Generic freeform prose — the fallback component for anything
    that isn't a semantic widget (banner, menu, list)."""
    write(message, justify=justify)


def banner(header: str, *, width: int = screen.WIDTH, clear: bool = False) -> None:
    if clear:
        screen.clear()
    screen.divider(width)
    blank()
    write(wrap_text(header, width, justify="center"), wrap=False, margin=False)
    blank()
    screen.divider(width)


def banner_figlet(header: str, width: int = screen.WIDTH) -> None:
    # local import: avoid pyfiglet cost for callers that never use figlet banners
    import pyfiglet
    from version import __version__

    screen.clear()
    screen.divider(width)
    blank()
    figlet = pyfiglet.figlet_format(header, font="dos_rebel", justify="center", width=width)
    write(figlet, wrap=False, margin=False)
    text(f"Running {__version__}.", justify="center")
    blank()
    screen.divider(width)


def options_menu(options: list[str], footer: str | None = None) -> None:
    lines = ["Options:"] + [f"  ({i}) {opt}" for i, opt in enumerate(options, 1)]
    if footer:
        lines.append(footer)
    write("\n".join(lines), wrap=False)


def dot_leader_list(rows: list[tuple[str, str]], empty_message: str = "Nothing to show.") -> None:
    if not rows:
        text(empty_message)
        return
    lines = [dot_leader_line(left, right, constants.CONTENT_WIDTH) for left, right in rows]
    write("\n".join(lines), wrap=False)


def section_header(title: str) -> None:
    """A section title followed by a light single-rule divider — used to
    separate subsections within one screen (e.g. GROUPS vs UNGROUPED)."""
    screen.divider()
    write(title, wrap=False)
    screen.divider()


def tree_list(sections: list[tuple[str, list[str]]], *, max_children: int = 5,
                  empty_message: str = "Nothing to show.") -> None:
    """Render a sequence of tree-connected header+children blocks. Not
    address-book-specific — anywhere a 'header + nested detail lines' shape
    shows up (group rosters, feed lists with sub-detail, etc)."""
    if not sections:
        text(empty_message)
        return
    blocks = [tree_lines(h, c, max_children=max_children) for h, c in sections]
    write("\n\n".join(blocks), wrap=False)


def label_block(labels: list[str], values: list[str], *, sep: str = "", empty_message: str = "Nothing to show."):
    if not labels or not values:
        text(empty_message)
        return
    label_width = max(len(str(label)) for label in labels)
    lines = [label_line(label, value, constants.CONTENT_WIDTH, 
                        sep=sep, label_width=label_width) 
             for label, value in zip(labels, values)]
    write("\n".join(lines))


def enumerated_list(start: int, values: list, empty_message: str = "Nothing to show."):
    if not values:
        text(empty_message)
        return
    labels = [f"[{i}]" for i in range(start, start + len(values))]
    label_block(labels, values)


# ===== PROGRESS DISPLAY =====

def run_with_spinner(message: str, func, *args, **kwargs):
    import itertools
    import sys
    import threading
    import time

    stop_event = threading.Event()

    def _spinner():
        for char in itertools.cycle("⠋⠙⠹⠸⠼⠴⠦⠧⠇⠏"):
            if stop_event.is_set():
                break
            sys.stdout.write(f"\r  {char}  {message}")
            sys.stdout.flush()
            time.sleep(0.1)
        sys.stdout.write("\r" + " " * (len(message) + 6) + "\r")

    t = threading.Thread(target=_spinner)
    t.start()
    try:
        result = func(*args, **kwargs)
    finally:
        stop_event.set()
        t.join()
    return result