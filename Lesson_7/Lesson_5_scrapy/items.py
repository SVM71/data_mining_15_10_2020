# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy

# Dакансиz данные:
#     1. название вакансии
#     2. оклад (строкой от до или просто сумма)
#     3. Описание вакансии
#     4. ключевые навыки - в виде списка названий
#     5. ссылка на автора вакансии
class VacancyItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    _id = scrapy.Field()
    vac_name = scrapy.Field()
    salary = scrapy.Field()
    vac_info = scrapy.Field()
    key_skills = scrapy.Field()
    employer_url = scrapy.Field()


# Работодатель данные:
#     1. Название
#     2. сайт ссылка (если есть)
#     3. сферы деятельности (списком)
#     4. Описание
class EmployerItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    _id = scrapy.Field()
    emp_name = scrapy.Field()
    url = scrapy.Field()
    area_of_activity = scrapy.Field()
    emp_description = scrapy.Field()
    emp_vacancy_offer = scrapy.Field()


class InstaItem(scrapy.Item):
    _id = scrapy.Field()
    date_parse = scrapy.Field()
    data = scrapy.Field()
    img = scrapy.Field()

class InstaTag(InstaItem):
    pass

class InstaPost(InstaItem):
    pass

class InstaUser(InstaItem):
    pass

class InstaFollow(scrapy.Item):
    _id = scrapy.Field()
    date_parse = scrapy.Field()
    user_name = scrapy.Field()
    user_id = scrapy.Field()
    follow_name = scrapy.Field()
    follow_id = scrapy.Field()
