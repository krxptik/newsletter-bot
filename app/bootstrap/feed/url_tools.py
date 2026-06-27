import re
import validators
from urllib.parse import urlparse


# ===== URL PARSING =====

def _split_url(url: str) -> tuple[str, list[str]]:
    parsed = urlparse(url)
    parts = parsed.path.strip("/").split("/")
    return parsed.netloc, parts


def regexify(url1: str, url2: str) -> str | None:
    dom1, par1 = _split_url(url1)
    dom2, par2 = _split_url(url2)

    if dom1 != dom2 or len(par1) != len(par2):
        return None

    regex_parts = []

    for p1, p2 in zip(par1, par2):
        if p1 == p2:
            regex_parts.append(re.escape(p1))
        elif p1.isdigit() and p2.isdigit() and len(p1) == len(p2):
            regex_parts.append(rf"\d{{{len(p1)}}}")
        else:
            regex_parts.append(r"[^\/]+")

    return rf"^https://{re.escape(dom1)}/{'/'.join(regex_parts)}$"


# ===== URL NORMALISATION =====

def normalise_url(url: str) -> str:
    url = url.strip()
    if not url.startswith(("http://", "https://")):
        url = "https://" + url
    return url


def is_valid_url(url: str) -> bool:
    try:
        return bool(validators.url(url))
    except Exception:
        return False