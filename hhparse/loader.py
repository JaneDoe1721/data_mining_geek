from itemloaders.processors import TakeFirst, MapCompose
from scrapy.loader import ItemLoader
from .items import HhparseItem, HeadHunterCompanies


def create_author_url(itm):
    result = f'https://klin.hh.ru{itm[0]}'
    return result


def symbol_delete(itm):
    result = itm.replace('\xa0', '')
    return result


def string_concat(itm):
    result = ' '.join(itm)
    return symbol_delete(result)


class HeadHunterJobsLoader(ItemLoader):
    default_item_class = HhparseItem
    url_out = TakeFirst()
    title_out = TakeFirst()
    salary_in = string_concat
    salary_out = TakeFirst()
    description_in = string_concat
    description_out = TakeFirst()
    skills_out = MapCompose(symbol_delete)
    author_in = create_author_url
    author_out = TakeFirst()


class HeadHunterCompaniesLoader(ItemLoader):
    default_item_class = HeadHunterCompanies
    url_out = TakeFirst()
    title_in = string_concat
    title_out = TakeFirst()
    company_adress_out = TakeFirst()
    field_of_activity_out = MapCompose(symbol_delete)
    description_in = string_concat
    description_out = TakeFirst()