from bs4 import BeautifulSoup
import requests
from urllib.parse import urlparse
from pymongo import MongoClient
import re

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
            print(1)

    def get_product_structure(self, product_soup, url):

        product_template = {

            'promo_name': ('div', 'action__title', 'text'),
            'product_name': ('div', 'action__title', 'text'),
            'old_price': ('div', 'label__price_old', 'text'),
            'new_price': ('div', 'label__price_new',  'text'),
            'image_url': ('img', '', 'text'),
            'date_from': ('div', 'action__date-label', 'text'),
            'date_to': ('div', 'action__date-label', 'text'),
        }
        product = {'url': url, }
        for key, value in product_template.items():
            try:
                product[key] = getattr(product_soup.find(value[0], attrs={'class': value[1]}), value[2])
            except Exception:
                product[key] = None

        return product

    def save_to(self, product_data: dict):
        collection = self.db['magnit']
        collection.insert_one(product_data)
        print(1)


if __name__ == '__main__':
    url = 'https://magnit.ru/promo/?geo=moskva'
    parser = MagnitParser(url)
    parser.parse()


mongo_client = MongoClient('mongodb://localhost:27017')
db = mongo_client['parse_10']
collection = db['magnit']

sort = collection.find().sort('promo_name')

for itm in sort:
    print(itm)