import requests
from datetime import datetime
from bs4 import BeautifulSoup, element
from urllib.parse import urlparse

from database import Geek_blog


class PostsParser:
    _headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:81.0) Gecko/20100101 Firefox/81.0',
    }

    def __init__(self, start_url: str):
        self.start_url = start_url
        _url = urlparse(start_url)
        self.start_website_url = f'{_url.scheme}://{_url.hostname}'
        self.db_blog = Geek_blog()

    def _get_soup(self, url_for_pars: str) -> BeautifulSoup:
        response = requests.get(url_for_pars, headers=self._headers)
        return BeautifulSoup(response.text, 'lxml')

    def _get_comment(self, comments_json: list, comments_list: list) -> None:
        for comment in comments_json:
            comment_data = comment['comment']
            comments_list.append({'id': comment_data['id'],
                                  'author_name': comment_data['user']['full_name'],
                                  'author_url': comment_data['user']['url'],
                                  'comment_text': comment_data['body']})
            if len(comment_data['children']) > 0:
                self._get_comment(comment_data['children'], comments_list)

    def _parse_post(self, url_post: str) -> None:
        page_data = {
            'page_url': url_post,
            'page_title': None,
            'img_url': None,
            'publication_date': None,
            'author_name': None,
            'author_url': None
        }
        soup = self._get_soup(url_post)
        page_data['page_title'] = soup.h1.text
        page_data['img_url'] = soup.img.attrs['src']
        page_data['publication_date'] = datetime.fromisoformat(soup.time.attrs['datetime'])
        author = soup.find('div', attrs={'itemprop': 'author'})
        page_data['author_name'] = author.text
        page_data['author_url'] = f'{self.start_website_url}{author.parent.attrs["href"]}'

        tags = soup.find_all('a', attrs={'class': 'small'})
        tags_list = []
        for tag in tags:
            tags_list.append({'name': tag.text,
                              'url': f'{self.start_website_url}{tag.attrs["href"]}'})

        comments = soup.comments
        params = {
            'commentable_type': comments.attrs['commentable-type'],  # 'Post',
            'commentable_id': comments.attrs['commentable-id'],
            'order': 'desc',
        }
        response = requests.get('https://geekbrains.ru/api/v2/comments', headers=self._headers, params=params)
        comments_json = response.json()
        comments_list = []
        if len(comments_json) > 0:
            self._get_comment(comments_json, comments_list)

        self.db_blog.save_to_db(page_data, tags_list, comments_list)

    def _get_page_max(self, start_page):
        pagination = start_page.find('ul', attrs={'class': "gb__pagination"})
        li_list = pagination.find_all('a')
        page_max = 0
        for li in li_list:
            if li.text.isdigit():
                page_max = int(li.text)
        return page_max

    def parse(self) -> None:
        soup = self._get_soup(self.start_url)
        page_max = self._get_page_max(soup)

        for page_num in range(1, page_max+1):
            if page_num > 1:
                soup = self._get_soup(f"{self.start_url}?page={page_num}")

            post_items = soup.find('div', attrs={'class': "post-items-wrapper"})
            posts = post_items.findChildren('div', attrs={'class': 'post-item event'})
            for post in posts:
                self._parse_post(f'{self.start_website_url}{post.find("a").attrs["href"]}')


if __name__ == '__main__':
    url = 'https://geekbrains.ru/posts'
    parser = PostsParser(url)
    parser.parse()