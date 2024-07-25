import time
from datetime import datetime
from tempfile import mkdtemp
from selenium import webdriver
from typing import List, Any
import logging
from bs4 import BeautifulSoup
from crawlers.base import BaseCrawler
from models.documents import ArticleDocument
from config import settings
from selenium.webdriver.common.by import By

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


class NewsBTCCrawler(BaseCrawler):
    name = "coin_telegraph_crawler"
    date_format = "%Y-%m-%d"
    url = "https://cointelegraph.com/"

    def __init__(self, dev=False) -> None:
        super().__init__()

        if dev:
            # observe crawling behaviour in dev mode
            self.driver = webdriver.Chrome()
        else:
            options = webdriver.ChromeOptions()
            options.binary_location = "/opt/chrome/chrome"
            options.add_argument("--no-sandbox")
            options.add_argument("--headless=new")
            options.add_argument("--single-process")
            options.add_argument("--disable-dev-shm-usage")
            options.add_argument("--disable-gpu")
            options.add_argument("--log-level=3")
            options.add_argument("--disable-popup-blocking")
            options.add_argument("--disable-notifications")
            options.add_argument("--disable-dev-tools")
            options.add_argument("--ignore-certificate-errors")
            options.add_argument("--no-zygote")
            options.add_argument(f"--user-data-dir={mkdtemp()}")
            options.add_argument(f"--data-path={mkdtemp()}")
            options.add_argument(f"--disk-cache-dir={mkdtemp()}")
            options.add_argument("--remote-debugging-port=9222")
            options.add_experimental_option("detach", True)
            self.driver = webdriver.Chrome(
                service=webdriver.ChromeService("/opt/chromedriver"), options=options
            )

    def extract(
        self,
        n_scrolls,
        start_date=datetime.now().strftime(date_format),
        end_date=datetime.now().strftime(date_format),
    ) -> List[Any]:
        """Scrap news from cointelegraph"""

        url = "https://www.newsbtc.com/news/"

        self.driver.get(url)

        # Find the list of articles and extract links 
        links = []

        parent = self.driver.find_element(By.ID)
        article_elements = parent.find_elements(By.TAG_NAME, 'article')
        links = [article.find_element(By.TAG_NAME, 'a').get_attribute('href') for article in article_elements]

        # articles = []
        # articles.append(
        #     ArticleDocument(
        #         source="coin_telepraph",
        #         title=title,
        #         summary=summary,
        #         content=content,
        #         published_at=datetime,
        #     )
        # )

        self.driver.close()

    def date_filter(self, date, lower: str, upper: str):
        dt = datetime.strptime(date, self.date_format)
        lower_dt = datetime.strptime(lower, self.date_format)
        upper_dt = datetime.strptime(upper, self.date_format)
        return dt >= lower_dt and dt <= upper_dt

    def save(self, articles) -> None:
        ArticleDocument.bulk_insert(articles)

    def __scroll_ntimes(self, n=3) -> None:
        """Scroll a webpage n times

        Args:
            n (int, optional): Number of page scrolls before stop.
        """

        scrolls = 0
        while True:
            # # Scroll down the page a few times
            self.driver.execute_script("window.scrollBy(0, 2 * window.innerHeight);")

            # Wait to load page
            time.sleep(1)

            scrolls += 1
            if scrolls == n:
                break
