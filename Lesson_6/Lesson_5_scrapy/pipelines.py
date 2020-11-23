# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
from itemadapter import ItemAdapter
from pymongo import MongoClient
from scrapy.pipelines.images import ImagesPipeline
from scrapy import Request
import json
from scrapy.exporters import PythonItemExporter


class Lesson5ScrapyPipeline:

    def __init__(self):
        # client = MongoClient()
        # self.db = client['parse_20']
        self.f = open("insta_images.json", "w+", encoding='utf-8')
#        self.f = open("insta_user_and_follows.json", "w+", encoding='utf-8')

    def __del__(self):
        self.f.close()

    def _get_exporter(self, **kwargs):
        return PythonItemExporter(binary=False, **kwargs)

    def process_item(self, item, spider):
        item_name = type(item).__name__
        print( f' Lesson5ScrapyPipeline => process_item with type_name:  \'{item_name}\'')
        # connection = self.db[item_name]
        # connection.insert_one(item)
        ie = self._get_exporter()
        exported = ie.export_item(item)
        #print(json.dumps(exported))
        try:
            self.f.write(json.dumps(exported))
        except IOError as err:
            print(f"Outpur to insta_images.json ERROR: {err}")
        return item


class Lesson5ScrapyImagePipeline(ImagesPipeline):

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
            except Exception as err:
                print(err)

    def item_completed(self, results, item, info):
        try:
            item['img'] = [itm[1] for itm in results if itm[0]]
        except KeyError:
            pass
        return item