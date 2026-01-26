from datetime import datetime, timedelta
import html

class Article:
    def __init__(self, title, link, pub_date, text=None, summary=None, tags=None, source=None):
        self.title = title
        self.link = link
        self.pub_date = pub_date
        self.text = text
        self.summary = summary
        self.tags = tags
        self.source = source

    # ---- title ----
    @property
    def title(self):
        return self._title

    @title.setter
    def title(self, value):
        self._title = html.unescape(value) if value else value

    # ---- text ----
    @property
    def text(self):
        return self._text

    @text.setter
    def text(self, value):
        self._text = html.unescape(value) if value else value

    # ---- summary ----
    @property
    def summary(self):
        return self._summary

    @summary.setter
    def summary(self, value):
        self._summary = html.unescape(value) if value else value

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
