import logging
from typing import Any, cast

from path_config import CONFIG_DIR
from .data_manager import load_file_data, overwrite_file_data

logger = logging.getLogger(__name__)

ADDRESS_BOOK_FILE = CONFIG_DIR / "address_book.json"


def load_address_book() -> dict[str, Any]:
    logger.debug(f"Loading address book from {ADDRESS_BOOK_FILE}")
    data = load_file_data(ADDRESS_BOOK_FILE, default={"groups": {}, "ungrouped": []})
    address_book = cast(dict[str, Any], data)
    logger.debug(
        f"Loaded {len(address_book.get('groups', {}))} group(s), "
        f"{len(address_book.get('ungrouped', []))} ungrouped recipient(s)"
    )
    return address_book


def save_address_book(data: dict) -> None:
    logger.debug(f"Saving address book to {ADDRESS_BOOK_FILE}")
    overwrite_file_data(data, ADDRESS_BOOK_FILE)
    logger.debug("Address book saved")