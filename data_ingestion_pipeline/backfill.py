import asyncio
import fire
import pandas as pd
import logging
from datetime import datetime, timedelta
from models.documents import ArticleDocument
from crawlers import CoinTelegraphCrawler, TelegramChannelsCrawler

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

date_format="%Y-%m-%d"
coin_crawler = CoinTelegraphCrawler(dev=True)
telegram_crawler = TelegramChannelsCrawler()


def to_df(articles):
    df =  pd.DataFrame.from_records([record.model_dump() for record in articles])
    df["parsed_dt"] = pd.to_datetime(df["published_at"])
    return df

def backfill(scrolls=30, k_channel=100, save_as_csv=True):
    try:
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
        telegram_messages = loop.run_until_complete(telegram_crawler.extract(channel_count=k_channel, loop=loop))

        logger.info(f"Extracted {len(telegram_messages)} articles from telegram.")

        merged_articles = ct_articles + telegram_messages
        ArticleDocument.bulk_insert(merged_articles)

        if save_as_csv:
            df = to_df(merged_articles)
            df.to_csv("data/articles.csv")

        return merged_articles
    except Exception as e:
        logger.exception(f"Unable to fetch articles {e}")
    finally:
        ArticleDocument.close_connection()
        return []

if __name__ == "__main__":
    fire.Fire(backfill)
    

    