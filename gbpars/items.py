# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class GbparsItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    pass


class Insta(scrapy.Item):
    _id = scrapy.Field()
    date_parse = scrapy.Field()
    data = scrapy.Field()
    img = scrapy.Field()


class TagInsta(Insta):
    pass


class PostInsta(Insta):
    pass


class YoulaAutoItem(scrapy.Item):
    _id = scrapy.Field()
    title = scrapy.Field()
    img = scrapy.Field()
    url = scrapy.Field()
    characteristic = scrapy.Field()
    price = scrapy.Field()
    description = scrapy.Field()
    name = scrapy.Field()
    phone = scrapy.Field()
