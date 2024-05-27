from typing import Optional
from datetime import datetime
from models.base import DataModel

class ArticleRawModel(DataModel):
    entry_id: str
    source: str
    title: str
    content: str
    summary: Optional[str] = None
    published_at: Optional[str] = datetime.now().strftime(format="%Y-%m-%d")
    
    class Settings:
        name = "articles"