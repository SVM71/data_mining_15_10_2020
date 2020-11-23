import scrapy
import json
import datetime as dt
from Lesson_5_scrapy.items import InstaTag, InstaPost, InstaFollow, InstaUser


class InstSpider(scrapy.Spider):
    name = 'inst_spider'
    allowed_domains = ['www.instagram.com']
    start_urls = ['https://www.instagram.com']
    login_url = 'https://www.instagram.com/accounts/login/ajax/'
    tags_dict = {
        'python': 'https://www.instagram.com/graphql/query/',
        'python_query_hash': '9b498c08113f1e09617a1703c22b2f32'
    }

    users_start_page = ['teslamotors']
    api_url = '/graphql/query/'
    query_hash = {
        # 'posts': '56a7068fea504063273cc2120ffd54f3',
        # 'tag_posts': "9b498c08113f1e09617a1703c22b2f32",
        'follow': 'd04b0a864b4b54837c0d870b0e77e076',
        'followers': 'c76146de99bb02f6415203be841dd25a'
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
                # for tag in self.tags_dict.keys():
                #     yield response.follow( f'/explore/tags/{tag}/', callback=self.tag_parse)
                for user_sp in self.users_start_page:
                    yield response.follow(f'/{user_sp}/', callback=self.user_page_parse)
            else:# message -- НЕ ПОДКЛЮЧИЛСЯ ПАУК к INSTAGRAM
                print(f'=====> OOPS, ERROR! Authorisation on "{self.start_urls[0]}" FAILED!! <=====')

    def user_page_parse(self, response):
        user_data = self.js_data_extract(response)['entry_data']['ProfilePage'][0]['graphql']['user']
        yield InstaUser(
            date_parse=dt.datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S"),
            data=user_data
        )
        yield from self.get_api_follow_request(response, user_data)

    def get_api_follow_request(self, response, user_data, variables=None):
        if not variables:
            variables = {
                'id': user_data['id'],
                'first': 100,
            }
        url = f'{self.api_url}?query_hash={self.query_hash["follow"]}&variables={json.dumps(variables)}'
        yield response.follow(url, callback=self.get_api_follow, cb_kwargs={'user_data': user_data})

    def get_api_follow(self, response, user_data):
        if b'application/json' in response.headers['Content-Type']:
            data = response.json()
            yield from self.get_follow_item(user_data, data['data']['user']['edge_follow']['edges'])
            if data['data']['user']['edge_follow']['page_info']['has_next_page']:
                variables = {
                    'id': user_data['id'],
                    'first': 100,
                    'after': data['data']['user']['edge_follow']['page_info']['end_cursor'],
                }
                yield from self.get_api_follow_request(response, user_data, variables)

    def get_follow_item(self, user_data, follow_users_data):
        for user in follow_users_data:
            yield InstaFollow(
                user_id=user_data['id'],
                user_name=user_data['username'],
                follow_id=user['node']['id'],
                follow_name=user['node']['username']
            )
            yield InstaUser(
                date_parse=dt.datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S"),
                data=user['node']
            )

    def tag_parse(self, response):
        js_data = self.js_data_extract(response)
        tag = js_data['entry_data']['TagPage'][0]['graphql']['hashtag']
        print(f'{dt.datetime.utcnow()} id: {tag["id"]}, name: {tag["name"]}, profile_pic_url: {tag["profile_pic_url"]}')
        yield InstaTag(
            date_parse=dt.datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S"),
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
            next_req=f'https://www.instagram.com/graphql/query/?query_hash={self.tags_dict["python_query_hash"]}&variables={vars_str}'
            yield response.follow(next_req, callback=self.tag_api_parse)

        yield from self.get_post_item(tag['edge_hashtag_to_media']['edges'])

    @staticmethod
    def get_post_item(edges):
        for edge in edges:
            yield InstaPost(
                date_parse=dt.datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S"),
                data=edge['node']
            )

    @staticmethod
    def js_data_extract(response):
        script = response.xpath('//script[contains(text(), "window._sharedData = ")]/text()').get()
        script = script.replace('window._sharedData = ', '')[:-1]
        return json.loads(script)
