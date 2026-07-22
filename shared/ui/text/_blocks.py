from ._layout import wrap_text
from ._truncate import truncate


def apply_margin(text: str, margin: int) -> str:
    prefix = " " * margin
    return "\n".join(prefix + line if line else "" for line in text.splitlines())


def format_block(text: str, *, width: int, wrap: bool = True, justify: str = "left",
                  truncate_lines: bool = False, margin: int = 0) -> str:
    """Compose wrapping/truncation/alignment/margin into a single final string."""
    if not text:
        return ""

    if wrap:
        rendered = wrap_text(text, width, justify=justify)
    elif truncate_lines:
        rendered = "\n".join(truncate(line, width) for line in text.splitlines())
    else:
        rendered = text

    if margin:
        rendered = apply_margin(rendered, margin)

    return rendered