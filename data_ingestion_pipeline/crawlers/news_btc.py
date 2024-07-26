import time
from datetime import datetime
from tempfile import mkdtemp
from selenium import webdriver
from typing import List, Any
import logging
from bs4 import BeautifulSoup
from urllib.parse import urlparse
from models.documents import ArticleDocument
from datetime import datetime, timedelta
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

    date_map = {
        "minute": 1,
        "hour": 60,
        "day": 24 * 60,
        "week": 7 * 24 * 60
    }

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

    def get_minutes(self, date_string):
        "Given a string with a number and a time period, return the equivalent number of minutes. e.g 1 hour -> 60 minutes"
        parts = date_string.split(" ")
        num = int(parts[0]) 
        window = parts[1].replace("s", "")
        minutes = num * self.date_map[window]
        return minutes

    def extract_article(self, link):
        "Extract the titles and paragraphs of a page with an article"

        parsed_url = urlparse(link)

        # Split the path to get components
        path_components = parsed_url.path.split('/')

        # Extract the topic and title
        topic = path_components[2]  # 'company'
        title = path_components[-2].replace('-', ' ')

        # Parse the page source
        self.driver.get(link)
        time.sleep(1) # wait for content to load     
        soup = BeautifulSoup(self.driver.page_source, "html.parser")

        # Find date
        delta_text = soup.find("div", class_="jeg_meta_date").find("div").get_text().strip()
        dt = datetime.now() - timedelta(minutes=self.get_minutes(delta_text))
        date = datetime.strftime(dt, self.date_format)

        soup.find('div', class_='entry_content')

        # Find all h1, h2 and p elements within the jeg_inner_content div
        relevant_elements = soup.find('div', class_='content-inner').find_all(['h1', 'h2', 'p'])

        # Extract the text content from each element
        extracted_text = [element.text.strip() for element in relevant_elements]
        text = " ".join(extracted_text)

        # Print the extracted text
        return ArticleDocument(source="newsbtc", title=title, content=text, published_at=date)

    def extract(
        self,
        n_scrolls,
        start_date=datetime.now().strftime(date_format),
        end_date=datetime.now().strftime(date_format),
    ) -> List[Any]:
        """Scrap news from news btc"""

        url = "https://www.newsbtc.com/news/"
        self.driver.get(url)

        # Find the list of articles and extract links
        parent = self.driver.find_element(By.ID, "load-more-article-stream")

        for _ in range(n_scrolls):
            self.driver.execute_script("window.scrollBy(0, document.body.scrollHeight);")
            
            # load more button
            load_button = self.driver.find_element(By.ID, "load-more-container")
            load_button.click()
            time.sleep(1)

        # After clicking the load button, collect all article elements and extract their links
        article_elements = parent.find_elements(By.TAG_NAME, 'article')
        links = [article.find_element(By.TAG_NAME, 'a').get_attribute('href') for article in article_elements]

        # TODO: extract the date from the article_elements and filter before visiting the links.

        # Visit each link saved before
        articles = []
        for link in links:
            article = self.extract_article(link)
            articles.append(article)
            time.sleep(1.5)  # Adjust the sleep time as needed to allow the page to load

        self.driver.close()
        return articles



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
