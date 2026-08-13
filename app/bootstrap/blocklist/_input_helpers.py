from shared.prompts import ask
from shared.ui import widgets


def prompt_domain(blocklist: dict[str, list[str]], prompt: str = "Domain number or name:") -> str | None:
    domains = sorted(blocklist.keys())
    raw = ask(prompt, cancel_word="back")
    if not raw:
        return None

    if raw.isdigit():
        idx = int(raw) - 1
        result = domains[idx] if 0 <= idx < len(domains) else None
    else:
        result = raw if raw in blocklist else None

    if result is None:
        widgets.notify(f"ERROR: Domain not found: '{raw}'.")

    return result