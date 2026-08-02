import time

from ._gateway import write, blank
from .. import constants, screen
from ..text import wrap_text, dot_leader_line, label_line, tree_lines


def text(message: str, *, justify: str = "left") -> None:
    """Generic freeform prose — the fallback component for anything
    that isn't a semantic widget (banner, menu, list)."""
    write(message, justify=justify)


def notify(message: str) -> None:
    text(message)
    time.sleep(constants.PAUSE_SHORT)


def banner(header: str, *, width: int = screen.WIDTH, clear: bool = False) -> None:
    if clear:
        screen.clear()
    screen.divider(width)
    blank()
    write(wrap_text(header, width, justify="center"), wrap=False, margin=False)
    blank()
    screen.divider(width)


def banner_figlet(header: str = "ellie!", width: int = screen.WIDTH) -> None:
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
        lines.append("")
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


def label_block(
        labels: list[str],
        values: list[str],
        *,
        sep: str = "",
        empty_message: str = "Nothing to show.",
        overflow: str | None = None) -> None:
    if not labels or not values:
        text(empty_message)
        return
    label_width = max(len(str(label)) for label in labels)
    lines = [label_line(label, value, constants.CONTENT_WIDTH,
                        sep=sep, label_width=label_width, overflow=overflow)
             for label, value in zip(labels, values)]
    write("\n".join(lines), overflow=overflow)


def enumerated_list(
        start: int, 
        values: list[str], 
        *, 
        empty_message: str = "Nothing to show.", 
        letters: bool = True, 
        overflow: str | None = None) -> None:
    if not values:
        text(empty_message)
        return
    labels = [f"[{chr(ord('A') + i - 1) if letters else i}]" for i in range(start, start + len(values))]
    label_block(labels, values, overflow=overflow)


