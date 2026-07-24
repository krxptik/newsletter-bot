TRUNCATION_MARKERS = [
    "continue reading",
    "read more",
    "read the full",
    "[...]",
]

# ===== SCRAPE DETECTION =====

def _is_truncated(content: str) -> bool:
    content_lower = content.lower()
    if any(marker in content_lower for marker in TRUNCATION_MARKERS):
        return True
    return len(content.strip()) < 200


def _is_scraping_required(feed) -> bool:  # no type hint: pylance mis-narrows `content` in _is_truncated if hinted here
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