# Задача организовать сбор данных,
# необходимо иметь метод сохранения данных в .json файлы
#
# результат: Данные скачиваются с источника, при вызове метода/функции сохранения в файл скачанные данные сохраняются
# в Json вайлы, для каждой категории товаров должен быть создан отдельный файл и содержать
# товары исключительно соответсвующие данной категории.
#
# пример структуры данных для файла:
#
# {
# "name": "имя категории",
# "code": "Код соответсвующий категории (используется в запросах)",
# "products": [{PRODUCT},  {PRODUCT}........] # список словарей товаров соответсвующих данной категории
# }

import json
import requests
from typing import List, Dict
import datetime
import os


class Cat5ka:
    __url = {
        'categories' : 'https://5ka.ru/api/v2/categories/',
        'special_offers' : 'https://5ka.ru/api/v2/special_offers/',
    }

    __params = {
        'records_per_page' : 20,
        'categories' : [],
    }

    __headers = {
        'User-Agent' : 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:81.0) Gecko/20100101 Firefox/81.0',
    }

    __recover = ('.', '"', "'", '*', '#', '$', '%', '@', '+', ',', '-', '/', '\\',)

    def __init__(self, name='data'):
        self.category = self.categories()
        self.data = os.path.dirname(__file__).join(name)

    def categories(self) -> List[Dict[str, str]]:
        response = requests.get(self.__url['categories'])
        return response.json()

    def parse_use(self):
        for category in self.category:
            self.get_products(category)

    def get_products(self, category=None):
        url = self.__url['special_offers']
        params = self.__params
        params['categories'] = category['parent_group_code']

        while url:
            response = requests.get(url, params=params, headers=self.__headers)
            data = response.json()
            url = data['next']
            params = {}

            if category.get('special_offers'):
                category['special_offers'].extend(data['results'])
            else:
                category['special_offers'] = data['results']
        category['parse_date'] = datetime.datetime.now().timestamp()

    def save_to_file(self, category):
        name = category['parent_group_name']
        for itm in self.__recover:
            name = name.replace(itm, '')
        name = '_'.join(name.split()).lower()

        print(1)
        file_path = os.path.join(self.data, f'{name}.json')
        print(file_path)

        with open(file_path, 'w', encoding='UTF-8') as file:
            json.dump(category, file, ensure_ascii=False)


if __name__ == '__main__':
    parser = Cat5ka()
    parser.parse_use()


