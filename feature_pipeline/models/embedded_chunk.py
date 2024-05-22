from typing import Tuple
import numpy as np
from models.base import VectorDBDataModel


class ArticleEmbeddedChunkModel(VectorDBDataModel):
    entry_id: str
    title: str
    chunk_id: str
    chunk_content: str
    published_at: str
    embedded_content: np.ndarray
    type: str

    class Config:
        arbitrary_types_allowed = True

    def to_payload(self) -> Tuple[str, np.ndarray, dict]:
        data = {
            "id": self.entry_id,
            "title": self.title,
            "published_at": self.published_at,
            "content": self.chunk_content,
            "type": self.type,
        }

        return self.chunk_id, self.embedded_content, data
