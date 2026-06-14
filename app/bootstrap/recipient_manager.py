import logging

from shared.terminal import clear_terminal, display_banner, divider
from app.persistence.email_addrs_store import load_address_book, save_address_book, get_groups, get_ungrouped

logger = logging.getLogger(__name__)


# ===== DISPLAY =====

def _display_address_book(data: dict, title: str) -> None:
    clear_terminal()
    display_banner(title)

    groups = get_groups(data)
    ungrouped = get_ungrouped(data)

    print("\nGroups:")
    if groups:
        for name, members in groups.items():
            print(f"  [{name}] — {len(members)} members")
            for m in members:
                print(f"    - {m}")
    else:
        print("  (none)")

    print("\nUngrouped recipients:")
    if ungrouped:
        for addr in ungrouped:
            print(f"  - {addr}")
    else:
        print("  (none)")

    divider(single=True, spacing=True)
    print("Options:")
    print("  (1) Add group")
    print("  (2) Remove group")
    print("  (3) Add ungrouped recipient")
    print("  (4) Remove ungrouped recipient")
    print("  (5) Done")


# ===== HANDLERS =====

def _add_group(data: dict) -> None:
    name = input("Group name: ").strip().upper()
    if not name:
        return
    if name in data["groups"]:
        print(f"Group '{name}' already exists.")
        return

    emails_input = input("Enter emails separated by commas: ").strip()
    emails = [e.strip() for e in emails_input.split(",") if e.strip()]

    if not emails:
        print("No emails entered, group not created.")
        return

    data["groups"][name] = emails
    save_address_book(data)
    logger.info(f"Added group '{name}' with {len(emails)} member(s)")
    print(f"Group '{name}' added.")


def _remove_group(data: dict) -> None:
    name = input("Group name to remove: ").strip().upper()
    if name in data["groups"]:
        del data["groups"][name]
        save_address_book(data)
        logger.info(f"Removed group '{name}'")
        print(f"Group '{name}' removed.")
    else:
        print(f"Group '{name}' not found.")


def _add_ungrouped(data: dict) -> None:
    email = input("Email to add: ").strip()
    if not email:
        return
    if email in data["ungrouped"]:
        print(f"'{email}' already in ungrouped.")
        return
    data["ungrouped"].append(email)
    save_address_book(data)
    logger.info(f"Added ungrouped recipient '{email}'")
    print(f"'{email}' added.")


def _remove_ungrouped(data: dict) -> None:
    email = input("Email to remove: ").strip()
    if email in data["ungrouped"]:
        data["ungrouped"].remove(email)
        save_address_book(data)
        logger.info(f"Removed ungrouped recipient '{email}'")
        print(f"'{email}' removed.")
    else:
        print(f"'{email}' not found in ungrouped.")


# ===== ENTRY POINT =====

def run_recipient_manager(title: str = "ADDRESS BOOK") -> None:
    logger.info(f"Running recipient manager (title='{title}')")
    data = load_address_book()

    while True:
        _display_address_book(data, title)
        user_input = input("\n> ").strip()

        if not user_input.isdigit():
            continue

        option = int(user_input)

        if option == 1:
            _add_group(data)
        elif option == 2:
            _remove_group(data)
        elif option == 3:
            _add_ungrouped(data)
        elif option == 4:
            _remove_ungrouped(data)
        elif option == 5:
            logger.info("Recipient manager exited")
            break