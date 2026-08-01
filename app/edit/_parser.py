import re

from shared.url_utils import is_valid_url_format

_HEADER_RE = re.compile(r'^(#{1,2})(?!#)(?:\s+(.*))?$')


class DraftParsingError(Exception):
    """Raised when the edited draft can't be parsed back into a newsletter."""


# ===== ENTRY POINT =====

def parse_draft(text: str) -> dict:
    lines = text.splitlines()
    headers = _find_headers(lines)

    titles = [(i, txt) for level, i, txt in headers if level == 1]
    articles = [(i, txt) for level, i, txt in headers if level == 2]

    if not articles:
        raise DraftParsingError("No articles found — at least one '## ' heading is required.")
    if not titles:
        raise DraftParsingError("Newsletter title (a single '# ' line) is missing.")
    if len(titles) > 1:
        raise DraftParsingError("More than one '# ' title line found — there should be exactly one.")

    title_idx, title = titles[0]
    if title_idx > articles[0][0]:
        raise DraftParsingError("The title must come before the first article.")
    if not title:
        raise DraftParsingError("Newsletter title text is missing (the text after '# ').")

    summary = _join_paragraph(lines[title_idx + 1:articles[0][0]])
    if not summary:
        raise DraftParsingError("Newsletter summary is missing (the text under the title).")

    article_rows = []
    for pos, (start, article_title) in enumerate(articles):
        end = articles[pos + 1][0] if pos + 1 < len(articles) else len(lines)
        article_rows.append(_parse_article_block(article_title, lines[start + 1:end]))

    return {"title": title, "summary": summary, "article_rows": article_rows}


# ===== HEADER LOCATION =====

def _match_header(line: str) -> tuple[int, str] | None:
    """Return (level, heading_text) for a level-1 or level-2 markdown header
    line, else None. Guards against '###+' being misread as a shorter
    header, and tolerates a header with no text after it (e.g. an
    accidentally emptied '##') by returning an empty heading_text rather
    than failing to match at all — that emptiness gets caught later as a
    normal validation error instead of silently vanishing into body text."""
    match = _HEADER_RE.match(line.strip())
    if not match:
        return None
    return len(match.group(1)), (match.group(2) or "").strip()


def _find_headers(lines: list[str]) -> list[tuple[int, int, str]]:
    headers = []
    for i, line in enumerate(lines):
        match = _match_header(line)
        if match:
            level, heading_text = match
            headers.append((level, i, heading_text))
    return headers


# ===== ARTICLE PARSING =====

def _parse_article_block(title: str, body: list[str]) -> dict:
    if not title:
        raise DraftParsingError("An article is missing its title (the text after '## ').")

    source_idx, source = _extract_field(body, "Source:", title)
    link_idx, link = _extract_field(body, "Link:", title)

    summary = _join_paragraph(body[:min(source_idx, link_idx)])
    if not summary:
        raise DraftParsingError(f"Article '{title}' is missing its summary text.")

    if not is_valid_url_format(link):
        raise DraftParsingError(f"Article '{title}' has an invalid link: '{link}'.")

    return {"title": title, "summary": summary, "source": source, "link": link}


def _extract_field(body: list[str], prefix: str, article_title: str) -> tuple[int, str]:
    idx = next((i for i, l in enumerate(body) if l.strip().startswith(prefix)), None)
    if idx is None:
        raise DraftParsingError(f"Article '{article_title}' is missing its '{prefix}' line.")
    return idx, body[idx].split(":", 1)[1].strip()


# ===== TEXT HELPERS =====

def _join_paragraph(lines: list[str]) -> str:
    """Join non-empty lines into one paragraph — tolerates an accidental
    line break in the middle of a summary."""
    return " ".join(l.strip() for l in lines if l.strip())