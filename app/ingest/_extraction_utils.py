from datetime import datetime
from typing import Any, Callable

from trafilatura.settings import Document

from ._fallback_stats import record_fallback
from ._constants import TRUNCATION_MARKERS, MIN_CONTENT_LENGTH

from shared.ai_client import AIClient


def parse_date(raw_date: Any) -> datetime | None:
    """Coerce feedparser or Trafilatura dates into a datetime object."""
    if isinstance(raw_date, datetime):
        return raw_date

    if not raw_date:
        return None

    if hasattr(raw_date, "tm_year") and hasattr(raw_date, "tm_mon") and hasattr(raw_date, "tm_mday"):
        return datetime(raw_date.tm_year, raw_date.tm_mon, raw_date.tm_mday)

    if isinstance(raw_date, str):
        value = raw_date.strip()
        for fmt in ("%Y-%m-%d %H:%M:%S", "%Y-%m-%d", "%Y/%m/%d"):
            try:
                return datetime.strptime(value, fmt)
            except ValueError:
                continue

        try:
            return datetime.fromisoformat(value.replace("Z", "+00:00"))
        except ValueError:
            return None

    return None


def normalise_trafilatura_result(
    result: Document | dict[str, Any] | None,
) -> tuple[str | None, str | None, datetime | None]:
    """Convert Trafilatura's Document/dict outputs into a uniform shape."""
    if result is None:
        return None, None, None

    if isinstance(result, Document):
        return result.text, result.title, parse_date(result.date)

    if isinstance(result, dict):
        return result.get("text"), result.get("title"), parse_date(result.get("date"))

    return None, None, None


def is_truncated(content: str) -> bool:
    content_lower = content.lower()
    if any(marker in content_lower for marker in TRUNCATION_MARKERS):
        return True
    return len(content.strip()) < MIN_CONTENT_LENGTH


def enrich_extraction_with_ai(
    html: str,
    title: str | None,
    pub_date: datetime | None,
    content: str | None,
    client: AIClient,
    ai_extract: Callable[[str, bool, bool, bool, AIClient], dict | None],
    url: str | None = None,
) -> tuple[str | None, str | None, datetime | None]:
    need_title = not bool(title and str(title).strip())
    need_date = pub_date is None
    need_text = content is None or is_truncated(content)

    if need_title or need_date or need_text:
        if url:
            record_fallback(url, need_title, need_date, need_text)
        ai_result = ai_extract(html, need_title, need_date, need_text, client)
        if ai_result:
            content = ai_result.get("text") or content
            title = ai_result.get("title") or title
            pub_date = ai_result.get("date") or pub_date

    return content, title, pub_date