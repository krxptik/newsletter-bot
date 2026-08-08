from json import JSONDecodeError
import json
import logging
import re
from typing import Any, TYPE_CHECKING

from bs4 import BeautifulSoup

from path_config import INGEST_PROMPTS_DIR
from ._constants import AI_STRIP_TAGS, MAX_HTML_CHARS
from ._extraction_utils import parse_date
from shared.ai import safe_prompt

if TYPE_CHECKING:
    from shared.ai import AIClient

logger = logging.getLogger(__name__)

PROMPT_FILE = INGEST_PROMPTS_DIR / "ai_fallback_prompt.txt"


def ai_extract(html: str, need_title: bool, need_date: bool, need_text: bool, client: "AIClient") -> dict | None:
    """Single AI fallback function, parameterized by what's missing."""
    if not (need_title or need_date or need_text):
        return None

    prompt = _build_prompt(html, need_title=need_title, need_date=need_date, need_text=need_text)
    success, raw = safe_prompt(client, prompt)
    if not success or raw is None:
        return None

    data = _parse_json_response(raw)
    if data is None:
        return None

    result: dict[str, Any] = {}

    if need_text:
        result["text"] = _clean_text(data.get("text"))
        if not result["text"]:
            return None

    if need_title:
        result["title"] = _clean_title(data.get("title"))

    if need_date:
        result["date"] = parse_date(data.get("date"))

    return result


def _trim_html(html: str, max_chars: int = MAX_HTML_CHARS) -> str:
    """Strip low-value tags (scripts, nav, footer, etc.) and cap length
    before the HTML goes anywhere near an AI prompt — this is the single
    biggest lever on per-call token cost, since raw page HTML is mostly
    boilerplate the model doesn't need to find a title/date/body."""
    soup = BeautifulSoup(html, "html.parser")
    for tag in soup.find_all(AI_STRIP_TAGS):
        tag.decompose()

    trimmed = str(soup)
    if len(trimmed) > max_chars:
        trimmed = trimmed[:max_chars]
        logger.debug(f"_trim_html: truncated to {max_chars} chars")

    return trimmed


def _build_prompt(html: str, need_title: bool, need_date: bool, need_text: bool) -> str:
    with open(PROMPT_FILE, "r", encoding="utf-8") as handle:
        template = handle.read()

    return template % (
        "yes" if need_title else "no",
        "yes" if need_date else "no",
        "yes" if need_text else "no",
        _trim_html(html).strip(),
    )


def _parse_json_response(raw: str) -> dict[str, Any] | None:
    text = raw.strip()

    if text.startswith("```"):
        text = re.sub(r"^```(?:json)?\s*", "", text, flags=re.IGNORECASE)
        text = re.sub(r"\s*```$", "", text)

    try:
        parsed = json.loads(text)
    except JSONDecodeError:
        start = text.find("{")
        end = text.rfind("}")
        if start == -1 or end == -1 or end <= start:
            logger.warning("AI response did not contain JSON")
            return None

        try:
            parsed = json.loads(text[start : end + 1])
        except JSONDecodeError:
            logger.warning("AI response JSON could not be parsed")
            return None

    if not isinstance(parsed, dict):
        return None

    return parsed


def _clean_text(value: Any) -> str | None:
    if value is None:
        return None

    text = re.sub(r"\s+", " ", str(value)).strip()
    return text or None


def _clean_title(value: Any) -> str | None:
    return _clean_text(value)