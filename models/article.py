from datetime import datetime, timedelta

class Article:
    def __init__(self, title, link, pub_date, text=None, summary=None, tags=None):
        self.title = title
        self.link = link
        self.pub_date = pub_date
        self.text = text
        self.summary = summary
        self.tags = tags

    def is_recent(self, days=14):
        if self.pub_date:
            return self.pub_date > datetime.now() - timedelta(days=days)
        else:
            return True