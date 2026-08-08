from models import AddressBook, Group
from shared.ui import widgets
from shared.prompts import ask


def prompt_group(book: AddressBook, prompt: str = "Group number or name:") -> Group | None:
    raw = ask(prompt, cancel_word="back")
    result = None
    if not raw:
        return None
    elif raw.isdigit():
        idx = int(raw) - 1
        result = book.get_group_by_index(idx)
    else:
        result = book.get_group_by_name(raw)
    
    if result is None:
        widgets.notify(f"ERROR: Group not found: '{raw}'.")

    return result