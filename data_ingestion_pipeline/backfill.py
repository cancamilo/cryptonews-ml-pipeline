import logging
import asyncio
import pandas as pd
from typing import Any
from datetime import datetime, timedelta
from crawlers import CoinTelegraphCrawler, TelegramChannelsCrawler, NewsBTCCrawler

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

date_format="%Y-%m-%d"
coin_crawler = CoinTelegraphCrawler(dev=True)
news_btc_crawler = NewsBTCCrawler(dev=True)
telegram_crawler = TelegramChannelsCrawler()

k_channel=100

def backfill():
    """ Extract past articles by scrolling multiple times 
    """
    start_dt = datetime.now() - timedelta(days=1)
    end_dt = datetime.now()
    
    ct_articles = coin_crawler.extract(
        n_scrolls=200,
        start_date=start_dt.strftime(date_format),
        end_date=end_dt.strftime(date_format)
    )
    save_as_df(ct_articles, name="data/coin_telegraph_articles.csv")
    logger.info(f"Extracted {len(ct_articles)} articles from cointelegraph.")

    # Use event loop for telegram functions
    loop = asyncio.get_event_loop()
    telegram_messages = loop.run_until_complete(telegram_crawler.extract(channel_count=k_channel, loop=loop))
    save_as_df(telegram_messages, name="data/telegram_articles.csv")
    logger.info(f"Extracted {len(telegram_messages)} articles from telegram.")

    articles = news_btc_crawler.extract(3, start_date=start_dt, end_date=end_dt)
    save_as_df(articles, name="data/news_btc_articles.csv")
    logger.info(f"Extracted {len(articles)} from newsbtc")

    save_as_df(ct_articles + telegram_messages + articles, name="data/all_articles.csv")
    return articles

def daily():
    """ Extract articles for the current date only
    """
    ct_articles = coin_crawler.extract(n_scrolls=10)
    save_as_df(ct_articles)
    return ct_articles

def save_as_df(articles: pd.DataFrame, name: str) -> None:
    df = pd.DataFrame.from_records([article.model_dump() for article in articles])
    df.to_csv(name, index=False)

if __name__ == "__main__":
    try:
        backfill()
    except Exception as e:
        print("Unable to extract articles", e)

