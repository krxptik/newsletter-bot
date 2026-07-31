import threading
from urllib.parse import urlparse

from ._constants import PER_DOMAIN_CONCURRENCY

_semaphores: dict[str, threading.Semaphore] = {}
_registry_lock = threading.Lock()


def domain_semaphore(url: str) -> threading.Semaphore:
    """Return the shared Semaphore for url's domain, creating it on first use."""
    domain = urlparse(url).netloc
    with _registry_lock:
        sem = _semaphores.get(domain)
        if sem is None:
            sem = threading.Semaphore(PER_DOMAIN_CONCURRENCY)
            _semaphores[domain] = sem
        return sem