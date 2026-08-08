import logging

logger = logging.getLogger(__name__)


def index_error_details(details: dict) -> dict[str, dict]:
    """Given a Google API error `details` dict (shape: {'error': {'details': [...]}}),
    return its entries keyed by the last segment of `@type`
    (e.g. 'QuotaFailure', 'RetryInfo', 'ErrorInfo').

    Later entries win if a type appears more than once.
    """
    error_block = details.get('error', {})
    indexed = {}

    for entry in error_block.get('details', []):
        type_str = entry.get('@type', '')
        key = type_str.rsplit('.', 1)[-1] if type_str else ''
        if key:
            indexed[key] = entry

    return indexed