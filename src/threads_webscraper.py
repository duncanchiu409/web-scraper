from webscraper import Webscraper
from bs4 import BeautifulSoup
import logging
import os
import json
from typing import Callable
from utils import wait_for_element
from selenium.webdriver.common.by import By
from dotenv import dotenv_values
from time import sleep
from datetime import datetime
import pytz

config = dotenv_values(os.path.join(os.path.dirname(os.path.abspath(__file__)), '.env'))
AWS_DYNAMODB_TABLE = config['AWS_DYNAMODB_TABLE'] if config['AWS_DYNAMODB_TABLE'] else os.getenv('AWS_DYNAMODB_TABLE')

THREADS_LOGIN_URL = config['THREADS_LOGIN_URL'] if config['THREADS_LOGIN_URL'] else os.getenv('THREADS_LOGIN_URL')
THREADS_LOGIN_USERNAME = config['THREADS_LOGIN_USERNAME'] if config['THREADS_LOGIN_USERNAME'] else os.getenv('THREADS_LOGIN_USERNAME')
THREADS_LOGIN_PASSWORD = config['THREADS_LOGIN_PASSWORD'] if config['THREADS_LOGIN_PASSWORD'] else os.getenv('THREADS_LOGIN_PASSWORD')
THREADS_URL = config['THREADS_URL'] if config['THREADS_URL'] else os.getenv('THREADS_URL')
THREADS_POSTS_LIMIT = config['THREADS_POSTS_LIMIT'] if config['THREADS_POSTS_LIMIT'] else os.getenv('THREADS_POSTS_LIMIT')

TIMEZONE = config['TIMEZONE'] if config['TIMEZONE'] else os.getenv('TIMEZONE')

def scrape_threads_social_media_results(soup: BeautifulSoup):
    logging.info("Starting to scrape the threads social media results")
    timezone = pytz.timezone(TIMEZONE)
    start_time = int(datetime.now().timestamp())

    try:
        main_div_elements = soup.find_next('div', attrs={'class': 'x78zum5 xdt5ytf x1n2onr6 x1ja2u2z'})
        if main_div_elements is None:
            raise Exception("No main div elements found")

        main_div_element = main_div_elements.find_next('div', attrs={'class': 'x1iyjqo2 x14vqqas'})
        if main_div_element is None:
            raise Exception("Main div element not found")

        div_elements = main_div_element.find_all('div', attrs={'class': 'x78zum5 xdt5ytf'})
        if div_elements is None or len(div_elements) == 0:
            raise Exception("No post div elements found")

        results = []

        i = 0
        for div_element in div_elements:
            span_elements = div_element.find_all('span')
            if len(span_elements) == 0:
                continue

            username = span_elements[1].text
            if "<span>" in username: # it is follow suggestion
                continue

            context = div_element.find_next('div', attrs={'class': 'x1a6qonq x6ikm8r x10wlt62 xj0a0fe x126k92a x6prxxf x7r5mf7'}).text

            a_element = div_element.find_next('a', attrs={'class': 'x1i10hfl xjbqb8w x1ejq31n xd10rxx x1sy0etr x17r0tee x972fbf xcfux6l x1qhh985 xm0m39n x9f619 x1ypdohk xt0psk2 xe8uvvx xdj266r x11i5rnm xat24cr x1mh8g0r xexx8yu x4uap5 x18d9i69 xkhd6sd x16tdsg8 x1hl2dhg xggy1nq x1a2a7pz x1lku1pv x12rw4y6 xrkepyr x1citr7e x37wo2f'})
            if a_element is not None:
                href = a_element.get('href')
                time_element = a_element.find_next('time')
                if time_element is not None:
                    timestamp = time_element.get('datetime')
                else:
                    timestamp = ""
            else:
                href = ""
                timestamp = ""

            picture_element = div_element.find_next('picture')
            if picture_element is not None:
                picture_url = picture_element.find_next('img')['src']
            else:
                picture_url = ""

            like_svg_element = div_element.find_next('svg', attrs={'aria-label': 'Like'})
            if like_svg_element is None:
                logging.debug(f"No like svg element found for {username}")
                like_count = 0
            else:
                like_span_element = like_svg_element.find_next_sibling('span')
                if like_span_element is not None:
                    like_count = like_span_element.text
                else:
                    like_count = 0

            comment_svg_element = div_element.find_next('svg', attrs={'aria-label': 'Comment'})
            if comment_svg_element is None:
                logging.debug(f"No comment svg element found for {username}")
                comment_count = 0
            else:
                comment_span_element = comment_svg_element.find_next_sibling('span')
                if comment_span_element is not None:
                    comment_count = comment_span_element.text
                else:
                    comment_count = 0

            repost_svg_element = div_element.find_next('svg', attrs={'aria-label': 'Repost'})
            if repost_svg_element is None:
                logging.debug(f"No repost svg element found for {username}")
                repost_count = 0
            else:
                repost_span_element = repost_svg_element.find_next_sibling('span')
                if repost_span_element is not None:
                    repost_count = repost_span_element.text
                else:
                    repost_count = 0

            share_svg_element = div_element.find_next('svg', attrs={'aria-label': 'Share'})
            if share_svg_element is None:
                logging.debug(f"No share svg element found for {username}")
                share_count = 0
            else:
                share_span_element = share_svg_element.find_next_sibling('span')
                if share_span_element is not None:
                    share_count = share_span_element.text
                else:
                    share_count = 0

            logging.info(f"Username: {username}, Context: {context}, Timestamp: {timestamp}, Picture: {picture_url}, Like: {like_count}, Comment: {comment_count}, Repost: {repost_count}, Share: {share_count}")

            results.append({
                'id': str(start_time+i),
                'Username': username,
                'Context': context,
                'Timestamp': timestamp,
                'Href': href,
                'Like': like_count,
                'Comment': comment_count,
                'Repost': repost_count,
                'Share': share_count,
                'Datetime': datetime.now(timezone).isoformat(),
            })

            i += 1

        return results

    except Exception as e:
        logging.error(f"Error scraping the threads social media results: {e}")
        return

class ThreadsWebscraper(Webscraper):
    def __init__(self):
        super().__init__()

    def scrape(self, url: str, table_name: str, func: Callable, scroll_to_bottom: bool = True):
        logging.info(f"Starting the webscraper on url: {url}")
        try:
            # Get the directory of the current script
            current_dir = os.path.dirname(os.path.abspath(__file__))
            # Construct the path to threads.json
            threads_json_path = os.path.join(current_dir, 'credentials', 'threads.json')

            with self._driver:
                # Go to the url
                self._driver.get(url)

                # Wait for the threads posts' div element to be present
                wait_for_element(self._driver, "//div[@class='x1a2a7pz x1n2onr6']")

                # If the threads.json file exists, load the cookies and refresh the page
                if os.path.exists(threads_json_path):
                    with open(threads_json_path) as f:
                        d = json.load(f)
                    for cookie in d:
                        self._driver.add_cookie(cookie)
                    self._driver.refresh()
                else:
                    # Go to the threads login url
                    self._driver.get(THREADS_LOGIN_URL)

                    # Wait for the username input element to be present
                    wait_for_element(self._driver, "//input[@placeholder='Username, phone or email']")

                    self._driver.find_element(By.XPATH, "//input[@placeholder='Username, phone or email']").send_keys(THREADS_LOGIN_USERNAME)
                    self._driver.find_element(By.XPATH, "//input[@placeholder='Password']").send_keys(THREADS_LOGIN_PASSWORD)
                    self._driver.find_element(By.XPATH, "//input[@type='submit']").submit()

                    wait_for_element(self._driver, "//div[@class='xc26acl x6s0dn4 x78zum5 xl56j7k x6ikm8r x10wlt62 x1swvt13 x1pi30zi xlyipyv xp07o12']")
                    self._driver.get(url)

                # Wait for the threads posts' div element to be present
                wait_for_element(self._driver, "//div[@class='x1a2a7pz x1n2onr6']")

                # Wait for dynamic content to load (ensure the page is fully loaded)
                sleep(2)

                cookies = self._driver.get_cookies()

                # Write cookies to threads.json
                with open(threads_json_path, 'w') as f:
                    json.dump(cookies, f)

                results = []
                if not scroll_to_bottom:
                    # Parse the page source
                    soup = BeautifulSoup(self._driver.page_source, 'html5lib')
                    results = func(soup)

                    # Save the results to dynamodb
                    self.save_to_dynamodb(table_name, results)
                else:
                    while len(results) < int(THREADS_POSTS_LIMIT):
                        soup = BeautifulSoup(self._driver.page_source, 'html5lib')
                        for item_1 in func(soup):
                            found = False
                            for item_2 in results:
                                if item_1['Href'] == item_2['Href']:
                                    found = True
                                    break
                            if not found:
                                results.append(item_1)

                        self._driver.execute_script("window.scrollTo({top:document.body.scrollHeight, behavior:'smooth'})")
                        logging.info("Scrolling to the bottom of the page")

                    self.save_to_dynamodb(table_name, results)

        except Exception as e:
            logging.error(f"Error scraping: {e}")
            exit()

if __name__ == "__main__":
    # Configure the logging
    log_fmt = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    logging.basicConfig(level=logging.INFO, format=log_fmt)

    webscraper = ThreadsWebscraper()
    webscraper.scrape(
        url=THREADS_URL,
        table_name=AWS_DYNAMODB_TABLE,
        func=scrape_threads_social_media_results,
        scroll_to_bottom=True)