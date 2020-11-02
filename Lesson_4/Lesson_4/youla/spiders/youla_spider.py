import scrapy
from pymongo import MongoClient
import re
# Источник https://auto.youla.ru/
# Обойти все марки авто и зайти на странички объявлений
# Собрать след стуркутру и сохранить в БД Монго
#     Название объявления
#     Список фото объявления (ссылки)
#     Список характеристик
#     Описание объявления
#     ссылка на автора объявления
# дополнительно попробуйте вытащить телефона

def Convert(lst):
    res_dct = {lst[i]: lst[i + 1] for i in range(0, len(lst), 2)}
    return res_dct

class YoulaSpider(scrapy.Spider):
    name = 'youla'
    allowed_domains = ['youla.ru']
    start_urls = ['https://auto.youla.ru/']
    xpath = {
        'brands': '//div[@class="TransportMainFilters_brandsList__2tIkv"]//a[@class="blackLink"]/@href',
        'ads': '//div[@id="serp"]//article//a[@data-target="serp-snippet-title"]/@href',
        'pagination': '//div[contains(@class, "Paginator_block")]/a/@href',
    }
    db_client = MongoClient()

    def parse(self, response, **kwargs):
        urls = response.xpath(self.xpath['brands'])
        for url in urls:
            yield response.follow(url, callback=self.brand_parse)

    def brand_parse(self, response, **kwargs):
        urls = response.xpath(self.xpath['pagination'])
        for url in urls:
            yield response.follow(url, callback=self.brand_parse)

        adsurls = response.xpath(self.xpath['ads'])
        for adsurl in adsurls:
            yield response.follow(adsurl, callback=self.ads_parse)

    def ads_parse(self, response, **kwargs):
        name = response.xpath('//div[contains(@class, "AdvertCard_advertTitle")]/text()').extract_first()
        images = response.xpath('//figure[contains(@class, "PhotoGallery_photo")]/picture/img/@src').extract()
        features = Convert(response.xpath('//div[contains(@class, "AdvertSpecs_row")]//text()').extract())
        description = response.xpath('//div[contains(@class, "AdvertCard_descriptionInner")]/text()').extract_first()
        script = response.xpath('//script[contains(text(), "window.transitState =")]/text()').get()
        re_str = re.compile(r"youlaId%22%2C%22([0-9a-zA-Z]+)%22%2C%22avatar")
        user = re.search(re_str, script).group(1)
        user_url = f'https://youla.ru/user/{user}' if user else None
        dict = {
            'name': name,
            'images': images,
            'features': features,
            'description': description,
            'user_url': user_url,
        }
        # сохраняем в БД
        collection = self.db_client["parse_10"][self.name]
        collection.insert_one(dict)
        # print(1)


#<GET https://auto.youla.ru/samara/cars/used/ac/>
#a = response.css('.TransportMainFilters_brandsList__2tIkv a.blackLink')
#a[0].attrib['href']

# a = response.xpath('//div[@class="TransportMainFilters_brandsList__2tIkv"]//a[@class="blackLink"]/@href')
# a[0]
# <Selector xpath='//div[@class="TransportMainFilters_brandsList__2tIkv"]//a[@class="blackLink"]/@href' data='/samara/cars/used/ac/'>

#######
# aa =  response.xpath('//div[@id="serp"]//article//a[@data-target="serp-snippet-title"]/@href')
#       response.xpath('//div[@id="serp"]//a[contains(@class, "titleText")]/@href')
#a = response.xpath('//div[@id="serp"]//article//a[contains(text(), "titleText")]/@href')

# SerpSnippet_name__3F7Yu SerpSnippet_titleText__1Ex8A blackLink

# response.xpath('//div[contains(@class, "AdvertCard_advertTitle")]/text()').extract_first()
#.estract() - список строк
# для последнего можно ...)[-1].extract()
# 'УАЗ 452 3909 2 поколение, минивэн 4 дв.'
# https://youla.ru/user/5dc0f86ec6ab9e37ab6cde02?_ga=2.237274240.1404697604.1604149666-2029101521.1604149666
