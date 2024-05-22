import logger_utils
from db.documents import ArticleDocument

logger = logger_utils.get_logger(__name__)

def insert_articles() -> None:
    
    mock1 = ArticleDocument(
        source="medium",
        title="btc news",
        content="wen moon",
        summary=None
    )

    articles=[mock1]

    ArticleDocument.bulk_insert(articles)

    logger.info(
        "Articles inserted into collection", num=len(articles)
    )


if __name__ == "__main__":
    insert_articles()
    