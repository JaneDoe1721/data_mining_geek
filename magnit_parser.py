from bs4 import BeautifulSoup
import requests
from urllib.parse import urlparse
from pymongo import MongoClient
import datetime
import re

MONTHS = {
    "янв": 1,
    "фев": 2,
    "март": 3,
    "апр": 4,
    "май": 5,
    "июн": 6,
    "июл": 7,
    "авг": 8,
    "сент": 9,
    "окт": 10,
    "ноя": 11,
    "дек": 12,
}


class MagnitParser:
    _headers = {
        'User-Agent': "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:81.0) Gecko/20100101 Firefox/81.0",
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
        date = product_soup.find('div', 'action__date-label').text
        date_list = date.replace('с', '', 1).replace(' ', '', 1).split('по')
        finaly_list = []
        for date in date_list:
            temp_date = date.split()
            finaly_list.append(datetime.datetime(year=datetime.datetime.now().year, day=int(temp_date[0]),
                                     month=MONTHS[temp_date[1][:3]]))
        product_template = {
            'url': url,
            'promo_name': product_soup.find('p', 'action__name-text').text,
            'product_name': product_soup.find('div', 'action__title').text,
            'old_price': float(product_soup.find('div', 'label__price label__price_old').text.replace('\n','', 1).replace('\n','.',1).replace('\n','',1)),
            'new_price': float(product_soup.find('div', 'label__price label__price_new').text.replace('\n','', 1).replace('\n','.',1).replace('\n','',1)),
            'image_url': f'{"https://magnit.ru"}{product_soup.find("img", attrs={"class": "action__image"}).attrs["data-src"]}',
            'date_from': finaly_list[0],
            'date_to': finaly_list[1],
        }
        print(1)

        return product_template

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