import time
from tempfile import mkdtemp
from selenium import webdriver
from typing import List, Any
from aws_lambda_powertools import Logger
from bs4 import BeautifulSoup
from crawlers.base import BaseCrawler
from models.documents import CoinTelegraphArticle
from selenium.webdriver.common.by import By


logger = Logger(service="cryto_fetcher/crawler")


class CoinTelegraphCrawler(BaseCrawler):
    url = "https://cointelegraph.com/"

    def __init__(self) -> None:
        super().__init__()
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
            service=webdriver.ChromeService("/opt/chromedriver"),
            options=options,
        )
        # self.driver = webdriver.Chrome()

    def extract(self) -> List[Any]:
        """Scrap news from cointelegraph"""

        self.driver.get("https://cointelegraph.com/")
        main_carousel = self.driver.find_element(By.XPATH, "//div[@data-testid='carousel-main']")
        first_link = main_carousel.find_element(By.XPATH, "//a[@data-testid='main-news-controls__link']")
        first_link.click()

        logger.info(f"Scraping articles from: {self.url}")
        self.__scroll_ntimes()
        articles = []

        # Parse the page source
        soup = BeautifulSoup(self.driver.page_source, "html.parser")

        # Find all the 'article' elements
        article_elements = soup.find_all("article")

        # For each 'article', find the 'h1' element and all 'div' siblings
        for article in article_elements:
            h1_element = article.find("h1")
            title = h1_element.text
            summary = h1_element.find_next_sibling("div").text
            content_div = article.find("div", class_="post__content-wrapper")
            time_element = article.find("time")
            datetime = time_element.get("datetime") if time_element else None
            ps = content_div.find_all("p")
            content = " ".join(p.text for p in ps if "Advertisement" not in p.text)

            # Create a dictionary for each article and append it to the list

            articles.append(
                CoinTelegraphArticle(
                    title=title, summary=summary, content=content, date=datetime
                )
            )

        # self.save(articles)
        self.driver.close()
        return articles

    def save(self, articles) -> None:
        CoinTelegraphArticle.bulk_insert(articles)

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
            time.sleep(2)

            scrolls += 1
            if scrolls == n:
                break
