from datetime import datetime, timedelta

class Article:
    def __init__(self, title, link, pub_date, text=None, summary=None, tags=None, source=None):
        self.title = title
        self.link = link
        self.pub_date = pub_date
        self.text = text
        self.summary = summary
        self.tags = tags
        self.source = source

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
        else:
            return True