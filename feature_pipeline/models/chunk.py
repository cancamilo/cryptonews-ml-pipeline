from typing import Optional
from models.base import DataModel

class ArticleChunkModel(DataModel):
    entry_id: str
    chunk_id: str
    title: str
    chunk_content: str
    published_at: Optional[str] = None
    type: str