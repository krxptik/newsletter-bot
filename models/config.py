from dataclasses import dataclass


@dataclass
class Config:
    ai_ready: bool = False
    sender_ready: bool = False
    feeds_ready: bool = False
    recipients_ready: bool = False

    def is_complete(self) -> bool:
        return self.ai_ready and self.sender_ready and self.feeds_ready and self.recipients_ready

    def display_data(self) -> list[tuple[str, str]]:
        def _ready(value: bool) -> str:
            return "Ready" if value else "Not ready"
        return [
            ("AI:", _ready(self.ai_ready)),
            ("Sender:", _ready(self.sender_ready)),
            ("Feeds:", _ready(self.feeds_ready)),
            ("Recipients:", _ready(self.recipients_ready))
        ]