import os
from pydantic_settings import BaseSettings, SettingsConfigDict

dir_path = os.path.dirname(os.path.realpath(__file__))

class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=os.path.join(dir_path, "./.env"),
        env_file_encoding="utf-8"
    )

    #Telegram
    TELEGRAM_API_ID: str
    TELEGRAM_API_HASH: str
    TELEGRAM_PHONE: str
    TELEGRAM_USERNAME: str

    #APIS
    NEWSDATAIO_KEY: str
    NEWSAPI_KEY: str
    NEWS_TOPIC: str

    # MongoDB
    MONGO_DATABASE_HOST: str = "mongodb://mongo1:30001,mongo2:30002,mongo3:30003/?replicaSet=my-replica-set"
    MONGO_DATABASE_NAME: str = "crypto-articles"

settings = Settings()

if __name__ == "__main__":
    print(os.path.join(dir_path, ".env"))
    print(settings.NEWS_TOPIC)
