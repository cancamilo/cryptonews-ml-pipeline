from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    # MongoDB
    MONGO_DATABASE_HOST: str = "mongodb://localhost:30001,localhost:30002/?replicaSet=my-replica-set"
    MONGO_DATABASE_NAME: str = "crypto-articles"

settings = Settings()
