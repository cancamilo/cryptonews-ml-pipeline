import json
import asyncio
from typing import Any
from aws_lambda_powertools import Logger
from aws_lambda_powertools.utilities.typing import LambdaContext
from datetime import datetime, timedelta
from models.documents import ArticleDocument
from crawlers import CoinTelegraphCrawler, TelegramChannelsCrawler, NewsFetcher

logger = Logger(service="text-etl-fetcher/crawler")
date_format="%Y-%m-%d"
coin_crawler = CoinTelegraphCrawler(dev=False)
telegram_crawler = TelegramChannelsCrawler()
news_api_crawler = NewsFetcher()

def backfill():
    try:
        start_dt = datetime.now() - timedelta(days=360)
        end_dt = datetime.now()
        ct_articles = coin_crawler.extract(
            n_scrolls=30, 
            start_date=start_dt.strftime(date_format),
            end_date=end_dt.strftime(date_format)
        )

        # Use event loop for telegram functions
        loop = asyncio.get_event_loop()
        telegram_messages = loop.run_until_complete(telegram_crawler.extract(channel_count=1000, loop=loop))

        # Extract maximum allowed articles from NewsAPI
        start_dt = datetime.now() - timedelta(days=10)
        end_dt = datetime.now()

        api_articles = news_api_crawler.extract(
            page=1,
            start_date=start_dt.strftime(date_format),
            end_date=end_dt.strftime(date_format)
        )

        merged_articles = ct_articles + telegram_messages + api_articles
        ArticleDocument.bulk_insert(merged_articles)
        response = {"statusCode": 200, "body": json.dumps([article.model_dump(exclude="id") for article in merged_articles])}
    except Exception as e:
        response = {"statusCode": 500, "body": f"An error occurred: {str(e)}"}
    finally:
        ArticleDocument.close_connection()
        return response


def daily():
    # Execute daily ETL
    try:
        # For extract functions, default dates are today´s date.
        ct_articles = coin_crawler.extract(n_scrolls=5)

        # Use event loop for telegram functions
        loop = asyncio.get_event_loop()
        telegram_messages = loop.run_until_complete(telegram_crawler.extract_day(loop=loop))

        # Extract yesterdays news since free api has 24 hours delay.
        start_dt = (datetime.now() - timedelta(days=1)).strftime(date_format)
        end_dt = (datetime.now() - timedelta(days=1)).strftime(date_format)
        api_articles = news_api_crawler.extract(
            page=1,
            start_date=start_dt,
            end_date=end_dt
        )

        merged_articles = ct_articles + telegram_messages + api_articles
        ArticleDocument.bulk_insert(merged_articles)
        response = {"statusCode": 200, "body": json.dumps([article.model_dump(exclude="id") for article in merged_articles])}
    except Exception as e:
        response = {"statusCode": 500, "body": f"An error occurred: {str(e)}"}
    finally:
        ArticleDocument.close_connection()
        return response

def handler(event, context: LambdaContext) -> dict[str, Any]:
    mode = event.get("mode")
    if mode == "backfill":
        return backfill()
    else:
        return daily()


if __name__ == "__main__":
    event = {
        "mode": "backfill",
    }
    handler(event, None)
