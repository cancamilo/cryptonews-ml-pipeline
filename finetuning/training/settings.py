import os
from pydantic_settings import BaseSettings, SettingsConfigDict
from pathlib import Path

dir_path = os.path.dirname(os.path.realpath(__file__))

class AppSettings(BaseSettings):
    # model_config = SettingsConfigDict(
    #     env_file=os.path.join(dir_path, "./.env"),
    #     env_file_encoding="utf-8"
    # )

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    OPENAI_MODEL_ID: str = "gpt-4-1106-preview"
    OPENAI_API_KEY: str = ""

    # QdrantDB config
    USE_QDRANT_CLOUD: bool = False
    QDRANT_DATABASE_HOST: str = "localhost"
    QDRANT_DATABASE_PORT: int = 6333
    QDRANT_DATABASE_URL: str = "http://localhost:6333"
    QDRANT_APIKEY: str = ""

    TOKENIZERS_PARALLELISM: str = "false"
    HUGGINGFACE_ACCESS_TOKEN: str

    # COMET SETTINGS
    COMET_API_KEY: str = ""
    COMET_PROJECT: str = "crypto-reporter"
    COMET_WORKSPACE: str = "cancamilo"

    
    DATASET_ARTIFACT_NAME: str = "cleaned_articles"
    LLM_MODEL_TYPE: str = "cancamilo/reporter-v0.1"
    CONFIG_FILE: str = "./training/config.yaml"
    MODEL_SAVE_DIR: str = "./training_pipeline_output"
    CACHE_DIR: Path = Path("./.cache")

    QUARK_API_KEY: str = ""



settings = AppSettings()
