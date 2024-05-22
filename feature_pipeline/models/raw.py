from typing import Optional

from models.base import DataModel

class ArticleRawModel(DataModel):
    entry_id: str
    source: str
    title: str
    content: str
    summary: Optional[str] = None
    
    class Settings:
        name = "articles"