from email.message import EmailMessage

from shared.ui import screen, widgets


def display_address_book(groups: dict, ungrouped: list) -> None:
    print("Address book:")
    if groups:
        for name, members in groups.items():
            print(f"  [{name}] - {len(members)} member(s)")
            for member in members:
                print(f"    - {member}")
    else:
        print("  (no groups)")

    if ungrouped:
        print("\n  Ungrouped:")
        for addr in ungrouped:
            print(f"    - {addr}")
    else:
        print("  (no ungrouped recipients)")

    screen.divider()


def display_details(em: EmailMessage) -> None:
    widgets.banner("EMAIL DETAILS", clear=True)
    widgets.blank()
    widgets.label_block(
        ["Subject:", "From:", "To:", "Cc:", "Bcc:"],
        [
            str(em.get("Subject")),
            str(em.get("From")),
            str(em.get("To")),
            str(em.get("Cc")),
            str(em.get("Bcc")),
        ],
    )
    screen.divider()