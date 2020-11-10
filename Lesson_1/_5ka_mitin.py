import json
import asyncio
import requests
from collections import namedtuple


class c_category_lst_5ka:
    __url_categories = 'https://5ka.ru/api/v2/categories/'
    c_tuple_id_name = namedtuple('c_categ', ['id', 'name'])

    def __init__(self):
        self.categ = []
        self.categ_dict = {}
        # заполняем переменные...
        self.__parce_category_list()

    def __parce_category_list(self):
        req_categories = requests.get(self.__url_categories)
        categories_lst = json.loads(req_categories.text)
        for ctg in categories_lst:
            self.categ.append(self.c_tuple_id_name(ctg['parent_group_code'], ctg['parent_group_name']))
        for id, name in self.categ:
            self.categ_dict[id] = name

    def get_5ka_category_lst(self):
        return self.categ

    def get_category_name_by_id(self, ctg_id):
        return self.categ_dict[ctg_id]


# cat5ka_obj = c_category_lst_5ka()
# for id, name in cat5ka_obj.get_5ka_category_lst():
#     print ( id, name, cat5ka_obj.get_category_name_by_id(id) )

class c_price_string_parcer:
    ''' парсер для разбора строки о товаре отданной сайтом 5ка в json или формат удобный для чтения
        ид: 23939, наименование: 'ЧАЙКОФСКИЙ Сахар бел.кусковой 250г', цена:19.99...22.99 руб.
    '''

    def __init__(self, inp_json, categ_str = ''):
        self.str_json_obj = {
            'category': categ_str, 'id': 0, 'name': '',
            'promo': {'date_begin': '', 'date_end': '', 'expired_at': 0, },
            'current_prices': {'price_reg__min': 0.0, 'price_promo__min': 0.0}
        }
        self.__convert_inp_json(inp_json)

    def __convert_inp_json(self, inp_json):
        for el in self.str_json_obj.keys():
            if el == 'category':
                continue
            if type(self.str_json_obj[el]) is not type({}):
                self.str_json_obj[el] = inp_json[el]
            else:
                for dict_el in self.str_json_obj[el].keys():
                    self.str_json_obj[el][dict_el] = inp_json[el][dict_el]

    def get_human_readble_str(self):
        str2_wr = f"категория: {self.str_json_obj['category']},  ид: {self.str_json_obj['id']}, наим: '{self.str_json_obj['name']}'," \
                  f" цена:{self.str_json_obj['current_prices']['price_promo__min']}...{self.str_json_obj['current_prices']['price_reg__min']} руб."
        return str2_wr

    def get_json(self):
        return self.str_json_obj


class Parser5ka:
    __params = {
        'records_per_page': 50,
        'categories': 902,
    }
    __headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:81.0) Gecko/20100101 Firefox/81.0',
    }
    # задержка между запросами, сек
    __time_delay = 0.02

    def __init__(self, start_url):
        self.start_url = start_url
        self.categ_obj = c_category_lst_5ka()

    async def parse(self, url=None):
        for categ in self.categ_obj.categ_dict.keys():
            if url is None:
                url = self.start_url
            params = self.__params
            params['categories'] = categ
            #print(f' categ: {categ}, name: {self.categ_obj.get_category_name_by_id(categ)}, url: {url}' )
            with open(f'category_{categ}.json', 'w', encoding='UTF-8') as file:
                while url:
                    await asyncio.sleep(self.__time_delay)
                    response = requests.get(url, params=params, headers=self.__headers)
                    if params:
                        params = {}
                    data: dict = response.json()
                    url = data['next']
                    for product in data['results']:
                        str_parcer = c_price_string_parcer(product, self.categ_obj.get_category_name_by_id(categ))
                        json.dump(str_parcer.get_json(), file, ensure_ascii=False)
                        #print(str_parcer.get_human_readble_str())

if __name__ == '__main__':
    parser = Parser5ka('https://5ka.ru/api/v2/special_offers/')
    loop = asyncio.get_event_loop()
    loop.run_until_complete(parser.parse())
    loop.close()

