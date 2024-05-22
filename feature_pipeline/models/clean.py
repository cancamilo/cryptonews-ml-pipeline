from typing import Optional, Tuple

from models.base import VectorDBDataModel


class ArticleCleanedModel(VectorDBDataModel):
    entry_id: str
    source: str
    title: str
    cleaned_content: str
    summary: Optional[str] = None
    published_at: Optional[str] = None
    type: str = "article"

    def to_payload(self) -> Tuple[str, dict]:
        data = {
            "source": self.source,
            "title": self.title,
            "summary": self.summary,
            "published_at": self.published_at,
            "cleaned_content": self.cleaned_content,
            "type": self.type,
        }

        return self.entry_id, data
