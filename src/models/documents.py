import uuid
from datetime import datetime
from dateutil import parser
from typing import List, Optional

from aws_lambda_powertools import Logger
from config import settings
from db.mongodb import connection
from errors import ImproperlyConfigured
from pydantic import UUID4, BaseModel, ConfigDict, Field, field_validator
from pymongo import errors

logger = Logger(service="text-fetch-etl/crawler")
_database = connection.get_database(settings.MONGO_DATABASE_NAME)


class BaseDocument(BaseModel):
    id: UUID4 = Field(default_factory=uuid.uuid4)
    published_at: str = Field(
        default_factory=lambda: datetime.now().strftime("%Y-%m-%d")
    )

    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    @field_validator("published_at")
    def clean_date_field(cls, v):
        try:
            parsed_date = parser.parse(v)
            return parsed_date.strftime("%Y-%m-%d")
        except (ValueError, TypeError):
            logger.error(f"Error parsing date: {v}, using current date instead.")

    @classmethod
    def from_mongo(cls, data: dict):
        """Convert "_id" (str object) into "id" (UUID object)."""
        if not data:
            return data

        id = data.pop("_id", None)
        return cls(**dict(data, id=id))

    def to_mongo(self, **kwargs) -> dict:
        """Convert "id" (UUID object) into "_id" (str object)."""
        exclude_unset = kwargs.pop("exclude_unset", False)
        by_alias = kwargs.pop("by_alias", True)

        parsed = self.model_dump(
            exclude_unset=exclude_unset, by_alias=by_alias, **kwargs
        )

        if "_id" not in parsed and "id" in parsed:
            parsed["_id"] = str(parsed.pop("id"))

        return parsed

    def save(self, **kwargs):
        collection = _database[self._get_collection_name()]
        try:
            result = collection.insert_one(self.to_mongo(**kwargs))
            return result.inserted_id
        except errors.WriteError as e:
            logger.error(f"Failed to insert document {e}")
            return None

    @classmethod
    def get_or_create(cls, **filter_options) -> Optional[str]:
        collection = _database[cls._get_collection_name()]
        try:
            instance = collection.find_one(filter_options)
            if instance:
                return str(cls.from_mongo(instance).id)
            new_instance = cls(**filter_options)
            new_instance = new_instance.save()
            return new_instance
        except errors.OperationFailure as e:
            logger.error(f"Failed to retrieve document: {e}")
            return None

    @classmethod
    def bulk_insert(cls, documents: List, **kwargs) -> Optional[List[str]]:
        collection = _database[cls._get_collection_name()]
        try:
            result = collection.insert_many(
                [doc.to_mongo(**kwargs) for doc in documents]
            )
            return result.inserted_ids
        except errors.WriteError as e:
            logger.error(f"Failed to insert document {e}")
            return None

    @classmethod
    def _get_collection_name(cls):
        if not hasattr(cls, "Settings") or not hasattr(cls.Settings, "name"):
            raise ImproperlyConfigured(
                "Document should define an Settings configuration class with the name of the collection."
            )

        return cls.Settings.name
    
    @classmethod
    def close_connection(cls):
        connection.close()
    
    @classmethod
    def dump_json(cls, articles) -> None:
        with open("articles.txt", "w") as file:
            for article in articles:
                file.write(str(article.model_dump()) + "\n")

class ArticleDocument(BaseDocument):
    source: str
    title: str
    content: str
    summary: Optional[str] = None
    
    class Settings:
        name = "articles"