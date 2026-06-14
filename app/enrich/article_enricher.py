import logging
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed
from enum import Enum, auto

from tqdm import tqdm

from config import AI_PROMPTS_DIR
from models.article import Article
from app.enrich.retry import safe_prompt
from shared.ai_client import AIClient
from shared.exceptions import InsufficientQuotaError

logger = logging.getLogger(__name__)

ARTICLE_PROMPT_FILE = AI_PROMPTS_DIR / "article_prompt.txt"
NEWSLETTER_REQUESTS = 1
BATCH_SIZE = 5


class EnrichResult(Enum):
    SUCCESS = auto()
    SKIP = auto()   # bad format, retries exhausted — move on
    HALT = auto()   # quota gone — stop everything


class AIParsingError(Exception):
    pass


# ===== PROMPT BUILDING =====

def _build_article_prompt(article: Article) -> str:
    with open(ARTICLE_PROMPT_FILE, 'r') as f:
        return f.read() % (article.text)


# ===== RESPONSE PARSING =====

def _parse_article_response(raw_response: str) -> tuple[str, list[str]]:
    if "SUMMARY:" not in raw_response or "TAGS:" not in raw_response:
        raise AIParsingError("Missing SUMMARY or TAGS")

    _, _, after_summary = raw_response.partition("SUMMARY:")
    summary_block, _, tags_part = after_summary.partition("TAGS:")
    summary_block = summary_block.strip()
    tags_block = tags_part.strip()

    if not summary_block or not tags_block:
        raise AIParsingError("Empty SUMMARY or TAGS")

    tags = [tag.strip() for tag in tags_block.split(",")]
    return (summary_block, tags)


# ===== ARTICLE ENRICHMENT =====

def _enrich_article(
    client: AIClient,
    article: Article,
    max_attempts: int
) -> EnrichResult:
    for attempt in range(max_attempts):
        prompt = _build_article_prompt(article)
        success, response = safe_prompt(client, prompt)

        if not success:
            return EnrichResult.HALT

        try:
            summary, tags = _parse_article_response(response)
            article.summary = summary
            article.tags = tags
            return EnrichResult.SUCCESS
        except AIParsingError as e:
            logger.warning(f"Bad response format on attempt {attempt + 1}: {e}")

    logger.warning(f"Skipping article after {max_attempts} attempts")
    return EnrichResult.SKIP


def process_articles(
    client: AIClient,
    articles: list[Article],
    max_attempts: int = 2
) -> list[Article]:
    logger.info(f"Processing {len(articles)} articles")
    successful = []
    halt = threading.Event()  # shared flag to signal early stop

    def process_one(article: Article) -> tuple[Article, EnrichResult]:
        if halt.is_set():
            return (article, EnrichResult.SKIP)
        if client.remaining_requests() <= NEWSLETTER_REQUESTS:
            halt.set()
            return (article, EnrichResult.SKIP)
        result = _enrich_article(client, article, max_attempts)
        if result == EnrichResult.HALT:
            halt.set()
        return (article, result)

    with tqdm(total=len(articles), desc="AI Processing", unit="article",
              bar_format="{desc}: {percentage:3.0f}%|{bar}| {n}/{total} {unit}s [{elapsed} elapsed, ~{remaining} left]") as pbar:
        with ThreadPoolExecutor(max_workers=BATCH_SIZE) as executor:
            futures = {executor.submit(process_one, article): article for article in articles}
            for future in as_completed(futures):
                article, result = future.result()
                pbar.update(1)
                if result == EnrichResult.HALT:
                    logger.error("Halting — quota exhausted")
                    raise InsufficientQuotaError("AI quota exhausted during article processing")
                if result == EnrichResult.SUCCESS:
                    successful.append(article)

    logger.info(f"Processed {len(successful)} articles")
    return successful