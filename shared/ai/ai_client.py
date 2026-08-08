import logging

from google import genai

from .token_bucket import TPMLimiter, estimate_tokens

logger = logging.getLogger(__name__)


class AIClientError(Exception):
    """Raised when the AI backend returns a client error."""


class AIClient:
    """Base class for AI clients."""

    def __init__(self, model: str, rpd: int, tpm: int | None = None):
        from app.persistence.ai_usage_store import retrieve_ai_usage

        self.model = model
        self.rpd = rpd
        self.tpm = tpm
        self.request_count = retrieve_ai_usage(model)
        self._tpm_limiter = TPMLimiter(tpm) if tpm else None
        logger.info(f"Client initialised: {model} with RPD limit {rpd}, TPM limit {tpm}")

    def remaining_requests(self) -> int:
        """Remaining requests today based on local tracking."""
        return self.rpd - self.request_count

    def call_api(self, prompt: str) -> str:
        raise NotImplementedError("Subclasses must implement call_api()")

    def _check_limit(self):
        if self.request_count >= self.rpd:
            logger.critical(f"RPD limit reached: {self.request_count}/{self.rpd}")
            raise AIClientError("Daily request limit reached")

    def _throttle(self, prompt: str) -> None:
        """Block (across all threads sharing this client) until there's
        room in the current per-minute token window for this prompt."""
        if self._tpm_limiter is None:
            return
        tokens = estimate_tokens(prompt)
        self._tpm_limiter.acquire(tokens)
        logger.debug(f"TPM throttle: reserved ~{tokens} tokens")

    def _post_request(self):
        from app.persistence.ai_usage_store import increment_ai_usage

        self.request_count = increment_ai_usage(self.model)
        logger.info(f"Requests used: {self.request_count}/{self.rpd}")


GEMMA_LIMITS = {
    # tpm confirmed from live 429 payload:
    # "Quota exceeded for metric: ...generate_content_free_tier_input_token_count
    #  ... quotaValue: '16000'"
    'gemma-4-31b-it': {'rpm': 15, 'tpm': 16000, 'rpd': 1500}
}


class GemmaClient(AIClient):
    def __init__(self, api_key: str, model: str = 'gemma-4-31b-it'):
        if model not in GEMMA_LIMITS:
            raise ValueError(f"Unknown Gemma model: {model}")
        limits = GEMMA_LIMITS[model]
        super().__init__(model=model, rpd=limits['rpd'], tpm=limits['tpm'])
        self.client = genai.Client(api_key=api_key)
        self.rpm = limits['rpm']

    @classmethod
    def from_env(cls, model: str = 'gemma-4-31b-it') -> 'GemmaClient':
        import os
        api_key = os.getenv("GOOGLE_AI_API_KEY")
        if not api_key:
            raise AIClientError("GOOGLE_AI_API_KEY not set in environment")
        return cls(api_key=api_key, model=model)

    def call_api(self, prompt: str) -> str:
        self._check_limit()
        self._throttle(prompt)
        logger.debug(f"Calling Gemma API ({len(prompt)} chars)")
        try:
            response = self.client.models.generate_content(
                model=self.model,
                contents=prompt
            )
            self._post_request()
            text = response.text
            if text is None:
                raise AIClientError("Empty response from Gemma API")
            return text
        except Exception as e:
            logger.error(f"Gemma API call failed: {e}")
            raise AIClientError(str(e)) from e