from typing import Any
import json
from aws_lambda_powertools import Logger
from aws_lambda_powertools.utilities.typing import LambdaContext
from crawlers import CoinTelegraphCrawler

logger = Logger(service="decodingml/crawler")

def handler(event, context: LambdaContext) -> dict[str, Any]:
    crawler = CoinTelegraphCrawler()
    try:
        articles = crawler.extract()
        return {"statusCode": 200, "body": json.dumps([article.model_dump(exclude="id") for article in articles])}
    except Exception as e:
        return {"statusCode": 500, "body": f"An error occurred: {str(e)}"}


if __name__ == "__main__":
    event = {
        "user": "Paul Iuztin",
        "link": "https://www.linkedin.com/in/vesaalexandru/",
    }
    handler(event, None)
