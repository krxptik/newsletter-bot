import validators


def normalise_url(url: str) -> str:
    url = url.strip()
    if not url.startswith(("http://", "https://")):
        url = "https://" + url
    return url


def is_valid_url_format(url: str) -> bool:
    """Check URL syntax only — no network request."""
    return True if validators.url(url) == True else False