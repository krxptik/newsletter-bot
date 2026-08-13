import logging
from urllib.parse import urlparse
from typing import cast

from .data_manager import load_file_data, overwrite_file_data
from shared.core import normalise_path
from path_config import CONFIG_DIR

logger = logging.getLogger(__name__)

DOMAIN_BLOCKLIST_FILE = CONFIG_DIR / "domain_blocklist.json"


def load_domain_blocklist(path=DOMAIN_BLOCKLIST_FILE) -> dict[str, list[str]]:
    logger.debug("Loading domain blocklist from %s", path)
    blocklist = load_file_data(path, default={})
    logger.debug("Loaded %d domain blocklist entries", len(blocklist))
    return cast(dict[str, list[str]], blocklist)


def save_domain_blocklist(blocklist: dict, path=DOMAIN_BLOCKLIST_FILE) -> None:
    logger.debug("Saving domain blocklist to %s", path)
    overwrite_file_data(blocklist, path)
    logger.debug("Domain blocklist saved")


def add_to_blocklist(link: str):
    logger.debug("Adding link to blocklist: %s", link)
    blocklist = load_domain_blocklist()

    parsed = urlparse(link)
    domain = parsed.hostname.removeprefix("www.") if parsed.hostname else None
    path = normalise_path(parsed.path or "/")

    if not domain:
        logger.warning("Skipping blocklist update for invalid link: %s", link)
        return

    logger.debug("Parsed link into domain=%s path=%s", domain, path)

    domain_list = list(blocklist.get(domain, []))
    if path not in domain_list:
        domain_list.append(path)
        blocklist[domain] = domain_list
        logger.info("Added path '%s' to blocklist for domain '%s'", path, domain)
    else:
        logger.debug("Path '%s' already exists for domain '%s'", path, domain)

    save_domain_blocklist(blocklist)
    logger.debug("Blocklist persisted for %s with %d entries", domain, len(domain_list))