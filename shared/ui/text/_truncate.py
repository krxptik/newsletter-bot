def truncate(text: str, width: int) -> str:
    return text[:width - 1] + "…" if len(text) > width else text