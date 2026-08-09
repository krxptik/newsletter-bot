import logging
from typing import cast

from .data_manager import load_file_data, overwrite_file_data
from path_config import CONFIG_DIR

logger = logging.getLogger(__name__)

DOMAIN_BLOCKLIST_FILE = CONFIG_DIR / "domain_blocklist.json"


def load_domain_blocklist(path=DOMAIN_BLOCKLIST_FILE) -> dict[str, list[str]]:
    logger.debug(f"Loading domain blocklist from {path}")
    blocklist = load_file_data(path, default={})
    logger.debug(f"Loaded {len(blocklist)} used URLs")
    return cast(dict[str, list[str]], blocklist)


def save_domain_blocklist(blocklist: dict, path=DOMAIN_BLOCKLIST_FILE) -> None:
    logger.debug(f"Saving domain blocklist to {path}")
    overwrite_file_data(blocklist, path)
    logger.debug("Domain blocklist saved")