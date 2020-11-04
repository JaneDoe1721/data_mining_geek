import scrapy
from ..loaders import YoulaAutoLoader


class YoulaSpider(scrapy.Spider):
    name = 'youla'
    allowed_domains = ['auto.youla.ru']
    start_urls = ['https://auto.youla.ru/']

    xpath = {
        'brands': '//div[@class="TransportMainFilters_brandsList__2tIkv"]//a[@class="blackLink"]/@href',
        'ads': '//div[@id="serp"]//article//a[@data-target="serp-snippet-title"]/@href',
        'pagination': '//div[contains(@class, "Paginator_block")]/a/@href',
    }

    def parse(self, response, **kwargs):
        for url in response.xpath(self.xpath['brands']):
            yield response.follow(url, callback=self.brand_parse)

    def brand_parse(self, response, **kwargs):
        for url in response.xpath(self.xpath['pagination']):
            yield response.follow(url, callback=self.brand_parse)

        for url in response.xpath(self.xpath['ads']):
            yield response.follow(url, callback=self.ads_parse)

    def ads_parse(self, response, **kwargs):
        loader = YoulaAutoLoader(response=response)
        loader.add_xpath('title', '//div[contains(@class, "AdvertCard_advertTitle")]/text()')
        loader.add_xpath('img', '//div[contains(@class, "PhotoGallery_block")]//img/@src')
        loader.add_xpath('price', '//div[contains(@class, "AdvertCard_priceBlock")]/div/text()')
        loader.add_xpath('description', '//div[contains(@class, "AdvertCard_description")]/div[contains(@class, "dvertCard_descriptionInner")]/text()' )
        loader.add_xpath('name', '//script[contains(text(), "window.transitState =")]/text()')
        loader.add_xpath('phone', '//script[contains(text(), "window.transitState =")]/text()')
        loader.add_xpath('characteristic', '/div[contains(@class, "AdvertCard_specs")]//div[contains(@class, "AdvertSpecs")]')
        loader.add_value('url', response.url)
        yield loader.load_item()