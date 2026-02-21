from datetime import datetime, timedelta
from typing import Optional, List
from dataclasses import dataclass
import html

@dataclass
class Article:
    title: str
    link: str
    pub_date: datetime
    text: Optional[str] = None
    source: Optional[str] = None
    summary: Optional[str] = None
    tags: Optional[List[str]] = None

    def __post_init__(self):
        # Unescape text
        self.title = html.unescape(self.title) if self.title else self.title
        self.text = html.unescape(self.text) if self.text else self.text
        self.summary = html.unescape(self.summary) if self.summary else self.summary

        # Validation
        if not self.title or not self.title.strip():
            raise ValueError("Title cannot be empty")
        if not self.link.startswith(('http://', 'https://')):
            raise ValueError(f"Invalid URL: {self.link}")

    def to_dict(self):
        return {
            "title": self.title,
            "summary": self.summary,
            "link": self.link,
            "source": self.source
        }

    def is_recent(self, days=14):
        if self.pub_date:
            return self.pub_date > datetime.now() - timedelta(days=days)
        return True
