import threading

import requests

_local = threading.local()


def get_session() -> requests.Session:
    """Return a Session unique to the calling thread. One Session per
    worker thread, reused across tasks — never shared across threads."""
    if not hasattr(_local, "session"):
        _local.session = requests.Session()
    return _local.session