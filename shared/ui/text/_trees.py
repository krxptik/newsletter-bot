def tree_lines(header: str, children: list[str], *, max_children: int = 5) -> str:
    """Header + tree-connected children, truncated after max_children.
    Pure string transform — no printing, no width defaults, no state.
    Caller (widgets.py) decides how this gets written.
    """
    shown = children[:max_children]
    remainder = len(children) - len(shown)
    lines = [header]
    for i, child in enumerate(shown):
        last = (i == len(shown) - 1) and remainder == 0
        lines.append(f"    {'└─' if last else '├─'} {child}")
    if remainder:
        lines.append(f"    └─ …and {remainder} more")
    return "\n".join(lines)
