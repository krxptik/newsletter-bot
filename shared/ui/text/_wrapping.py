MIN_HYPHEN_BEFORE = 3
MIN_WORD_LENGTH = 6


# ===== WORD FITTING =====

def _fits_whole(word: str, remaining_length: int) -> bool:
    return len(word) <= remaining_length


def _can_hyphenate(word: str, remaining_length: int) -> bool:
    return len(word) >= MIN_WORD_LENGTH and remaining_length - 1 >= MIN_HYPHEN_BEFORE


def _split_hyphenated(word: str, remaining_length: int) -> tuple[str, str]:
    """Split word into (left_with_hyphen, right_remainder) at the hyphenation point."""
    left, right = word[:remaining_length - 1], word[remaining_length - 1:]
    return left + "-", right


# ===== LINE BUILDING =====

def _process_word(words: list[str], idx: int, current: str, width: int, lines: list[str]) -> tuple[int, str]:
    """Handle a single word: append it, hyphenate-split it, or force a line break.
    Mutates `words` in place when hyphenating. Returns the updated (idx, current).
    """
    word = words[idx]
    remaining_length = width - len(current)

    if remaining_length > 0:
        if _fits_whole(word, remaining_length):
            return idx + 1, current + word + " "

        if _can_hyphenate(word, remaining_length):
            left, right = _split_hyphenated(word, remaining_length)
            words[idx] = right
            return idx, current + left

    lines.append(current.rstrip())
    return idx, ""


def _wrap_paragraph(paragraph: str, width: int) -> list[str]:
    """Wrap a single paragraph (no newlines) into width-constrained lines,
    hyphenating long words where meaningful."""
    leading_ws = paragraph[:len(paragraph) - len(paragraph.lstrip())]
    words = paragraph.split()
    idx = 0
    lines = []
    current = leading_ws

    while idx < len(words):
        idx, current = _process_word(words, idx, current, width, lines)

    if current:
        lines.append(current.rstrip())

    return lines


# ===== ENTRY POINT =====

def wrap_lines(text: str, width: int) -> list[str]:
    """Break text into wrapped lines, hyphenating long words where meaningful.
    Explicit newlines in `text` are treated as hard line breaks — each
    paragraph between them is wrapped independently. Blank lines are
    preserved as empty lines in the output. Pure line-breaking — no
    indent, no alignment.
    """
    lines = []

    for paragraph in text.split("\n"):
        if not paragraph.strip():
            lines.append("")
            continue
        lines.extend(_wrap_paragraph(paragraph, width))

    return lines