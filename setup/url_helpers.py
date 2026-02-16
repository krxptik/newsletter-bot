from urllib.parse import urlparse
import re

def split_url(url):
    parsed = urlparse(url)
    parts = parsed.path.strip('/').split('/')
    return parsed.netloc, parts

def regexify(url1, url2):
    dom1, par1 = split_url(url1)
    dom2, par2 = split_url(url2)

    if dom1 != dom2:
        return
    
    regex_parts = []

    for p1, p2 in zip(par1, par2):
        if p1 == p2:
            regex_parts.append(re.escape(p1))
        elif p1.isdigit() and p2.isdigit() and len(p1) == len(p2):
            regex_parts.append(r"\d{"
                               + rf"{len(p1)}"
                               + r"}+")
        else:
            regex_parts.append(r"[^\/]+")

    return rf"^https://{re.escape(dom1)}/{'/'.join(regex_parts)}$"