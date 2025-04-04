from bs4 import BeautifulSoup
from datetime import datetime
import logging
from time import sleep
from webscraper import WebScraper
import pytz

def scrape_coinmarketcap_crypto_trend_ranking_results(soup: BeautifulSoup):
    logging.info("Starting to scrape the coinmarketcap crypto trend ranking results")
    start_time = int(datetime.now().timestamp())
    timezone = pytz.timezone('Asia/Hong_Kong')

    try:
        tbody_html_element = soup.find_next('tbody')
        if tbody_html_element is None:
            raise Exception("Tbody element not found")

        tr_elements = tbody_html_element.find_all('tr')
        if tr_elements is None or len(tr_elements) == 0:
            raise Exception("No table rows found")

        assert len(tr_elements) >= 9

        results = []

        for i in range(len(tr_elements)):
            td_html_elements = tr_elements[i].find_all('td')

            # Ranking
            ranking = td_html_elements[1].text

            # Crypto Name
            crypto_name = td_html_elements[2].find_next('p').text

            # Crypto Symbol
            crypto_symbol = td_html_elements[2].find_next('p', attrs={'class': 'coin-item-symbol'}).text

            # Price td
            span_html_element = td_html_elements[3].text

            # 24hrs Change
            first_change = td_html_elements[4].text

            # 7days Change
            second_change = td_html_elements[5].text

            # 30days Change
            third_change = td_html_elements[6].text

            # Market Cap
            marketCap = td_html_elements[7].text

            # 24hrs Volume
            volume = td_html_elements[8].text

            logging.debug(f"Scraped {ranking}, {crypto_name}, {crypto_symbol}, {span_html_element}, {first_change}, {second_change}, {third_change}, {marketCap}, {volume}")

            results.append({
                'id': start_time+i,
                'Crypto Name': crypto_name,
                'Crypto Symbol': crypto_symbol,
                'Ranking': ranking,
                '24hrs % Change': first_change,
                '7days % Change': second_change,
                '30days % Change': third_change,
                'Market Cap': marketCap,
                '24hrs Volume': volume,
                'Datetime': datetime.now(timezone).isoformat(),
            })

        return results

    except Exception as e:
        logging.error(f"Error scraping the coinmarketcap crypto trend ranking results: {e}")
        return

def scrape_threads_social_media_results(soup: BeautifulSoup):
    logging.info("Starting to scrape the threads social media results")
    timezone = pytz.timezone('Asia/Hong_Kong')
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

if __name__ == "__main__":
    # Configure the logging
    log_fmt = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    logging.basicConfig(level=logging.INFO, format=log_fmt)

    webscraper = WebScraper()
    webscraper.scrape(
        url="https://www.threads.net/search?q=cryptocurrency",
        table_name="threads_posts_table",
        func=scrape_threads_social_media_results,
        scroll_to_bottom=True
    )