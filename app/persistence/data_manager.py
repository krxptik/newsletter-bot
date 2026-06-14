import json
import logging

def load_file_data(path, default=None) -> list | dict:
    logger = logging.getLogger(__name__)
    logger.debug(f"Loading data from {path}")

    try:
        with open(path, 'r', encoding='utf-8') as f:
            data = json.load(f)
            logger.info(f"Loaded data from {path}")
            return data
    except FileNotFoundError:
        if default is not None:
            logger.warning(f"File not found: {path} — returning default")
            return default
        logger.error(f"File not found: {path}")
        raise
    except json.JSONDecodeError as e:
        logger.error(f"Invalid JSON in file: {e}")
        raise

def overwrite_file_data(data, path) -> None:
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=4)