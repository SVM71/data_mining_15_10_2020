# процесс управляет пауками
from scrapy.crawler import CrawlerProcess
from scrapy.settings import Settings

from avito import settings
from avito.spiders.avito_spider import YoulaSpider

if __name__ == '__main__':
    crawl_settings = Settings()
    crawl_settings.setmodule(settings)
    crawl_proc = CrawlerProcess(settings=crawl_settings)
    crawl_proc.crawl(YoulaSpider)
    crawl_proc.start()
