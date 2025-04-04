from selenium import webdriver
import logging
import boto3
from typing import Callable
from bs4 import BeautifulSoup
from selenium.webdriver.common.by import By
from utils import wait_for_element
import os
from time import sleep
import json
from dotenv import dotenv_values

config = dotenv_values(os.path.join(os.path.dirname(os.path.abspath(__file__)), '.env'))
AWS_REGION = config['AWS_REGION'] if config['AWS_REGION'] else os.getenv('AWS_REGION')
AWS_PROFILE = config['AWS_PROFILE'] if config['AWS_PROFILE'] else os.getenv('AWS_PROFILE')

class Webscraper:
    def __init__(self):
        self._initialize_dynamodb_connection()
        self._initialize_webdriver()

    def _initialize_dynamodb_connection(self):
        try:
            logging.info(f"Initializing dynamodb connection with profile: {AWS_PROFILE} and region: {AWS_REGION}")
            # Create a session with the specified profile
            session = boto3.Session(profile_name=AWS_PROFILE)
            # Create a DynamoDB resource with specified region
            self._dynamodb = session.resource('dynamodb', region_name=AWS_REGION)
        except Exception as e:
            logging.error(f"Error initializing dynamodb connection: {e}")
            exit()

    def save_to_dynamodb(self, table_name: str, results: list):
        try:
            table = self._dynamodb.Table(table_name)
            for result in results:
                table.put_item(Item=result)
            logging.info(f"Saved {len(results)} items to dynamodb table: {table_name}")
        except Exception as e:
            logging.error(f"Error saving to dynamodb: {e}")
            exit()

    def delete_dynamodb_table(self, table_name: str):
        try:
            self._dynamodb.Table(table_name).delete()
            logging.info(f"Deleted dynamodb table: {table_name}")
        except Exception as e:
            logging.error(f"Error deleting dynamodb table: {e}")
            exit()

    def _initialize_webdriver(self):
        logging.info("Initializing webdriver")
        while True:
            try:
                options = webdriver.ChromeOptions()
                options.add_argument("--no-sandbox")
                options.add_argument("--disable-dev-shm-usage")  # Recommended for Docker
                # options.add_argument("--log-level=3")
                self._driver = webdriver.Remote(
                    command_executor='http://localhost:4444',
                    options=options
                )
                break
            except Exception as e:
                logging.error(f"Error initializing webdriver: {e}")
                sleep(1)