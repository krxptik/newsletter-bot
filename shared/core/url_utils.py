import validators


def normalise_url(url: str) -> str:
    url = url.strip()
    if not url.startswith(("http://", "https://")):
        url = "https://" + url
    return url


def is_valid_url_format(url: str) -> bool:
    """Check URL syntax only — no network request."""
    return True if validators.url(url) == True else False


def normalise_path(path: str) -> str:
    """Strip trailing slash so '/foo/' and '/foo' match the same blocklist
    entry. Must be applied identically here and at mark_as_junk's write
    path, or entries silently become no-ops."""
    return path.rstrip("/") or "/"