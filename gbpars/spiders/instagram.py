import scrapy
import json
import datetime as dt

from ..loaders import InstagramTagLoader, InstagramPostLoader


class InstagramSpider(scrapy.Spider):
    name = 'instagram'
    allowed_domains = ['www.instagram.com']
    start_urls = ['https://www.instagram.com/']
    login_url = 'https://www.instagram.com/accounts/login/ajax/'

    api_tag_url = '/graphql/query/'
    query_hash_tag = '9b498c08113f1e09617a1703c22b2f32'
    query_hash_post = '56a7068fea504063273cc2120ffd54f3'

    def __init__(self, login, enc_password, *args, **kwargs):
        self.tags = ['python', 'mongodb', 'brazil', 'mercedes']
        self.login = login
        self.enc_password = enc_password
        super().__init__(*args, **kwargs)

    def parse(self, response, **kwargs):
        try:
            js_data = self.js_data_extract(response)
            yield scrapy.FormRequest(
                self.login_url,
                method='POST',
                callback=self.parse,
                formdata={
                    'username': self.login,
                    'enc_password': self.enc_password,
                },
                headers={'X-CSRFToken': js_data['config']['csrf_token']}
            )
        except AttributeError as e:
            if response.json().get('authenticated'):
                for tag in self.tags:
                    yield response.follow(f'/explore/tags/{tag}/', callback=self.tag_parse)

    def tag_parse(self, response, **kwargs):
        tag = self.js_data_extract(response)['entry_data']['TagPage'][0]['graphql']['hashtag']

        loader = InstagramTagLoader(response=response)
        loader.add_value('date_parse', dt.datetime.now())
        loader.add_value('data', tag)
        loader.add_value('img', tag['profile_pic_url'])
        yield loader.load_item()

        for post in self.tag_posts(response, tag):
            yield post

    def tag_posts(self, response, tag,):
        if tag['edge_hashtag_to_media']['page_info']['has_next_page']:
            variables = {
                'tag_name': tag['name'],
                'first': 50,
                'after': tag['edge_hashtag_to_media']['page_info']['end_cursor'],
            }
            url = f'{self.api_tag_url}?query_hash={self.query_hash_tag}&variables={json.dumps(variables)}'
            yield response.follow(url, callback=self.api_parse)

        for post in self.posts_parse(response, tag):
            yield post

    def api_parse(self, response):
        hashtag = response.json()['data']['hashtag']
        for post in self.tag_posts(response, hashtag):
            yield post

    @staticmethod
    def posts_parse(response, tag):
        for post in tag['edge_hashtag_to_media']['edges']:
            loader = InstagramPostLoader(response=response)
            loader.add_value('date_parse', dt.datetime.now())
            loader.add_value('data', post['node'])
            loader.add_value('img', post['node']['display_url'])
            yield loader.load_item()

    @staticmethod
    def js_data_extract(response):
        script = response.xpath('//script[contains(text(), "window._sharedData =")]/text()').get()
        return json.loads(script.replace("window._sharedData =", '')[:-1])

