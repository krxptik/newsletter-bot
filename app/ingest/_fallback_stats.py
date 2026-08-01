import logging
import threading
from collections import Counter
from urllib.parse import urlparse

logger = logging.getLogger(__name__)

_lock = threading.Lock()
_attempts: Counter[str] = Counter()
_fallbacks: Counter[str] = Counter()


def record_attempt(url: str) -> None:
    domain = urlparse(url).netloc
    with _lock:
        _attempts[domain] += 1


def record_fallback(url: str, need_title: bool, need_date: bool, need_text: bool) -> None:
    domain = urlparse(url).netloc
    missing = ", ".join(
        name for name, needed in (("title", need_title), ("date", need_date), ("text", need_text)) if needed
    )
    with _lock:
        _fallbacks[domain] += 1
    logger.info(f"AI fallback triggered for {domain} (missing: {missing}) — {url}")


def log_summary() -> None:
    with _lock:
        attempts, fallbacks = dict(_attempts), dict(_fallbacks)

    if not attempts:
        return

    logger.info("Trafilatura fallback summary:")
    for domain in sorted(attempts):
        total = attempts[domain]
        used_ai = fallbacks.get(domain, 0)
        rate = (used_ai / total * 100) if total else 0
        logger.info(f"  {domain}: {used_ai}/{total} articles needed AI fallback ({rate:.0f}%)")

    total_all = sum(attempts.values())
    fallback_all = sum(fallbacks.values())
    logger.info(f"  TOTAL: {fallback_all}/{total_all} ({(fallback_all/total_all*100) if total_all else 0:.0f}%)")


def reset() -> None:
    with _lock:
        _attempts.clear()
        _fallbacks.clear()