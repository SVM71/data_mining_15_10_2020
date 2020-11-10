# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
from itemadapter import ItemAdapter
from pymongo import MongoClient


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
