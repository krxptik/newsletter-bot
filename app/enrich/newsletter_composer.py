from path_config import AI_PROMPTS_DIR
from models import Article
from app.enrich.retry import safe_prompt
from app.enrich.article_enricher import AIParsingError
from shared.ai_client import AIClient
import logging

logger = logging.getLogger(__name__)

NEWSLETTER_PROMPT_FILE = AI_PROMPTS_DIR / "newsletter_prompt.txt"

FALLBACK_TITLE = "Newsletter"
FALLBACK_SUMMARY = "Generated automatically"


# ===== PROMPT BUILDING =====

def _build_newsletter_prompt(articles: list[Article]) -> str:
    summaries = [
        f"{i+1}. {article.summary}"
        for i, article in enumerate(articles)
    ]
    with open(NEWSLETTER_PROMPT_FILE, 'r') as f:
        return f.read() % ("\n".join(summaries))


# ===== RESPONSE PARSING =====

def _parse_newsletter_response(raw_response: str) -> tuple[str, str]:
    if "TITLE:" not in raw_response or "SUMMARY:" not in raw_response:
        raise AIParsingError("Missing TITLE or SUMMARY")

    _, _, after_title = raw_response.partition("TITLE:")
    title_block, _, summary_part = after_title.partition("SUMMARY:")
    title_block = title_block.strip()
    summary_block = summary_part.strip()

    if not title_block or not summary_block:
        raise AIParsingError("Empty TITLE or SUMMARY")

    return (title_block, summary_block)


# ===== NEWSLETTER METADATA GENERATION =====

def generate_newsletter_metadata(
    client: AIClient,
    articles: list[Article],
    max_attempts: int = 2
) -> tuple[str, str]:
    if client.remaining_requests() <= 0:
        logger.warning("No quota left for newsletter generation — using fallback")
        return (FALLBACK_TITLE, FALLBACK_SUMMARY)

    for attempt in range(max_attempts):
        prompt = _build_newsletter_prompt(articles)
        success, response = safe_prompt(client, prompt)

        if not success or response is None:
            logger.warning("Newsletter generation failed — using fallback")
            return (FALLBACK_TITLE, FALLBACK_SUMMARY)

        try:
            return _parse_newsletter_response(response)
        except AIParsingError as e:
            logger.warning(f"Bad response format on attempt {attempt + 1}: {e}")

    logger.warning(f"Newsletter parsing failed after {max_attempts} attempts — using fallback")
    return (FALLBACK_TITLE, FALLBACK_SUMMARY)