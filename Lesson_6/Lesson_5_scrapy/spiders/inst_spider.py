import scrapy
import json
import datetime as dt
from Lesson_5_scrapy.items import InstaTag, InstaPost

class InstSpider(scrapy.Spider):
    name = 'inst_spider'
    allowed_domains = ['www.instagram.com']
    start_urls = ['https://www.instagram.com']
    login_url = 'https://www.instagram.com/accounts/login/ajax/'
    tags_dict = {
        'python': 'https://www.instagram.com/graphql/query/',
        'query_hash': '9b498c08113f1e09617a1703c22b2f32'
    }

    def __init__(self, login, passwd, *args, **kwargs):
        self.username = login
        self.enc_paswd = passwd
        super().__init__(*args, **kwargs)

    def parse(self, response, **kwargs):
        try:
            js_data = self.js_data_extract(response)
            yield scrapy.FormRequest(
                self.login_url,
                method='POST',
                formdata={
                    'username':self.username,
                    'enc_password':self.enc_paswd
                },
                headers={'X-CSRFToken': js_data['config']['csrf_token']}
            )
        except AttributeError as err:
            print('Z'*20,response, 'Z'*20, response.json())
            if response.json().get('authenticated'):
                for tag in self.tags_dict.keys():
                    yield response.follow( f'/explore/tags/{tag}/', callback=self.tag_parse)
            else:# message -- НЕ ПОДКЛЮЧИЛСЯ ПАУК к INSTAGRAM
                print(f'=====> OOPS, ERROR! Authorisation on "{self.start_urls[0]}" FAILED!! <=====')

    def tag_parse(self, response):
        js_data = self.js_data_extract(response)
        tag = js_data['entry_data']['TagPage'][0]['graphql']['hashtag']
        print(f'{dt.datetime.utcnow()} id: {tag["id"]}, name: {tag["name"]}, profile_pic_url: {tag["profile_pic_url"]}')
        yield InstaTag(
            date_parse=dt.datetime.utcnow(),
            data={'id': tag['id'], 'name':tag['name'], 'profile_pic_url':tag['profile_pic_url']},
        )
        yield from self.get_posts_tag(tag, response)

    def tag_api_parse(self, response):
        yield from self.get_posts_tag(response.json()['data']['hashtag'], response)

    def get_posts_tag(self, tag, response):
        if tag['edge_hashtag_to_media']['page_info']['has_next_page']:
            vars = {
                "tag_name": tag['name'],
                "first": 10,
                "after": tag['edge_hashtag_to_media']['page_info']['end_cursor']
            }
            vars_str=json.dumps(vars).replace(" ", "")
            next_req=f'https://www.instagram.com/graphql/query/?query_hash={self.tags_dict["query_hash"]}&variables={vars_str}'
            yield response.follow(next_req, callback=self.tag_api_parse)

        yield from self.get_post_item(tag['edge_hashtag_to_media']['edges'])

    @staticmethod
    def get_post_item(edges):
        for edge in edges:
            yield InstaPost(
                date_parse=dt.datetime.utcnow(),
                data=edge['node']
            )

    @staticmethod
    def js_data_extract(response):
        script = response.xpath('//script[contains(text(), "window._sharedData = ")]/text()').get()
        script = script.replace('window._sharedData = ', '')[:-1]
        return json.loads(script)
