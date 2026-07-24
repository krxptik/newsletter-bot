from datetime import datetime
from typing import Any, NamedTuple

import requests

import trafilatura
from bs4 import BeautifulSoup

from ._extraction_utils import parse_date, normalise_trafilatura_result, enrich_extraction_with_ai, is_truncated
from ._ai_fallback import ai_extract

from models import Feed, Article
from shared.safe_request import safe_get
from shared.ai_client import AIClient


class EntryFields(NamedTuple):
    title: str | None
    link: str | None
    pub_date: datetime | None
    content: str | None


class ExtractionResult(NamedTuple):
    text: str | None
    title: str | None
    pub_date: datetime | None
    response: requests.Response | None


def entry_to_article(entry: dict[str, Any], feed_obj: Feed, session: requests.Session, client: AIClient) -> Article | None:
    """Build one Article from a feed entry, using Trafilatura and AI only as fallback."""
    title, link, pub_date, content = _get_entry_core_fields(entry)

    if not link:
        return None

    need_title = not bool(title and str(title).strip())
    need_date = pub_date is None
    need_text = content is None or is_truncated(content)

    if need_title or need_date or need_text:
        refreshed = _refresh_entry_from_url(link, session, need_title, need_date)
        content = refreshed.text or content
        title = refreshed.title or title
        pub_date = refreshed.pub_date or pub_date

        if refreshed.response:
            content, title, pub_date = enrich_extraction_with_ai(
                refreshed.response.text,
                title,
                pub_date,
                content,
                client,
                ai_extract,
            )

    if not (title and link and content):
        return None

    return Article(title, link, pub_date, content, feed_obj.name)


def _get_entry_core_fields(entry: dict[str, Any]) -> EntryFields:
    title = entry.get("title")
    link = entry.get("link")
    pub_date = parse_date(entry.get("published_parsed"))
    content = _extract_rss_content(entry)
    return EntryFields(title, link, pub_date, content)


def _refresh_entry_from_url(
    link: str,
    session: requests.Session,
    need_title: bool,
    need_date: bool,
) -> ExtractionResult:
    response = safe_get(link, session)

    result = trafilatura.bare_extraction(
        response.text,
        include_comments=False,
        favor_precision=True,
        with_metadata=need_title or need_date,
    ) if response else None

    extracted_text, extracted_title, extracted_date = normalise_trafilatura_result(result)
    return ExtractionResult(extracted_text, extracted_title, extracted_date, response)


def _extract_rss_content(entry) -> str | None:
    """Extract and clean article text directly from RSS feed data."""
    content_list = entry.get('content', [{}])
    content_html = content_list[0].get('value') or entry.get('description')
    if not content_html:
        return None
    return BeautifulSoup(content_html, 'html.parser').get_text(strip=True)