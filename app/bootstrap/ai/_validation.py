import logging
from enum import Enum, auto

from google import genai
from google.genai.errors import ClientError, ServerError

from shared.google_errors import index_error_details

logger = logging.getLogger(__name__)


class ApiKeyValidationResult(Enum):
    VALID = auto()
    INVALID = auto()
    TEMPORARY_UNAVAILABLE = auto()
    UNKNOWN_ERROR = auto()


def _get_error_reason(e: ClientError) -> str | None:
    details = getattr(e, "details", None)
    if not isinstance(details, dict):
        return None
    return index_error_details(details).get('ErrorInfo', {}).get('reason')


def validate_api_key(api_key: str) -> ApiKeyValidationResult:
    logger.debug("Validating Google API key")
    try:
        client = genai.Client(api_key=api_key)
        next(client.models.list())
        logger.info("Google API key is valid")
        return ApiKeyValidationResult.VALID
    except ClientError as e:
        reason = _get_error_reason(e)
        if reason == "API_KEY_INVALID":
            logger.warning("Google API key validation failed (invalid key)")
            return ApiKeyValidationResult.INVALID
        logger.warning(f"ClientError during API key validation, reason={reason}: {e}")
        return ApiKeyValidationResult.UNKNOWN_ERROR
    except ServerError:
        logger.warning("Google servers temporarily unavailable")
        return ApiKeyValidationResult.TEMPORARY_UNAVAILABLE