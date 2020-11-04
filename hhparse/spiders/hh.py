import scrapy
from ..loader import HhparseItem, HeadHunterCompanies


class HhSpider(scrapy.Spider):
    name = 'hh'
    allowed_domains = ['klin.hh.ru']
    start_urls = ['https://klin.hh.ru/search/vacancy?schedule=remote&L_profession_id=0&area=113']
    compain_url = 'https://klin.hh.ru/'

    xpath = {
        'vacancy': '//div[@class="vacancy-serp"]//a[contains(@class, "HH-LinkModifier")]/@href',
        'pagination': '//div[contains(@class, "bloko-gap")]//a[contains(@class, "HH-Pager-Controls-Next")]/@href',
        'company_vacancies': '//div[@class="employer-sidebar-content"]/div[@class="employer-sidebar-block"]/a/@href',
    }

    def parse(self, response, **kwargs):
        for url in response.xpath(self.xpath['pagination']):
            yield response.follow(url, callback=self.parse)

        for url in response.xpath(self.xpath['vacancy']):
            yield response.follow(url, callback=self.vacancy_parse)

    def vacancy_parse(self, response, **kwargs):
        loader = HhparseItem(response=response)
        loader.add_value('url', response.url)
        loader.add_xpath('title', '//h1[contains(@class, "bloko-header-1")]/text()')
        loader.add_xpath('salary', '//p[contains(@class, "vacancy-salary")]/span/text()')
        loader.add_xpath('description', '//div[@class="vacancy-section"]/div[@class="g-user-content"]//text()')
        loader.add_xpath('skills', '//div[@class="bloko-tag-list"]/div//span/text()')
        loader.add_xpath('author', '//div[contains(@class, "vacancy-company")]/a/@href')
        yield loader.load_item()

        for url in response.xpath('//div[contains(@class, "vacancy-company")]/a/@href'):
            yield response.follow(url, callback=self.company_parse)

    def company_parse(self, response, **kwargs):
        loader = HeadHunterCompanies(response=response)
        loader.add_value('url', response.url)
        loader.add_xpath('title', '//div[@class="employer-sidebar-header"]//span//text()')
        loader.add_xpath('company_adress', '//div[@class="employer-sidebar-content"]/a/@href')
        loader.add_xpath('field_of_activity', '//div[@class="employer-sidebar-block"]/p/text()')
        loader.add_xpath('description', '//div[@class="company-description"]/div[@class="g-user-content"]//text()')
        yield loader.load_item()

        for url in response.xpath(self.xpath['company_vacancies']):
            yield response.follow(url, callback=self.parse)