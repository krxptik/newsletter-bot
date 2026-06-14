import logging
from config import CONFIG_DIR
from app.persistence.data_manager import load_file_data, overwrite_file_data

logger = logging.getLogger(__name__)

EMAIL_ADDRS_FILE = CONFIG_DIR / "email_addrs.json"


def load_address_book() -> dict:
    logger.debug(f"Loading address book from {EMAIL_ADDRS_FILE}")
    data = load_file_data(EMAIL_ADDRS_FILE, default={"groups": {}, "ungrouped": []})
    logger.debug(f"Loaded {len(data.get('groups', {}))} group(s), {len(data.get('ungrouped', []))} ungrouped recipient(s)")
    return data


def save_address_book(data: dict) -> None:
    logger.debug(f"Saving address book to {EMAIL_ADDRS_FILE}")
    overwrite_file_data(data, EMAIL_ADDRS_FILE)
    logger.debug("Address book saved")


def get_groups(data: dict) -> dict:
    return data.get("groups", {})


def get_ungrouped(data: dict) -> list:
    return data.get("ungrouped", [])