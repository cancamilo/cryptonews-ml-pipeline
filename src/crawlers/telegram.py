import os
import re
import logging
from telethon.sync import TelegramClient
from typing import Dict, List
from models.documents import ArticleDocument
from config import settings
from datetime import datetime

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


class TelegramChannelsCrawler:

    date_format="%Y-%m-%d"
    dir_path = os.path.dirname(os.path.realpath(__file__))
    session_path = os.path.join(dir_path, "..", "session_data")
    chats = [
        {"id": "@socryptoland", "n_messages": 1000},  # good for short news
        {"id": "@crypto_fight", "n_messages": 1000},  # good for short news
        {"id": "@crypto_lake", "n_messages": 1000},  # good for short news
        {"id": "@tokens_stream", "n_messages": 1000},  # good for short news
        {"id": "@maptoken", "n_messages": 1000},  # good for short news
        {"id": "@getcoinit", "n_messages": 1000},  # good for short news
        {
            "id": "@cointelegraph",
            "n_messages": 10000,
        },  # really good and a lot of data. only headlines and short descriptions available and needs cleaning.
    ]

    
    def __extract_first_sentence(self, paragraph):
        try:
            sentences = re.split('[.!?]|[\r\n]', paragraph if paragraph != None else "")
            return sentences[0]
        except Exception as e:
            logger.error(f"An error ocurred parsing the text data: {str(e)}")
            return ""
    
    async def extract_day(self, date: str = datetime.now().strftime(date_format), channel_count=100, loop=None):
        channel_count = 100
        messages = []
        self.loop = loop
        self.client = TelegramClient(
            f"{self.session_path}/my_user",
            settings.TELEGRAM_API_ID,
            settings.TELEGRAM_API_HASH,
            loop=loop,
        )
        await self.client.connect()
        logger.info("Telegram client connected")
        async with self.client:
            # Ensure you're authorized
            if not await self.client.is_user_authorized():
                raise Exception("Client not auhtorized")

            for input_channel in self.chats:
                async for msg in self.client.iter_messages(
                    input_channel["id"], 
                    limit=channel_count,
                    offset_date=datetime.strptime(date, self.date_format).date(),
                    reverse=True
                ):
                    if msg.message is not None:
                        messages.append(
                            ArticleDocument(
                                source="telegram",
                                published_at=msg.date.strftime("%Y-%m-%d"),
                                title=self.__extract_first_sentence(msg.message),
                                content=msg.message,
                            )
                        )

            return messages
    
    async def extract(self, channel_count=100, loop = None) -> List[Dict]:
        messages = []
        self.loop = loop
        self.client = TelegramClient(
            f"{self.session_path}/my_user",
            settings.TELEGRAM_API_ID,
            settings.TELEGRAM_API_HASH,
            loop=loop,
        )
        await self.client.connect()
        logger.info("Telegram client connected")
        async with self.client:
            # Ensure you're authorized
            if not await self.client.is_user_authorized():
                raise Exception("Client not auhtorized")

            for input_channel in self.chats:
                async for msg in self.client.iter_messages(
                    input_channel["id"], limit=channel_count
                ):
                    if msg.message is not None:
                        messages.append(
                            ArticleDocument(
                                source="telegram",
                                published_at=msg.date.strftime("%Y-%m-%d"),
                                title=self.__extract_first_sentence(msg.message),
                                content=msg.message,
                            )
                        )

            return messages




