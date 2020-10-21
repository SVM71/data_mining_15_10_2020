from bs4 import BeautifulSoup
import requests
from urllib import parse
from pymongo import MongoClient

class magnit_parcer:
    __headers = { 'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:81.0) Gecko/20100101 Firefox/81.0' }
    __params = { 'geo' : 'moskva' }

    def __init__(self, start_url: str):
        self.url = start_url
        self._url_p = parse.urlparse(start_url)
        mongo_cli = MongoClient('mongodb://localhost:27017')
        self.mongo_db = mongo_cli['parse_data']

    def _get_soup(self, url):
        resp = requests.get(url, headers=self.__headers, params=self.__params)
        return BeautifulSoup(resp.text, 'lxml')

    def parse(self):
        soup = self._get_soup(self.url)
        catalog = soup.find('div', attrs={'class': 'сatalogue__main'})
        products = catalog.findChildren('a', attrs={'class': 'card-sale'})
        for product in  products[:3]:
            if len(product.attrs['class'])>2 or product.attrs['href'][0] != '/':
                #print(f"CONTINUE --- {product.attrs['class']}, {product.attrs['href']}")
                continue
            prod_url = (f"{self._url_p.scheme}://{self._url_p.hostname}{product.attrs['href']}")
            prod_soup = self._get_soup(prod_url)
            prod_info = prod_soup.find('div', attrs={'class':'action row'})
            prod_data = self.get_product_structure(prod_url, prod_info)
            print(prod_data)
            self.save_to(prod_data)

    def get_product_structure(self, url, prod_soup):
        product_template = {
            'promo_name' : ('p', 'action__name-text', 'text'),
            'product_name' : ('div', 'action__title', 'text'),
            'old_price' : ('div', 'label__price label__price_old', 'text'),
            'new_price' : ('div', 'label__price label__price_new', 'text'),
            'image_url': ('picture', 'action__image lazy loaded', 'data-src'),
            'date_from_to': ('div', 'action__date-label', 'text'),
        }
        prod = { 'url': url, }
        for key in product_template:
            value = product_template[key]
            try:
                if key == 'old_price' or key == 'new_price':
                    p_soup = prod_soup.find(value[0], attrs={'class': value[1]})
                    pr = getattr(p_soup.findChild('span', attrs={'class': 'label__price-integer'}), 'text')
                    pr_dec = getattr(p_soup.findChild('span', attrs={'class': 'label__price-decimal'}), 'text')
                    prod[key] = f'{pr}.{pr_dec}'
                elif key == 'image_url':
                    img_path = prod_soup.find('img')['data-src']
                    img_url = (f"{self._url_p.scheme}://{self._url_p.hostname}{img_path}")
                    prod[key] = img_url
                else:
                    prod[key] = getattr( prod_soup.find(value[0], attrs={'class':value[1]}) , value[2] )
            except Exception:
                prod[key] = None
        return prod

    def save_to(self, product_data: dict):
        collection = self.mongo_db['magnit_data']
        collection.insert_one(product_data)

if __name__ == '__main__':
    mp = magnit_parcer("https://magnit.ru/promo/")
    mp.parse()