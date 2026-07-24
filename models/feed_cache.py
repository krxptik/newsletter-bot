from dataclasses import dataclass
from datetime import datetime

@dataclass
class FeedCache:
    name: str
    trust_feed_url: bool = True
    consecutive_failures: int = 0
    last_parsed_at: str | None = None

    @classmethod
    def from_dict(cls, data: dict) -> "FeedCache":
        return cls(
            name=data["name"],
            trust_feed_url=data.get("trust_feed_url", True),
            consecutive_failures=data.get("consecutive_failures", 0),
            last_parsed_at=data.get("last_parsed_at"),
        )

    def mark_parsed(self, success: bool) -> None:
        self.last_parsed_at = datetime.now().isoformat()
        self.consecutive_failures = 0 if success else self.consecutive_failures + 1