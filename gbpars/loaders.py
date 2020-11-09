import re
import base64
from scrapy import Selector
from itemloaders.processors import TakeFirst, MapCompose
from scrapy.loader import ItemLoader

from .items import YoulaAutoItem


def search_author_id(itm):
    re_str = re.compile(r'youlaId%22%2C%22([0-9a-zA-Z]+)%22%2C%22avatar')
    result = re.findall(re_str, itm)
    return result


def create_user_url(itm):
    base_url = "htpps://youla.ru/user/"
    result = base_url + itm
    return result


def get_characteristic(itm):
    tag = Selector(text=itm)
    return {tag.xpath('//div/div[1]/text()').get(): tag.xpath('//div/div[2]/text()').get() or tag.xpath('//div/div[2]/a/text()').get()}


def get_characteristic_out(itms):
    result = {}
    for itm in itms:
        if None not in itm:
            result.update(itm)
    return result


def search_phone(itm):
    regex = re.compile(r'phone%22%2C%22([0-9|a-zA-Z]+)%3D%3D%22%2C%22time')
    trapped = re.findall(regex, itm)
    number = trapped[0] + '=='
    str_base64 = base64.b64decode(number)
    phone_number = base64.b64decode(str_base64)
    phone = phone_number.decode('utf-8')
    return phone


class YoulaAutoLoader(ItemLoader):
    default_item_class = YoulaAutoItem
    name_in = MapCompose(search_author_id, create_user_url)
    name_out = TakeFirst()
    title_out = TakeFirst()
    characteristic_in = MapCompose(get_characteristic)
    characteristic_out = get_characteristic_out
    url_out = TakeFirst()
    price_out = TakeFirst()
    description = TakeFirst()
    phone_in = MapCompose(search_phone)
    phone_out = TakeFirst()


