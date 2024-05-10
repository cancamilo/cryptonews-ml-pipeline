import logging
import functools
from datetime import datetime
from config import settings
from typing import Callable, Dict, List
from pydantic import ValidationError
from newsapi import NewsApiClient
from models.documents import ArticleDocument

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
        self.page_size = 100
        self._newsapi = NewsApiClient(api_key=settings.NEWSAPI_KEY)
        self._time_window_h = 24  # Fetch news once a day

    @handle_article_fetching
    def extract(self, page, start_date, end_date) -> List[Dict]:
        """Fetch top headlines from NewsAPI."""
        response = self._newsapi.get_everything(
            q=settings.NEWS_TOPIC,
            language="en",
            page=page,
            page_size=self.page_size,
            from_param=start_date,
            to=end_date,
        )
        return [
            ArticleDocument(
                source="news_api",
                published_at=article["publishedAt"],
                title=article["title"],
                content=article["content"],
                summary=article["description"],
            )
            for article in response.get("articles", [])
        ]

    @property
    def sources(self) -> List[callable]:
        """List of news fetching functions."""
        return [self.extract]
