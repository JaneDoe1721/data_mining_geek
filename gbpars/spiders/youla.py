import scrapy
from pymongo import MongoClient
import requests


class YoulaSpider(scrapy.Spider):
    name = 'youla'
    allowed_domains = ['auto.youla.ru']
    start_urls = ['https://auto.youla.ru/']
    autor_url = 'https://auto.youla.ru/api/get-youla-profile/'
    xpath = {
        'brands': '//div[@class="TransportMainFilters_brandsList__2tIkv"]//a[@class="blackLink"]/@href',
        'ads': '//div[@id="serp"]//article//a[@data-target="serp-snippet-title"]/@href',
        'pagination': '//div[contains(@class, "Paginator_block")]/a/@href',
    }
    db_client = MongoClient()

    def parse(self, response, **kwargs):
        for url in response.xpath(self.xpath['brands']):
            yield response.follow(url, callback=self.brand_parse)

    def brand_parse(self, response, **kwargs):
        for url in response.xpath(self.xpath['pagination']):
            yield response.follow(url, callback=self.brand_parse)

        for url in response.xpath(self.xpath['ads']):
            yield response.follow(url, callback=self.ads_parse)

    def ads_parse(self, response, **kwargs):

        name = response.xpath('//div[contains(@class, "AdvertCard_advertTitle")]/text()').extract_first()
        images = response.xpath('//div[contains(@class, "PhotoGallery_block")]//img/@src').extract()

        keys = response.xpath('//div[contains(@class, "AdvertSpecs_label")]/text()').extract()
        values = response.xpath(
            '//div[contains(@class, "AdvertSpecs_data")]/a/text() | //div[contains(@class, "AdvertSpecs_data")]/text()').extract()
        specifications = dict(zip(keys, values))

        price = response.xpath('//div[contains(@class, "AdvertCard_priceBlock")]/div/text()').get()
        description = response.xpath(
            '//div[contains(@class, "AdvertCard_description")]/div[contains(@class, "dvertCard_descriptionInner")]/text()').get()

        autor_name = self.autor_url
        print(1)

        collection = self.db_client['parse_10'][self.name]
        collection.insert_one({
            'title': name,
            'img': images,
            'characteristic': specifications,
            'price': price,
            'description': description,

        })