from bs4 import BeautifulSoup
from datetime import datetime
import logging
from time import sleep
from webScraper import WebScraper

def scrape_coinmarketcap_crypto_trend_ranking_results(soup: BeautifulSoup):
    start_time = int(datetime.now().timestamp())

    sleep(2)

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
                'Datetime': datetime.now().isoformat(),
            })

        return results

    except Exception as e:
        logging.error(f"Error scraping the coinmarketcap crypto trend ranking results: {e}")
        return

if __name__ == "__main__":
    # Configure the logging
    log_fmt = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    logging.basicConfig(level=logging.INFO, format=log_fmt)

    webscraper = WebScraper(region_name='ap-southeast-1', profile_name='local-dynamoDB-access')
    webscraper.scrape(
        url="https://coinmarketcap.com/trending-cryptocurrencies/",
        table_name="coinMarketCap-trend-ranking-table",
        func=scrape_coinmarketcap_crypto_trend_ranking_results
    )