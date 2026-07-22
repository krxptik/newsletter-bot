from ._wrapping import wrap_lines
from ._alignment import align_lines


def wrap_text(text: str, width: int, indent: int = 0, justify: str = "left") -> str:
    """Wrap + align in one call. Used by label_line/label_block and any
    caller that wants both in one shot."""
    lines = wrap_lines(text, width)
    aligned = align_lines(lines, width, indent, justify)
    raw = "\n".join(aligned)
    return raw[indent:]