import scrapy
import json
import datetime as dt

from ..items import PostInsta, TagInsta, UserInsta, SubscribersInsta


class InstagramSpider(scrapy.Spider):
    name = 'instagram'
    allowed_domains = ['www.instagram.com']
    start_urls = ['https://www.instagram.com/']
    login_url = 'https://www.instagram.com/accounts/login/ajax/'

    api_tag_url = '/graphql/query/'

    query_hash_tag = '9b498c08113f1e09617a1703c22b2f32'
    query_hash_post = '56a7068fea504063273cc2120ffd54f3'
    query_hash_following = 'd04b0a864b4b54837c0d870b0e77e076'
    query_hash_followers = 'c76146de99bb02f6415203be841dd25a'

    def __init__(self, login, enc_password, *args, **kwargs):
        self.tags = ['python', 'mongodb', 'brazil', 'mercedes']
        self.user = ['tammyhembrow']
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
                for user in self.user:
                    yield response.follow(f'/{user}/', callback=self.user_parse)

    def tag_parse(self, response, **kwargs):
        tag = self.js_data_extract(response)['entry_data']['TagPage'][0]['graphql']['hashtag']

        yield TagInsta(
            date_parse=dt.datetime.utcnow(),
            data={
                'id': tag['id'],
                'name': tag['name'],
                'profile_pic_url': tag['profile_pic_url'],
            }
        )
        yield from self.tag_posts(tag, response)

    def tag_posts(self, tag, response):
        if tag['edge_hashtag_to_media']['page_info']['has_next_page']:
            variables = {
                'tag_name': tag['name'],
                'first': 50,
                'after': tag['edge_hashtag_to_media']['page_info']['end_cursor'],
            }
            url = f'{self.api_tag_url}?query_hash={self.query_hash_tag}&variables={json.dumps(variables)}'
            yield response.follow(url, callback=self.api_parse)

        yield from self.posts_parse(tag)

    def api_parse(self, response):
        yield from self.tag_posts(response.json()['data']['hashtag'], response)

    @staticmethod
    def posts_parse(tag):
        edges = tag['edge_hashtag_to_media']['edges']
        for node in edges:
            yield PostInsta(
                date_parse=dt.datetime.utcnow(),
                data=node['node']
            )

    @staticmethod
    def js_data_extract(response):
        script = response.xpath('//script[contains(text(), "window._sharedData =")]/text()').get()
        return json.loads(script.replace("window._sharedData =", '')[:-1])

    def user_parse(self, response, **kwargs):
        user_data = self.js_data_extract(response)['entry_data']['ProfilePage'][0]['graphql']['user']
        yield UserInsta(
            date_parse=dt.datetime.utcnow(),
            data=user_data,
        )
        yield from self.follow_request(response, user_data)

    def follow_request(self, response, user_data, variables=None):
        if not variables:
            variables = {
                'id': user_data['id'],
                'first': 50,
            }
        api_url = f'{self.api_tag_url}?query_hash={self.query_hash_following}&variables={json.dumps(variables)}'
        yield response.follow(api_url, callback=self.following_followers_parse, cb_kwargs={'user_data': user_data})

    def following_followers_parse(self, response, user_data):
        print(1)
        if b'application/json' in response.headers['Content-Type']:
            print(1)
            full_data = response.json()
            yield from self.following_item(user_data, full_data['data']['user']['edge_follow']['edges'])
            if full_data['data']['user']['edge_follow']['page_info']['has_next_page']:
                variables = {
                    'id': user_data['id'],
                    'first': 50,
                    'after': full_data['data']['user']['edge_follow']['page_info']['end_cursor'],
                }
                yield from self.follow_request(response, user_data, variables)

    def following_item(self, user_data, follow_users):
        for user in follow_users:
            yield SubscribersInsta(
                date_parse=dt.datetime.utcnow(),
                user_id=user_data['id'],
                user_name=user_data['username'],
                follow_id=user['node']['id'],
                follow_name=user['node']['username']
            )
            yield UserInsta(
                date_parse=dt.datetime.utcnow(),
                data=user['node']
            )