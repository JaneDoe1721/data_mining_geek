import scrapy
from pymongo import MongoClient
import base64
import re
from urllib.parse import unquote


class YoulaSpider(scrapy.Spider):
    name = 'youla'
    allowed_domains = ['auto.youla.ru']
    start_urls = ['https://auto.youla.ru/']

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

    def decoder(self, response, **kwargs):
        regex = re.compile(r'phone%22%2C%22([0-9|a-zA-Z]+)%3D%3D%22%2C%22time')
        trapped = re.findall(regex, response.text)
        number = trapped[0] + '=='
        str_base64 = base64.b64decode(number)
        phone_number = base64.b64decode(str_base64)

        find_script = response.xpath('//script[contains(text(), "window.transitState =")]/text()').get()
        find_owner_id = re.compile(r"youlaId%22%2C%22([0-9a-zA-Z]+)%22%2C%22avatar")
        find_dealer_id = re.compile("page%22%2C%22(https%3A%2F%2Fam.ru%2Fcardealers%2F[0-9a-zA-Z\S]+%2F%23info)"
                                    "%22%2C%22salePointLogo")
        person = re.findall(find_owner_id, find_script)
        dealer = re.findall(find_dealer_id, find_script)
        autor = f'https://youla.ru/user/{person[0]}' if person else unquote(dealer[0])
        return autor, phone_number

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

        autor, phone_number = self.decoder(response)
        phone = phone_number.decode('utf-8')
        print(1)

        collection = self.db_client['parse_10'][self.name]
        collection.insert_one({
            'title': name,
            'img': images,
            'characteristic': specifications,
            'price': price,
            'description': description,
            'name': autor,
            'phone': phone,

        })