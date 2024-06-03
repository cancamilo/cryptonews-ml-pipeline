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
        scrolls = 100
        logger.info(f"Starting crawler with {scrolls} scrolls.")

        start_dt = datetime.now() - timedelta(days=360)
        end_dt = datetime.now()
        ct_articles = coin_crawler.extract(
            n_scrolls=scrolls, 
            start_date=start_dt.strftime(date_format),
            end_date=end_dt.strftime(date_format)
        )

        logger.info(f"Extracted {len(ct_articles)} articles from cointelegraph.")

        # Use event loop for telegram functions
        loop = asyncio.get_event_loop()
        telegram_messages = loop.run_until_complete(telegram_crawler.extract(channel_count=100, loop=loop))

        merged_articles = ct_articles + telegram_messages
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
        ct_articles = coin_crawler.extract(n_scrolls=10)

        # Use event loop for telegram functions
        loop = asyncio.get_event_loop()
        telegram_messages = loop.run_until_complete(telegram_crawler.extract_day(loop=loop))

        merged_articles = ct_articles + telegram_messages
        ArticleDocument.bulk_insert(merged_articles)
        response = {"statusCode": 200, "body": json.dumps([article.model_dump(exclude=["id", "content"]) for article in merged_articles[:10]])}
    except Exception as e:
        response = {"statusCode": 500, "body": f"An error occurred: {str(e)}"}
    finally:
        ArticleDocument.close_connection()
        return response

def handler(event, context: LambdaContext) -> dict[str, Any]:
    mode = event.get("mode")
    if mode == "backfill":
        return backfill()
    elif mode == "daily":
        return daily()
    else:
        return {"statusCode": 400, "body": f"mode {mode} not valid"}



if __name__ == "__main__":
    event = {
        "mode": "daily",
    }
    handler(event, None)
