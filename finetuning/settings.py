import os
from pydantic_settings import BaseSettings, SettingsConfigDict

dir_path = os.path.dirname(os.path.realpath(__file__))

class AppSettings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=os.path.join(dir_path, "./.env"),
        env_file_encoding="utf-8"
    )

    OPENAI_MODEL_ID: str = "gpt-4-1106-preview"
    OPENAI_API_KEY: str = ""

    # QdrantDB config
    USE_QDRANT_CLOUD: bool = False
    QDRANT_DATABASE_HOST: str = "localhost"
    QDRANT_DATABASE_PORT: int = 6333
    QDRANT_DATABASE_URL: str = "http://localhost:6333"
    QDRANT_APIKEY: str | None = None


    # COMET SETTINGS
    COMET_API_KEY: str
    COMET_PROJECT: str = "crypto-reporter"
    COMET_WORKSPACE: str = "cancamilo"



settings = AppSettings()
