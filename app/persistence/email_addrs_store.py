import logging
from typing import Any, cast

from config import CONFIG_DIR
from app.persistence.data_manager import load_file_data, overwrite_file_data

logger = logging.getLogger(__name__)

EMAIL_ADDRS_FILE = CONFIG_DIR / "email_addrs.json"


def load_address_book() -> dict[str, Any]:
    logger.debug(f"Loading address book from {EMAIL_ADDRS_FILE}")
    data = load_file_data(EMAIL_ADDRS_FILE, default={"groups": {}, "ungrouped": []})
    address_book = cast(dict[str, Any], data)
    logger.debug(
        f"Loaded {len(address_book.get('groups', {}))} group(s), "
        f"{len(address_book.get('ungrouped', []))} ungrouped recipient(s)"
    )
    return address_book


def save_address_book(data: dict) -> None:
    logger.debug(f"Saving address book to {EMAIL_ADDRS_FILE}")
    overwrite_file_data(data, EMAIL_ADDRS_FILE)
    logger.debug("Address book saved")


def get_groups(data: dict) -> dict:
    return data.get("groups", {})


def get_ungrouped(data: dict) -> list:
    return data.get("ungrouped", [])