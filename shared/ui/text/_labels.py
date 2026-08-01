from ._layout import wrap_text
from ._truncate import truncate


def label_line(label: str, value: str, width: int, *,
               sep: str = "", label_width: int | None = None,
               justify: str = "left", overflow: str | None = None) -> str:
    label_width = label_width if label_width else len(str(label))
    sep_length = len(sep) + 2
    value_length = width - label_width - sep_length
    value_indent = label_width + sep_length

    if overflow == "truncate":
        rendered_value = truncate(str(value), value_length)
    else:
        rendered_value = wrap_text(str(value), width=value_length, indent=value_indent, justify=justify)

    return f"{label:<{label_width}} {sep + ' ' if sep else ""}{rendered_value}"