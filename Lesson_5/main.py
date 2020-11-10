from scrapy.crawler import CrawlerProcess
from scrapy.settings import Settings

from Lesson_5_scrapy import settings
from Lesson_5_scrapy.spiders.tlt_hh import TltHhSpider

if __name__ == '__main__':
    crawl_settings = Settings()
    crawl_settings.setmodule(settings)
    crawl_proc = CrawlerProcess(settings=crawl_settings)
    crawl_proc.crawl(TltHhSpider)
    crawl_proc.start()





