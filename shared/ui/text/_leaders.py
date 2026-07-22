from ._truncate import truncate


def dot_leader_line(left: str, right: str, width: int, fill: str = ".", spacing: int = 1) -> str:
    """'left ..................... right', truncating left if the line can't fit."""
    gap = width - len(left) - len(right) - (spacing * 2)
    if gap < 3:
        max_left = width - len(right) - (spacing * 2) - 4
        left = truncate(left, max(max_left, 1))
        gap = width - len(left) - len(right) - (spacing * 2)
    leader = fill * max(gap, 0)
    return f"{left}{' ' * spacing}{leader}{' ' * spacing}{right}"