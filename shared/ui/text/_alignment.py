def _justify(text: str, width: int, justify: str = "left") -> str:
    stripped = text.rstrip()
    if justify == "right":
        return stripped.rjust(width)
    elif justify == "center":
        return stripped.center(width)
    return stripped


def align_lines(lines: list[str], width: int, indent: int = 0, justify: str = "left") -> list[str]:
    """Apply left/center/right alignment (and optional indent) to already-wrapped lines."""
    indent_spacing = " " * indent
    return [indent_spacing + _justify(line, width, justify) for line in lines]