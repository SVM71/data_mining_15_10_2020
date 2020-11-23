import scrapy
from ..loaders import VacancyLoader, EmployerLoader

# Источник https://hh.ru/search/vacancy?schedule=remote&L_profession_id=0&area=113
# вакансии удаленной работы.
# Задача: Обойти с точки входа все вакансии и собрать след данные:
#     1. название вакансии
#     2. оклад (строкой от до или просто сумма)
#     3. Описание вакансии
#     4. ключевые навыки - в виде списка названий
#     5. ссылка на автора вакансии
# Перейти на страницу автора вакансии,
# собрать данные:
#     1. Название
#     2. сайт ссылка (если есть)
#     3. сферы деятельности (списком)
#     4. Описание
# Обойти и собрать все вакансии данного автора.
# Обязательно использовать Loader Items Pipelines


class TltHhSpider(scrapy.Spider):

    name = 'tlt_hh'

    allowed_domains = ['togliatti.hh.ru']

    start_urls = ['https://togliatti.hh.ru/search/vacancy?schedule=remote&L_profession_id=0&area=113']

    xpath = {
        'vacancy_urls':'//a[@data-qa="vacancy-serp__vacancy-title"]/@href',
        'pagination':'//div[@data-qa="pager-block"]//a[@data-qa="pager-page"]/@href'
    }

    vacancy_xpath = {
        'vac_name':'//h1[@data-qa="vacancy-title"]/text()',
        'salary':'//p[@class="vacancy-salary"]/span[@data-qa="bloko-header-2"]//text()',
        'vac_info':'//div[@data-qa="vacancy-description"]//text()',
        'key_skills': '//div[@class="bloko-tag-list"]//span[@data-qa="bloko-tag__text"]//text()',
        'employer_url':'//a[@data-qa="vacancy-company-name"]/@href',
    }

    employer_xpath = {
        'emp_name' : '//span[@data-qa="company-header-title-name"]/text()',
        'url':'',
        'area_of_activity' : '//div[@class="employer-sidebar-content"]//div[@class="employer-sidebar-block__header"]/text()',
        'emp_description' : '//div[@class="g-user-content"]//text()',
    }

    employer_vaca_list = []

    def parse(self, response):
        pages = response.xpath(self.xpath['pagination'])
        for page in pages:
            yield response.follow(page, callback=self.parse)
        vacancys = response.xpath(self.xpath['vacancy_urls'])
        for vac_url in vacancys:
            yield response.follow(vac_url, callback=self.vacancy_parse)


    def vacancy_parse(self, response):
        loader = VacancyLoader(response=response)
        for key, val in self.vacancy_xpath.items():
            loader.add_xpath(key, val)
        yield loader.load_item()

        emp_url_path = response.xpath(self.vacancy_xpath['employer_url']).get()
        yield response.follow( emp_url_path, callback=self.company_parse )


    def company_parse(self, response):
        loader = EmployerLoader(response=response)
        for key, val in self.employer_xpath.items():
            if key == 'url':
                loader.add_value(key, response.url)
            else:
                loader.add_xpath(key, val)
        # Обойти и собрать все вакансии данного автора.
        emp_vaca_path = response.xpath('//a[@data-qa="employer-page__employer-vacancies-link"]/@href').get()
        yield response.follow( emp_vaca_path, callback=self.get_company_vaca_urls)
        loader.add_value( 'emp_vacancy_offer', self.employer_vaca_list )
        yield loader.load_item()

    def get_company_vaca_urls(self, response):
        self.employer_vaca_list = response.xpath('//div[@class="vacancy-serp"]//a[@data-qa="vacancy-serp__vacancy-title"]/@href').getall()
