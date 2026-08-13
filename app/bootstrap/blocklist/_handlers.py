import logging

from ._input_helpers import prompt_domain
from ._blocklist import view_domain_blocklist

from app.persistence import save_domain_blocklist
from shared.ui import widgets
from shared.prompts import ask, confirmation

logger = logging.getLogger(__name__)


def remove_domain(blocklist: dict[str, list[str]]) -> None:
    domain = prompt_domain(blocklist, "Domain number or name to remove:")
    if domain is None:
        return

    if not confirmation(f"Remove all blocked paths for '{domain}'?"):
        widgets.notify("Cancelled.")
        return

    del blocklist[domain]
    _persist(blocklist)
    logger.info(f"Removed all blocklist entries for '{domain}'")
    widgets.notify(f"All blocked paths removed for '{domain}'.")


def remove_path(blocklist: dict[str, list[str]]) -> None:
    domain = prompt_domain(blocklist, "Domain number or name:")
    if domain is None:
        return

    path = ask("Path to remove (exact):", cancel_word="back")
    if path is None:
        return

    if path not in blocklist[domain]:
        widgets.notify(f"ERROR: '{path}' not found under '{domain}'.")
        return

    if not confirmation(f"Remove '{path}' from '{domain}'?"):
        widgets.notify("Cancelled.")
        return

    blocklist[domain].remove(path)
    if not blocklist[domain]:
        del blocklist[domain]

    _persist(blocklist)
    logger.info(f"Removed blocklist path '{path}' for '{domain}'")
    widgets.notify(f"Removed '{path}'.")


def handle_view_blocklist(blocklist: dict[str, list[str]]) -> None:
    domain = prompt_domain(blocklist, "Domain number or name to view:")
    if domain is None:
        return

    view_domain_blocklist(domain, blocklist[domain])


def _persist(blocklist: dict[str, list[str]]) -> None:
    save_domain_blocklist(blocklist)