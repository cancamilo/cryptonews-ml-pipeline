from typing import Optional, Tuple

from models.base import VectorDBDataModel


class ArticleCleanedModel(VectorDBDataModel):
    entry_id: str
    source: str
    title: str
    cleaned_content: str
    summary: Optional[str] = None
    type: str = "article"

    def to_payload(self) -> Tuple[str, dict]:
        data = {
            "source": self.source,
            "title": self.title,
            "cleaned_content": self.cleaned_content,
            "type": self.type,
        }

        return self.entry_id, data
