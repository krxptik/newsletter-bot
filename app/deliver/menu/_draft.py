from email.message import EmailMessage

from shared.core import is_valid_email
from shared.prompts import ask
from shared.ui import widgets
from models import AddressBook


class EmailDraft:
    def __init__(
        self,
        subject: str | None = None,
        from_: str | None = None,
        address_book: AddressBook | None = None,
    ):
        self.em = EmailMessage()
        self.address_book = address_book
        self._to = SyncedRecipientList(self, "To")
        self._cc = SyncedRecipientList(self, "Cc")
        self._bcc = SyncedRecipientList(self, "Bcc")

        if subject:
            self.subject = subject
        if from_:
            self.from_ = from_

    @property
    def to(self):
        return self._to

    @property
    def cc(self):
        return self._cc

    @property
    def bcc(self):
        return self._bcc

    @property
    def to_addrs(self) -> set[str]:
        resolved: set[str] = set()
        for entry in list(self.to) + list(self.cc) + list(self.bcc):
            if not entry:
                continue
            if is_valid_email(entry):
                resolved.add(entry)
                continue

            if self.address_book is None:
                resolved.add(entry)
                continue

            group = self.address_book.get_group_by_name(entry)
            if group is not None:
                resolved.update(group.members)
            else:
                resolved.add(entry)

        return resolved

    @property
    def subject(self):
        return self.em.get("Subject", "")

    @subject.setter
    def subject(self, value: str):
        self._set_header("Subject", value)

    @property
    def from_(self):
        return self.em.get("From", "")

    @from_.setter
    def from_(self, value: str):
        self._set_header("From", value)

    def _set_header(self, header, value):
        if not value:
            if header in self.em:
                del self.em[header]
            return

        try:
            self.em.replace_header(header, value)
        except KeyError:
            self.em[header] = value

    def set_text(self, text: str):
        self.em.set_content(text)

    def set_html(self, html: str):
        self.em.add_alternative(html, subtype="html")

    def is_recipients_empty(self) -> bool:
        return len(self.to_addrs) == 0

    def edit_subject(self) -> None:
        new = ask("New subject:", cancel_word="back")
        if new is None:
            return
        if not new:
            widgets.notify("ERROR: Empty subject.")
            return
        self.subject = new

    
class SyncedRecipientList(list):
    def __init__(self, owner: EmailDraft, header_name: str, values=None):
        super().__init__(values or [])
        self._owner = owner
        self._header_name = header_name

    def _sync(self) -> None:
        if self:
            value = ", ".join(self)
            if self._header_name in self._owner.em:
                self._owner.em.replace_header(self._header_name, value)
            else:
                self._owner.em[self._header_name] = value
        else:
            if self._header_name in self._owner.em:
                del self._owner.em[self._header_name]

    def append(self, value: str):
        super().append(value)
        self._sync()

    def remove(self, value: str):
        super().remove(value)
        self._sync()