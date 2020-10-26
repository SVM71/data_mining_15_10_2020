from bs4 import BeautifulSoup
import requests
from urllib import parse
import json
import datetime as dt

class c_user_date:
    _month_dict = {
        'янв':1, 'фев':2, 'мар':3, 'апр':4, 'май':5, 'мая':5, 'июн':6,
        'июл':7, 'авг':8, 'сен':9, 'окт':10, 'ноя':11, 'дек':12
    }
    # преобразует строку в виде 3 сентября сего года в тип date
    @staticmethod
    def get_date(date_in: str):
        tmp_lst = date_in.split(' ')
        u_date = dt.date(year=int(tmp_lst[2]), month=c_user_date._month_dict[tmp_lst[1][:3]], day=int(tmp_lst[0]))
        return u_date

# url страницы материала
# Заголовок материала
# Первое изображение материала (Ссылка)
# Дата публикации (в формате datetime)
# имя автора материала
# ссылка на страницу автора материала
# комментарии в виде (автор комментария и текст комментария)

url = 'https://geekbrains.ru/posts'
headers = { 'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:81.0) Gecko/20100101 Firefox/81.0' }
params = { 'page' : 62 }
url_p = parse.urlparse(url)

resp = requests.get(url, headers=headers, params=params)
soup = BeautifulSoup(resp.text, 'lxml')
wrapper = soup.find('div', attrs={'class': 'post-items-wrapper'})
posts_on_pg = wrapper.find_all('div', attrs={'class': 'post-item event'})
### ==== Обход одной страницы с постами
print( len(posts_on_pg) )
for post in posts_on_pg[:3]:
    img_url = post.find('img')['src']
    post_date = c_user_date.get_date( post.find('div', attrs={ 'class': 'small m-t-xs'} ).string )
    post_inf = post.find('a', attrs={'class': 'post-item__title h3 search_text'})
    post_name = post_inf.string
    post_url = f"{url_p.scheme}://{url_p.hostname}{post_inf['href']}"
    print('X'*20)
    print( f'post_url:\t{post_url}\npost_name:\t{post_name}\nimg_url:\t{img_url}\npost_date:\t{post_date}' )

    ### == Собираем инфо о посте ====
    resp_post = requests.get(post_url, headers=headers, params=params)
    post_soup = BeautifulSoup(resp_post.text, 'lxml')
    autor_teg = post_soup.find('div', attrs={'class': 'col-md-5 col-sm-12 col-lg-8 col-xs-12 padder-v'})
    autor_url_path = autor_teg.findChild('a')['href']
    autor_url = f"{url_p.scheme}://{url_p.hostname}{autor_url_path}"
    autor_name = autor_teg.find('div', attrs={'class': 'text-lg text-dark'}).string
    print(f"autor_name:\t{autor_name}\nautor_url:\t{autor_url}")

    ### комментарии в виде (автор комментария и текст комментария)
    #'https://geekbrains.ru/api/v2/comments?commentable_type=Post&commentable_id=35&order=desc'
    comment_params = { 'commentable_type': '', 'commentable_id':0, 'order':'' }
    comment_headers = { 'Accept':'application/json, text/plain, */*',
                        'User-Agent':'Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:81.0) Gecko/20100101 Firefox/81.0'}

    ct_table_teg = post_soup.find('div', attrs={'class': 'm-t-xl'})
    ct_params_teg = ct_table_teg.find('comments')
    comment_params['commentable_type'] = ct_params_teg['commentable-type']
    comment_params['commentable_id'] = ct_params_teg['commentable-id']
    comment_params['order'] = ct_params_teg['order']
    comment_url = f'https://geekbrains.ru/api/v2/comments'
    comments = json.loads( requests.get(comment_url, headers=comment_headers, params=comment_params).text )
    print(f'XXXXXXX количество комментариев: {len(comments)}')
    for comment in comments:
        comment_text = comment['comment']['body']
        comment_author = comment['comment']['user']['url']
        print( f'comment_author:\t{comment_author}\ncomment_text:\n{comment_text}' )

    post_tegs_tag = post_soup.find_all('a', attrs={'class': 'small'})
    print(f'XXXXXXX Тегов: {len(post_tegs_tag)} XXXXXX tag_name: tag_url')
    for teg_tag in post_tegs_tag:
        teg_url = f"{url_p.scheme}://{url_p.hostname}{teg_tag['href']}"
        print( f'{teg_tag.string:<30}:{teg_url}' )
    print( 'X'*20 )

############################################################
# resp = requests.get(url, headers=headers, params=params)
# with open("GB_posts_p1.html", 'w', encoding='utf-8') as f:
#     f.write(resp.text)
#
# params = { 'page' : 62 }
# resp = requests.get(url, headers=headers, params=params)
# with open("GB_posts_p62.html", 'w', encoding='utf-8') as f:
#     f.write(resp.text)
#
# params = { 'page' : 63 }
# resp = requests.get(url, headers=headers, params=params)
# with open("GB_posts_p63.html", 'w', encoding='utf-8') as f:
#     f.write(resp.text)

# url_p = parse.urlparse(url)
#
# with open("GB_posts_p62.html", 'r', encoding='utf-8') as f:
#     html_pg = f.read()
#     soup = BeautifulSoup(html_pg, 'lxml')
#     wrapper = soup.find('div', attrs={'class': 'post-items-wrapper'})
#     posts_on_pg = wrapper.find_all('div', attrs={'class': 'post-item event'})
#     print( len(posts_on_pg) )
#     for post in posts_on_pg[:5]:
#         print('='*20)
#         post_inf = post.find('a', attrs={'class': 'post-item__title h3 search_text'})
#         img_url = post.find('img')['src']
#         post_date = c_user_date.get_date( post.find('div', attrs={ 'class': 'small m-t-xs'} ).string )
#         post_name = post_inf.string
#         post_url = f"{url_p.scheme}://{url_p.hostname}{post_inf['href']}"
#         print( post_url,'\n',post_name,'\n',img_url,'\n',post_date )
#         #print(f'post_url: {post_url}')#\nimg_url: {img_url}')


############################################################
# имя автора материала
# ссылка на страницу автора материала

#url_post = 'https://geekbrains.ru/posts/progers_practice'
# resp = requests.get(url, headers=headers)
# with open("GB_posts_p62_post1.html", 'w', encoding='utf-8') as f:
#     f.write(resp.text)

# url_p_post = parse.urlparse(url_post)
# with open("GB_posts_p62_post1.html", 'r', encoding='utf-8') as f:
#     html_pg = f.read()
#     soup = BeautifulSoup(html_pg, 'lxml')
    # autor_teg = soup.find('div', attrs={'class': 'col-md-5 col-sm-12 col-lg-8 col-xs-12 padder-v'})
    # autor_name = autor_teg.find('div', attrs={'class': 'text-lg text-dark'}).string
    # autor_url = autor_teg.find('meta', itemprop="name").next['content']
    # print('='*20,'\n',autor_name, '\n', autor_url)

# ################################################################
# import json
#     # комментарии в виде (автор комментария и текст комментария)
#     #'https://geekbrains.ru/api/v2/comments?commentable_type=Post&commentable_id=35&order=desc'
#     # https://geekbrains.ru/api/v2/comments?commentable_type=Post&commentable_id=2410&order=desc
#
# comment_params = { 'commentable_type': '', 'commentable_id':0, 'order':'' }
# comment_headers = { 'Accept':'application/json, text/plain, */*',
#                     'User-Agent':'Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:81.0) Gecko/20100101 Firefox/81.0'}
# with open("Original.htm", 'r', encoding='utf-8') as f:
#     resp = f.read()
#     soup = BeautifulSoup(resp, 'lxml')
#
#     post_tegs = soup.find('i', attrs={'class': 'i i-tag m-r-xs text-muted text-xs'})
#     tegs_names = post_tegs['keywords'].replace(' ', '').split(',')
#     for name in tegs_names:
#         teg = post_tegs.next
#         print( f"{name:<30}:{teg['href']}" )
#     print( 'Z'*20 )
# #    'internet-marketing, https://geekbrains.ru/posts?tag=internet-marketing'
#
#     print(f' post_tegs: {post_tegs}')
#     comment_table_teg = soup.find('div', attrs={'class': 'm-t-xl'})
#     ct_req_teg = comment_table_teg.find('comments')
#     comment_params['commentable_type'] = ct_req_teg['commentable-type']
#     comment_params['commentable_id'] = 33#ct_req_teg['commentable-id']
#     comment_params['order'] = ct_req_teg['order']
#     comment_url = f'https://geekbrains.ru/api/v2/comments'
#     resp_json = json.loads( requests.get(comment_url, headers=comment_headers, params=comment_params).text, \
#                             encoding='utf-8' )
#
#     #print( len( resp_json ), type(resp_json) )
#     comment_text = resp_json[0]['comment']['body']
#     comment_author = resp_json[0]['comment']['user']['url']
#     print( comment_author, '\n', comment_text )
#
# ############################################################

