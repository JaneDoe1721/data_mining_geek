import requests
import datetime as dt
from bs4 import BeautifulSoup
from urllib.parse import urlparse
from pymongo import MongoClient


MONTHS = {
    "янв": 1,
    "фев": 2,
    "мар": 3,
    "апр": 4,
    "май": 5,
    "мая": 5,
    "июн": 6,
    "июл": 7,
    "авг": 8,
    "сен": 9,
    "окт": 10,
    "ноя": 11,
    "дек": 12,
}


class MagnitParser:
    _headers = {
        'User-Agent': "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:81.0) Gecko/20100101 Firefox/81.0",
    }

    _params = {
        'geo': 'moskva',
    }

    def __init__(self, start_url):
        self.start_url = start_url
        self._url = urlparse(start_url)
        mongo_client = MongoClient('mongodb://localhost:27017')
        self.db = mongo_client['parse_10']

    def _get_soup(self, url: str):
        response = requests.get(url, headers=self._headers)
        return BeautifulSoup(response.text, 'lxml')

    def parse(self):
        soup = self._get_soup(self.start_url)
        catalog = soup.find('div', attrs={'class': "сatalogue__main"})
        products = catalog.findChildren('a', attrs={'class': 'card-sale'})
        for product in products:
            if len(product.attrs.get('class')) > 2 or product.attrs.get('href')[0] != '/':
                continue
            product_url = f'{self._url.scheme}://{self._url.hostname}{product.attrs.get("href")}'
            product_soup = self._get_soup(product_url)
            product_data = self.get_product_structure(product_soup, product_url)
            self.save_to(product_data)

    @staticmethod
    def date_parse(date_string: str):
        date_list = date_string.replace('с', '', 1).replace(' ', '', 1).split('по')
        for date in date_list:
            temp_date = date.split()
            yield dt.datetime(year=dt.datetime.now().year, day=int(temp_date[0]), month=MONTHS[temp_date[1][:3]])

    def get_product_structure(self, product_soup, url):
        url_p = urlparse(url)
        dt_parser = self.date_parse(product_soup.find('div', attrs={'class': 'action__date-label'}).text)
        product_template = {

            'promo_name': lambda soups: soups.find('p', attrs={'class': 'action__name-text'}).text,

            'product_name': lambda soups: str(soups.find('div', attrs={'class': 'action__title'}).text),

            'old_price': lambda soups: float(
                '.'.join(itm for itm in soups.find('div', attrs={'class': 'label__price_old'}).text.split())),

            'new_price': lambda soups: float(
                '.'.join(itm for itm in soups.find('div', attrs={'class': 'label__price_new'}).text.split())),

            'image_url': lambda
                soups: f"{url_p.scheme}://{url_p.netloc}{soups.find('img', attrs={'class': 'action__image'}).attrs['data-src']}",

            'date_from': lambda _: next(dt_parser),
            'date_to': lambda _: next(dt_parser),
        }
        product = {'url': url, }
        for key, value in product_template.items():
            try:
                product[key] = value(product_soup)
            except Exception:
                product[key] = None

        return product

    def save_to(self, product_data: dict):
        collection = self.db['magnit']
        collection.insert_one(product_data)


if __name__ == '__main__':
    url = 'https://magnit.ru/promo/?geo=moskva'
    parser = MagnitParser(url)
    parser.parse()