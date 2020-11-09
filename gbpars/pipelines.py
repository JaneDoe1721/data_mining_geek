# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
from itemadapter import ItemAdapter
from scrapy import Request
from scrapy.pipelines.images import ImagesPipeline
from pymongo import MongoClient


class GbparsPipeline:

    def __init__(self):
        client = MongoClient()
        self.db = client['parse_10']

    def process_item(self, item, spider):
        collection = self.db[type(item).__name__]
        collection.insert_one(item)
        return item


class GbparsImagesPipeline(ImagesPipeline):

    def get_media_requests(self, item, info):
        images = item.get('img',
                          item.get('data', {}).get('profile_pic_url',
                                                   item.get('data', {}).get('display_url',
                                                                            []
                                                                            )
                                                   )
                          )
        if not isinstance(images, list):
            images = [images]
        for url in images:
            try:
                yield Request(url)
            except Exception as e:
                print(e)

    def item_completed(self, results, item, info):
        try:
            item['img'] = [itm[1] for itm in results if itm[0]]
        except KeyError:
            pass
        return item