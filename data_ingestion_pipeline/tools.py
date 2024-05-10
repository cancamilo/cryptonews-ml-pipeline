import os
import datetime
import functools
import logging
from typing import Callable, Dict, List
from telethon.sync import TelegramClient

from newsapi import NewsApiClient
from newsdataapi import NewsDataApiClient
from pydantic import ValidationError

from data_ingestion_pipeline.models.article_models import NewsAPIModel, NewsDataIOModel, TelegramMessage
from settings import settings

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


def handle_article_fetching(func: Callable) -> Callable:
    """
    Decorator to handle exceptions for article fetching functions.

    This decorator wraps article fetching functions to catch and log any exceptions
    that occur during the fetching process. If an error occurs, it logs the error
    and returns an empty list.

    Args:
        func (Callable): The article fetching function to wrap.

    Returns:
        Callable: The wrapped function.
    """

    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except ValidationError as e:
            logger.error(f"Validation error while processing articles: {e}")
        except Exception as e:
            logger.error(f"Error fetching data from source: {e}")
            logger.exception(e)
        return []

    return wrapper

def time_window(hours: int) -> str:
    """
    Generate the datetime pairs for the specified time window.
    Args:
        hours (int): The length of the time window in hours.

    Returns:
        Tuple[str, str]: A tuple containing the start and end times of the window in ISO format.

    Note:
        Batch fetching feature is available only with pro plan.

    """
    current_datetime = datetime.datetime.now()
    end_datetime = current_datetime + datetime.timedelta(hours=hours)
    return current_datetime.strftime("%Y-%m-%dT%H:%M:%S"), end_datetime.strftime(
        "%Y-%m-%dT%H:%M:%S"
    )

class NewsFetcher:
    """
    A class for fetching news articles from various APIs.

    Attributes:
        _newsapi (NewsApiClient): Client for the NewsAPI.
        _time_window_h (int): The time window for fetching articles, in hours.

    Methods:
        fetch_from_newsapi(): Fetches articles from NewsAPI.
        sources: Returns a list of callable fetch functions.
    """

    def __init__(self):
        self._newsapi = NewsApiClient(api_key=settings.NEWSAPI_KEY)
        self._time_window_h = 24  # Fetch news once a day

    @handle_article_fetching
    def fetch_from_newsapi(self) -> List[Dict]:
        """Fetch top headlines from NewsAPI."""
        response = self._newsapi.get_everything(
            q=settings.NEWS_TOPIC,
            language="en",
            page=settings.ARTICLES_BATCH_SIZE,
            page_size=settings.ARTICLES_BATCH_SIZE,
        )
        return [
            NewsAPIModel(**article).to_common()
            for article in response.get("articles", [])
        ]

    @handle_article_fetching
    def fetch_from_newsdataapi(self) -> List[Dict]:
        """Fetch news data from NewsDataAPI."""
        response = self._newsdataapi.news_api(
            q=settings.NEWS_TOPIC,
            language="en",
            size=settings.ARTICLES_BATCH_SIZE,
        )
        return [
            NewsDataIOModel(**article).to_common()
            for article in response.get("results", [])
        ]

    @property
    def sources(self) -> List[callable]:
        """List of news fetching functions."""
        return [self.fetch_from_newsapi, self.fetch_from_newsdataapi]
    
class TelegramChannelsFetcher:

    dir_path = os.path.dirname(os.path.realpath(__file__))
    session_path = os.path.join(dir_path, "session_data")

    chats = [
        {"id":"@socryptoland", "n_messages": 1000},  # good for short news
        {"id":"@crypto_fight", "n_messages": 1000}, # good for short news
        {"id":"@crypto_lake", "n_messages": 1000}, # good for short news
        {"id":"@tokens_stream", "n_messages": 1000}, # good for short news
        {"id":"@maptoken", "n_messages": 1000}, # good for short news
        {"id":"@getcoinit", "n_messages": 1000}, # good for short news
        {"id":"@cointelegraph", "n_messages": 10000}, # really good and a lot of data. only headlines and short descriptions available and needs cleaning.
    ]   
    
    async def fetch_news_from_telegram(self, loop) -> List[Dict]:
        messages = []
        self.loop = loop
        self.client = TelegramClient(f"{self.session_path}/my_user", settings.TELEGRAM_API_ID, settings.TELEGRAM_API_HASH, loop=loop)
        await self.client.connect()
        logger.info("Telegram client connected")
        async with self.client:
            # Ensure you're authorized
            if not await self.client.is_user_authorized():
                raise Exception("Client not auhtorized")
            
            for input_channel in self.chats:
                print("fetching data for ", input_channel["id"])
                async for msg in self.client.iter_messages(input_channel["id"], input_channel["n_messages"]):
                    print(msg.message[0:10])
                    messages.append(TelegramMessage(publishedAt=msg.date.strftime("%Y-%m-%dT%H:%M:%S"), content=msg.message).to_common())
            
            
            return messages
            

if __name__ == "__main__":
    import asyncio
    loop = asyncio.get_event_loop()
    tele = TelegramChannelsFetcher()
    loop.run_until_complete(tele.fetch_news_from_telegram(loop))
        

        
