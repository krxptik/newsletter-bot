from dataclasses import dataclass

@dataclass
class Feed:
    url: str
    name: str
    metadata_retrieval: str   # "collect" | "scrape"
    content_retrieval: str    # "collect" | "scrape"

    @classmethod
    def from_dict(cls, data: dict) -> "Feed":
        # --- Migration: old format ---
        if "type" in data:
            is_non_rss = data["type"] == "NON-RSS"
            return cls(
                url=data["url"],
                name=data["name"],
                metadata_retrieval="scrape" if is_non_rss else "collect",
                content_retrieval="scrape" if (is_non_rss or data.get("scrape_content", False)) else "collect",
            )

        # --- Current format ---
        return cls(
            url=data["url"],
            name=data["name"],
            metadata_retrieval=data["metadata_retrieval"],
            content_retrieval=data["content_retrieval"],
        )