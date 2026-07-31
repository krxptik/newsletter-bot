from typing import TYPE_CHECKING

from ._draft import EmailDraft
from shared.ui import screen, widgets

if TYPE_CHECKING:
    from ._recipient import RecipientType

def display_details(draft: EmailDraft) -> None:
    screen.clear()
    widgets.section_header("EMAIL DETAILS")
    widgets.blank()
    widgets.label_block(
        ["Subject:", "From:", "To:", "Cc:", "Bcc:"],
        [draft.subject, draft.from_, ", ".join(draft.to), ", ".join(draft.cc), ", ".join(draft.bcc)]
    )
    widgets.blank()
    screen.divider()


def display_recipient_detail(draft: EmailDraft, recipient_type: RecipientType) -> None:
    labels = [f"{recipient_type.value.title()}:"]
    values = [", ".join(getattr(draft, recipient_type.value))]
    screen.clear()
    widgets.section_header(f"MANAGING '{recipient_type.value.title()}'")
    widgets.blank()
    widgets.label_block(labels, values if values[0] else ["No recipients set."])
    widgets.blank()
    screen.divider()