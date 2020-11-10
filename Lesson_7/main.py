import os
from scrapy.crawler import CrawlerProcess
from scrapy.settings import Settings

from Lesson_5_scrapy import settings
from Lesson_5_scrapy.spiders.tlt_hh import TltHhSpider
from Lesson_5_scrapy.spiders.inst_spider import InstSpider

from dotenv import load_dotenv
load_dotenv('Lesson_5_scrapy/.env')

import json
if __name__ == '__main__':
############################
    crawl_settings = Settings()
    crawl_settings.setmodule(settings)
    crawl_proc = CrawlerProcess(settings=crawl_settings)
    crawl_proc.crawl(InstSpider, login=os.getenv('USRNAME'), passwd=os.getenv('ENC_PASSWORD'))
    crawl_proc.start()





