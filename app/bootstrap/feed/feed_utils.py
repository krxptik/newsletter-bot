TRUNCATION_MARKERS = [
    "continue reading",
    "read more",
    "read the full",
    "[...]"
]


# ===== RSS UTILS =====

def _is_truncated(content: str) -> bool:
    content_lower = content.lower()
    if any(marker in content_lower for marker in TRUNCATION_MARKERS):
        return True
    return len(content.strip()) < 200


def is_scraping_required(feed) -> bool:
    sample = feed.entries[:3]
    truncated = 0

    for entry in sample:
        content = ""

        if hasattr(entry, "content"):
            content = entry.content[0].value if entry.content else ""
        elif hasattr(entry, "summary"):
            content = entry.summary
        elif hasattr(entry, "description"):
            content = entry.description

        if not content or _is_truncated(content):
            truncated += 1

    return truncated >= 2


# ===== FEED VALIDATION =====

def validate_unique_feed(new_feed: dict, feeds: list) -> str | None:
    for feed in feeds:
        if new_feed["url"] == feed["url"]:
            return f"Feed URL already exists: {feed['name']}"
        if new_feed["name"] == feed["name"]:
            return f"Feed name already in use: {feed['name']}"
    return None