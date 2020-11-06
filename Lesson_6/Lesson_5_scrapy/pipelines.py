# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
from itemadapter import ItemAdapter
from pymongo import MongoClient
from scrapy.pipelines.images import ImagesPipeline
from scrapy import Request

class Lesson5ScrapyPipeline:
    def __init__(self):
        client = MongoClient()
        self.db = client['parse_20']
        pass

    def process_item(self, item, spider):
        item_name = type(item).__name__
        print( f' Lesson5ScrapyPipeline => process_item with type_name:  \'{item_name}\'')
        connection = self.db[item_name]
        connection.insert_one(item)
        return item


class Lesson5ScrapyImagePipeline(ImagesPipeline):


    def get_media_requests(self, item, info):
        images = item.get('img', item['data'].get('profile_pic_url', item['data'].get('display_url', [])))
        if not isinstance(images, list):
            images = [images]
        for url in images:
            try:
                yield Request(url)
            except Exception as err:
                print(err)

    def item_completed(self, results, item, info):
        try:
            item['img'] = [itm[1] for itm in results if itm[0]]
        except KeyError:
            pass
