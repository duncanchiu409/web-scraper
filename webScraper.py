from selenium import webdriver
import logging
import boto3
from typing import Callable
from bs4 import BeautifulSoup

class WebScraper:
    def __init__(self, region_name: str, profile_name: str):
        self.region_name = region_name
        self.profile_name = profile_name

        self._initialize_dynamodb_connection()
        self._initialize_webdriver()

    def _initialize_dynamodb_connection(self):
        try:
            # Create a session with the specified profile
            session = boto3.Session(profile_name=self.profile_name)
            # Create a DynamoDB resource with specified region
            self._dynamodb = session.resource('dynamodb', region_name=self.region_name)
        except Exception as e:
            logging.error(f"Error initializing dynamodb connection: {e}")
            return

    def save_to_dynamodb(self, table_name: str, results: list):
        try:
            table = self._dynamodb.Table(table_name)
            for result in results:
                table.put_item(Item=result)
            logging.info(f"Saved {len(results)} items to dynamodb table: {table_name}")
        except Exception as e:
            logging.error(f"Error saving to dynamodb: {e}")
            return

    def delete_dynamodb_table(self, table_name: str):
        try:
            self._dynamodb.Table(table_name).delete()
            logging.info(f"Deleted dynamodb table: {table_name}")
        except Exception as e:
            logging.error(f"Error deleting dynamodb table: {e}")
            return

    def _initialize_webdriver(self):
        try:
            options = webdriver.ChromeOptions()
            options.add_argument("--headless")

            self._driver = webdriver.Chrome(options=options)
        except Exception as e:
            logging.error(f"Error initializing webdriver: {e}")
            return

    def scrape(self, url: str, table_name: str, func: Callable):
        logging.info(f"Starting the webscraper on url: {url}")
        try:
            self._driver.get(url)
            soup = BeautifulSoup(self._driver.page_source, 'html5lib')
            results = func(soup)
        except Exception as e:
            logging.error(f"Error scraping: {e}")
            return

        self.save_to_dynamodb(table_name, results)
        logging.info(f"Webscraper finished")

    def __del__(self):
        self._driver.quit()