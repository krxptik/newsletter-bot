from dataclasses import dataclass

@dataclass
class Feed:
    name: str
    site_url: str | None
    feed_url: str | None

    @classmethod
    def from_dict(cls, data: dict) -> "Feed":
        # --- Oldest format: type = "RSS" | "NON-RSS", optional scrape_content ---
        if "type" in data:
            is_non_rss = data["type"] == "NON-RSS"
            return cls(
                name=data["name"],
                site_url=data["url"] if is_non_rss else None,
                feed_url=None if is_non_rss else data["url"],
            )

        # --- Middle format: metadata_retrieval / content_retrieval ---
        if "metadata_retrieval" in data:
            is_scraped = data["metadata_retrieval"] == "scrape"
            return cls(
                name=data["name"],
                site_url=data["url"] if is_scraped else None,
                feed_url=None if is_scraped else data["url"],
            )

        # --- Current format ---
        return cls(
            name=data["name"],
            site_url=data.get("site_url"),
            feed_url=data.get("feed_url"),
        )

    def to_dict(self) -> dict:
        return {"name": self.name, "site_url": self.site_url, "feed_url": self.feed_url}