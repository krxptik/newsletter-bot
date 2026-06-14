import logging
from datetime import date
from config import RUNTIME_DIR
from app.persistence.data_manager import load_file_data, overwrite_file_data

logger = logging.getLogger(__name__)

AI_USAGE_FILE = RUNTIME_DIR / "ai_usage.json"


def _load_ai_usage(path=AI_USAGE_FILE) -> dict:
    logger.debug(f"Loading AI usage from {path}")
    data = load_file_data(path, default={})
    logger.debug(f"Loaded usage data for {len(data)} model(s)")
    return data


def _save_ai_usage(data: dict, path=AI_USAGE_FILE) -> None:
    logger.debug(f"Saving AI usage to {path}")
    overwrite_file_data(data, path)
    logger.debug("AI usage saved")


def _get_or_create_entry(data: dict, model: str) -> dict:
    """Return today's usage entry for model, creating it if absent."""
    today = date.today().isoformat()
    entry = data.get(model)

    if entry and entry.get("date") == today:
        return entry
    
    if entry:
        logger.info(f"New day detected for {model} — resetting usage")
    else:
        logger.info(f"No usage entry for {model} — creating one")
    
    data[model] = {"date": today, "requests_used": 0} # Modifies data parameter
    return data[model]


def retrieve_ai_usage(model: str) -> int:
    data = _load_ai_usage()
    entry = _get_or_create_entry(data, model)
    _save_ai_usage(data)
    logger.debug(f"Usage for {model} today: {entry['requests_used']}")
    return entry["requests_used"]


def increment_ai_usage(model: str) -> int:
    """Increment usage by 1 and return new count."""
    data = _load_ai_usage()
    entry = _get_or_create_entry(data, model)
    entry["requests_used"] += 1
    _save_ai_usage(data)
    logger.info(f"Updated {model} usage to {entry['requests_used']}")
    return entry["requests_used"]