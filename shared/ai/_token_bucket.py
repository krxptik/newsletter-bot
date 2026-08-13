import threading
import time
from collections import deque

# ===== FINE TUNING =====

CHARS_PER_TOKEN = 3
TOKEN_BUDGET_FACTOR = 0.7


# ===== TPM CLASS =====

class TPMLimiter:
    """Thread-safe rolling-window rate limiter for tokens-per-minute quotas.

    Multiple threads can safely call acquire() concurrently — each call
    blocks until there's room in the current 60s window, then reserves
    that many tokens. This trades "everyone fires at once and most get
    429'd" for "everyone queues and each call actually goes through."
    """

    def __init__(self, limit_per_minute: int, window_seconds: float = 60.0):
        self._limit = limit_per_minute
        self._window = window_seconds
        self._lock = threading.Lock()
        self._entries: deque[tuple[float, int]] = deque()  # (timestamp, tokens)
        self._used = 0

    def _prune(self, now: float) -> None:
        """Drop entries that have aged out of the window. Caller holds the lock."""
        while self._entries and now - self._entries[0][0] >= self._window:
            _, tokens = self._entries.popleft()
            self._used -= tokens

    def acquire(self, tokens: int) -> None:
        """Block until `tokens` fit in the current window, then reserve them."""
        effective_limit = int(self._limit * TOKEN_BUDGET_FACTOR)
        # A single request that alone exceeds the effective limit would block
        # forever — cap it and let the API itself accept or reject it.
        tokens = min(tokens, effective_limit)

        while True:
            with self._lock:
                now = time.monotonic()
                self._prune(now)

                if self._used + tokens <= effective_limit:
                    self._entries.append((now, tokens))
                    self._used += tokens
                    return

                oldest_time, _ = self._entries[0]
                wait_for = self._window - (now - oldest_time)

            time.sleep(max(wait_for, 0.05))


def estimate_tokens(text: str) -> int:
    """Rough token estimate (~<CHARS_PER_TOKEN> chars/token for English text). Good enough
    for rate-limiting purposes — we only need to stay under the ceiling,
    not match the provider's tokenizer exactly."""
    return max(1, len(text) // CHARS_PER_TOKEN)