import requests
import json
import datetime as dt
import time
from bs4 import BeautifulSoup
from urllib.parse import urlparse
import re

from database import Geek_posts
from models import Writer, Tag, Post

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


class PostsParser:

    __url = {
        'start_url':  'https://geekbrains.ru/posts',
        'comment_url': 'https://geekbrains.ru/api/v2/comments',
    }

    __params = {
        'commentable_type': 'Post',
        'commentable_id': 2391,
        'order': 'desc',
    }

    def __init__(self, db):
        self.attended_urls = set()
        self.links = set()
        self.data_post = []
        self.db: Geek_posts = db

    def parse(self, url=__url['start_url']):
        while url:
            if url in self.attended_urls:
                break
            response = requests.get(url)
            self.attended_urls.add(url)
            soup = BeautifulSoup(response.text, 'lxml')
            url = self.next_page(soup)
            self.search_links(soup)
            time.sleep(0.100)

    def next_page(self, soup: BeautifulSoup):
        next = soup.find('ul', attrs={'class': 'gb__pagination'})
        future = next.find('a', text=re.compile('›'))
        if future and future.get('href'):
            return f'{"https://geekbrains.ru"}{future.get("href")}'
        else:
            return None

    def search_links(self, soup: BeautifulSoup):
        cover = soup.find('div', attrs={'class': 'post-items-wrapper'})
        posts = cover.find('div', attrs={'class': 'post-item'})
        link = set()
        for item in posts:
            link.add(f'{"https://geekbrains.ru"}{item.find("a").get("href")}')
        self.links.update(link)

    def main_parse(self):
        for url in self.links:
            if url in self.attended_urls:
                continue
            response = requests.get(url)
            self.attended_urls.add(url)
            soup = BeautifulSoup(response.text, 'lxml')
            if len(self.data_post) > 5:
                break
            self.data_post.append(self.get_post_data(soup, url))
            time.sleep(0.3)
            # self.data_post.append(self.writer_data(soup))
            time.sleep(0.3)

    def get_post_data(self, soup: BeautifulSoup, url):
        content = soup.find('div', attrs={'class': 'blogpost-content', 'itemprop': "articleBody"})
        img = content.find('img')
        result_img = ''
        datetime = soup.find('div', attrs={'class': 'blogpost-date-views'}).find(attrs={'class': 'text-md'}).text
        temp_date = datetime.split()
        if img:
            result_img = img.get('src')
        else:
            result_img = None

        result = {'url': url,
                  'title': soup.find('h1', attrs={'class': 'blogpost-title'}).text,
                  'img_url': result_img,
                  'date': dt.datetime(year=dt.datetime.now().year, day=int(temp_date[0]), month=MONTHS[temp_date[1][:3]])
                  }
        self.db.add_post(Post(**result))

    def writer_data(self, soup: BeautifulSoup):
        autor = soup.find('div', attrs={'class': 'text-lg', 'itemprop': "author"})
        writer_result = {
            'name': autor.text,
            'url': f'{"https://geekbrains.ru"}{autor.findParent("a").get("href")}',
        }
        result = Writer(**writer_result)

        return result

    def tags_data(self, soup: BeautifulSoup):
        tags = soup.find_all('a', attrs={'class': 'small'})
        tag = ''
        for itm in tags:
             tag += f'{itm.text}, '

        tags_result = {
            'name': '',
            'url': '',
        }


    def comment_parse(self):
        params = self.__params
        response_comment = requests.get(self.__url['comment_url'], params=params)
        soup_comment = BeautifulSoup(response_comment.text, 'lxml')
        return soup_comment


if __name__ == '__main__':
    db = Geek_posts('sqlite:///gb_blog.db')
    parser = PostsParser(db)
    parser.parse()
    parser.main_parse()
    parser.comment_parse()
