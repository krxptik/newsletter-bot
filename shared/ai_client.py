from google import genai
import logging

from app.persistence import retrieve_ai_usage, increment_ai_usage

logger = logging.getLogger(__name__)


class AIClientError(Exception):
    """Raised when the AI backend returns a client error."""


class AIClient:
    """Base class for AI clients."""

    def __init__(self, model: str, rpd: int):
        self.model = model
        self.rpd = rpd
        self.request_count = retrieve_ai_usage(model)
        logger.info(f"Client initialised: {model} with RPD limit {rpd}")

    def remaining_requests(self) -> int:
        """Remaining requests today based on local tracking."""
        return self.rpd - self.request_count

    def call_api(self, prompt: str) -> str:
        raise NotImplementedError("Subclasses must implement call_api()")

    def _check_limit(self):
        if self.request_count >= self.rpd:
            logger.critical(f"RPD limit reached: {self.request_count}/{self.rpd}")
            raise AIClientError("Daily request limit reached")
        
    def _post_request(self):
        self.request_count = increment_ai_usage(self.model)
        logger.info(f"Requests used: {self.request_count}/{self.rpd}")


GEMINI_LIMITS = {
    'gemini-2.5-flash': {'rpm': 5, 'tpm': 250000, 'rpd': 20}
}

GEMMA_LIMITS = {
    'gemma-4-31b-it': {'rpm': 15, 'tpm': None, 'rpd': 1500}
}


class GeminiClient(AIClient):
    def __init__(self, api_key: str, model: str = 'gemini-2.5-flash'):
        if model not in GEMINI_LIMITS:
            raise ValueError(f"Unknown Gemini model: {model}")
        limits = GEMINI_LIMITS[model]
        super().__init__(model=model, rpd=limits['rpd'])
        self.client = genai.Client(api_key=api_key)
        self.rpm = limits['rpm']
        self.tpm = limits['tpm']

    @classmethod
    def from_env(cls, model: str = 'gemini-2.5-flash') -> 'GeminiClient':
        import os
        api_key = os.getenv("GOOGLE_AI_API_KEY")
        if not api_key:
            raise AIClientError("GOOGLE_AI_API_KEY not set in environment")
        return cls(api_key=api_key, model=model)

    def call_api(self, prompt: str) -> str:
        self._check_limit()
        logger.debug(f"Calling Gemini API ({len(prompt)} chars)")
        try:
            response = self.client.models.generate_content(
                model=self.model,
                contents=prompt
            )
            self._post_request()
            text = response.text
            if text is None:
                raise AIClientError("Empty response from Gemini API")
            return text
        except Exception as e:
            logger.error(f"Gemini API call failed: {e}")
            raise AIClientError(str(e)) from e


class GemmaClient(AIClient):
    def __init__(self, api_key: str, model: str = 'gemma-4-31b-it'):
        if model not in GEMMA_LIMITS:
            raise ValueError(f"Unknown Gemma model: {model}")
        limits = GEMMA_LIMITS[model]
        super().__init__(model=model, rpd=limits['rpd'])
        self.client = genai.Client(api_key=api_key)
        self.rpm = limits['rpm']
        self.tpm = limits['tpm']

    @classmethod
    def from_env(cls, model: str = 'gemma-4-31b-it') -> 'GemmaClient':
        import os
        api_key = os.getenv("GOOGLE_AI_API_KEY")
        if not api_key:
            raise AIClientError("GOOGLE_AI_API_KEY not set in environment")
        return cls(api_key=api_key, model=model)

    def call_api(self, prompt: str) -> str:
        self._check_limit()
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