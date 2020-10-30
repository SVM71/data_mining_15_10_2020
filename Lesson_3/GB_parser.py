from bs4 import BeautifulSoup
import requests
from urllib import parse
import json
import datetime as dt
import database


class CUsrDate:
    _month_dict = {
        'янв':1, 'фев':2, 'мар':3, 'апр':4, 'май':5, 'мая':5, 'июн':6,
        'июл':7, 'авг':8, 'сен':9, 'окт':10, 'ноя':11, 'дек':12
    }

    # преобразует строку в виде 3 сентября 2020 в тип date
    @staticmethod
    def get_date(date_in: str):
        tmp_lst = date_in.split(' ')
        u_date = dt.date(year=int(tmp_lst[2]), month=CUsrDate._month_dict[tmp_lst[1][:3]], day=int(tmp_lst[0]))
        return u_date


class GBParser:
    url = 'https://geekbrains.ru/posts'
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:81.0) Gecko/20100101 Firefox/81.0'}
    url_p = parse.urlparse(url)
    usr_db = database.DataBaseUtils()

    def get_posts_on_page(self, page_num: int):
        params = {'page': page_num}
        resp = requests.get(self.url, headers=self.headers, params=params)
        soup = BeautifulSoup(resp.text, 'lxml')
        wrapper = soup.find('div', attrs={'class': 'post-items-wrapper'})
        posts_on_pg = wrapper.find_all('div', attrs={'class': 'post-item event'})
        return posts_on_pg

    # собирает инфо для поста в виде словаря
    # post = { 'name':str, 'url':str, 'img_url':str, 'published':date }
    def get_post_dict(self, post_soup):
        post_data = dict()
        post_data['img_url'] = post_soup.find('img')['src']
        post_data['published'] = CUsrDate.get_date(post_soup.find('div', attrs={'class': 'small m-t-xs'}).string)
        post_inf = post_soup.find('a', attrs={'class': 'post-item__title h3 search_text'})
        post_data['name'] = post_inf.string
        post_data['url'] = f"{self.url_p.scheme}://{self.url_p.hostname}{post_inf['href']}"
        return post_data

    def get_post_page_soup(self, post_url:str):
        resp_post = requests.get(post_url, headers=self.headers)
        return BeautifulSoup(resp_post.text, 'lxml')

    # собирает инфо об авторе поста в виде словаря со страницы поста
    # author = { 'name':str, 'url':str}
    def get_author_dict(self, post_page_soup):
        author = dict()
        autor_teg = post_page_soup.find('div', attrs={'class': 'col-md-5 col-sm-12 col-lg-8 col-xs-12 padder-v'})
        autor_url_path = autor_teg.findChild('a')['href']
        author['url'] = f"{self.url_p.scheme}://{self.url_p.hostname}{autor_url_path}"
        author['name'] = autor_teg.find('div', attrs={'class': 'text-lg text-dark'}).string
        return author

    # собирает инфо об тематике поста в виде списка словарей со страницы поста
    # tag_data = { 'url':str, 'name':str}
    def get_list_of_tag_dict(self, post_page_soup):
        res = []
        post_tegs_tag = post_page_soup.find_all('a', attrs={'class': 'small'})
        for teg_tag in post_tegs_tag:
            tag_data = dict()
            tag_data['url'] = f"{self.url_p.scheme}://{self.url_p.hostname}{teg_tag['href']}"
            tag_data['name'] = teg_tag.string
            res.append(tag_data)
        return res

    # собирает комментарии к посту в виде списка словарей со страницы поста
    # comment_dict = { autor:dict, text:str)
    def get_list_of_comment_dict(self, post_page_soup):
        res = []
        # комментарии в виде (автор комментария и текст комментария)
        # 'https://geekbrains.ru/api/v2/comments?commentable_type=Post&commentable_id=35&order=desc'
        comment_params = {'commentable_type': '', 'commentable_id': 0, 'order': ''}
        comment_headers = {'Accept': 'application/json, text/plain, */*',
                           'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:81.0) Gecko/20100101 Firefox/81.0'}

        ct_table_teg = post_page_soup.find('div', attrs={'class': 'm-t-xl'})
        ct_params_teg = ct_table_teg.find('comments')
        comment_params['commentable_type'] = ct_params_teg['commentable-type']
        comment_params['commentable_id'] = ct_params_teg['commentable-id']
        comment_params['order'] = ct_params_teg['order']
        comment_url = f'https://geekbrains.ru/api/v2/comments'
        comments = json.loads(requests.get(comment_url, headers=comment_headers, params=comment_params).text)
        for comment in comments:
            item = dict()
            item['text'] = comment['comment']['body']
            item['author'] = {
                'url':comment['comment']['user']['url'],
                'name': comment['comment']['user']['full_name'],
            }
            res.append(item)
        return res

    # занимается разбором страницы с катрочками постов
    def api_parse_posts_page(self, page_num:int):
        page_posts = self.get_posts_on_page(page_num)
        if len(page_posts) == 0:
            return 0
        for post in page_posts:                 #[:3]:
            post_data = self.get_post_dict(post)
            pp_soup = self.get_post_page_soup(post_data['url'])
            post_author = self.get_author_dict(pp_soup)
            tags_list = self.get_list_of_tag_dict(pp_soup)
            comments_list = self.get_list_of_comment_dict(pp_soup)

            post_id = self.usr_db.api_db_save_post(post_data, post_author)
            for tag in tags_list:
                self.usr_db.api_db_save_tag(post_id, tag['name'], tag['url'])
            for comment in comments_list:
                self.usr_db.api_db_save_comment(post_id, comment['author'], comment['text'])
        return len(page_posts)

    # занимается разбором всех страниц с катрочками постов
    def api_parse_all_posts(self):
        curr_page = 1
        summ_posts = 0
        while True:
            pg_posts_len = self.api_parse_posts_page(curr_page)
            summ_posts += pg_posts_len
            if pg_posts_len == 0:
                break
            curr_page += 1 #10
        return { 'pages': curr_page, 'posts': summ_posts}


if __name__ == '__main__':
    parser = GBParser()
    #print(parser.api_parse_all_posts())
    print(parser.usr_db.api_db_select(parser.usr_db.t_authors))
