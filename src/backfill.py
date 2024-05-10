import asyncio
from datetime import datetime, timedelta
from crawlers import CoinTelegraphCrawler, TelegramChannelsCrawler, NewsFetcher

# TODO: delete this when the lambda function is ready for backfill and daily etl

if __name__ == "__main__":

    # Crawl coin telegraph articles
    coin_crawler = CoinTelegraphCrawler(dev=True)
    ct_articles = coin_crawler.extract(n_scrolls=3)

    # extract 5000 telegram messages per channel.
    telegram_crawler = TelegramChannelsCrawler(5) 
    loop = asyncio.get_event_loop()
    telegram_messages = loop.run_until_complete(telegram_crawler.extract(loop))

    # Extract maximum allowed articles from NewsAPI.
    news_api_crawler = NewsFetcher()
    date_format="%Y-%m-%d"
    start_dt = datetime.now() - timedelta(days=5)
    end_dt = datetime.now()

    api_articles = news_api_crawler.extract(
        page=1,
        start_date=start_dt.strftime(date_format),
        end_date=end_dt.strftime(date_format)
    )
    

    