from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import sqlalchemy as db
import models
import datetime as dt

# https://towardsdatascience.com/sqlalchemy-python-tutorial-79a577141a91


class DataBaseUtils:

    def __init__(self):
        self.engine = create_engine('sqlite:///GB_Posts_train.db')
        self.connection = self.engine.connect()
        models.Base.metadata.create_all(bind = self.engine)
        self.t_authors = db.Table('table_author', models.Author.metadata, autoload=True, autoload_with=self.engine)
        self.t_posts = db.Table('table_posts', models.Post.metadata, autoload=True, autoload_with=self.engine)
        self.t_comments = db.Table('table_comments', models.Comment.metadata, autoload=True, autoload_with=self.engine)
        self.t_tags = db.Table('table_tag', models.Tag.metadata, autoload=True, autoload_with=self.engine)
        self.t_teg_post = db.Table('table_teg_post', db.MetaData(), autoload=True, autoload_with=self.engine)

    def get_table_id(self, db_table, url: str):
        self.connection = self.engine.connect()
        query = db.select([db_table]).where(db_table.columns.url == url)  # select specific
        ResultProxy = self.connection.execute(query)
        ResultSet = ResultProxy.fetchall()
        ResultProxy.close()
        if len(ResultSet) != 0:
            return ResultSet[0][0]
        return None

    # author = { 'name': str, 'url': str}
    def set_author(self, author: dict):
        self.connection = self.engine.connect()
        query = db.insert(self.t_authors).values(name=author['name'], url=author['url'])
        ResultProxy = self.connection.execute(query)
        ResultProxy.close()

    # comment = { 'text':str, 'author_id':int, 'post_id':int}
    def set_comment(self, comment: dict):
        self.connection = self.engine.connect()
        query = db.insert(self.t_comments).values(
            comment_text=comment['text'],
            comment_author_id=comment['author_id'],
            comment_post_id=comment['post_id'])
        ResultProxy = self.connection.execute(query)
        ResultProxy.close()

    # post_data = { 'name':str, 'url':str, 'img_url':str, 'published':date, 'author_id':int}
    def set_post(self, post_data: dict):
        self.connection = self.engine.connect()
        query = db.insert(self.t_posts).values(
            url=post_data['url'],
            name=post_data['name'],
            img_url=post_data['img_url'],
            published=post_data['published'],
            author_id=post_data['author_id'])
        ResultProxy = self.connection.execute(query)
        ResultProxy.close()

    # tag_data = { 'url':str, 'name':str}
    def set_tag(self, tag_data: dict):
        self.connection = self.engine.connect()
        query = db.insert(self.t_tags).values(
            url=tag_data['url'],
            name=tag_data['name'])
        ResultProxy = self.connection.execute(query)
        ResultProxy.close()

    def set_tag_post(self, tag_id: int, post_id: int):
        self.connection = self.engine.connect()
        query = db.insert(self.t_teg_post).values(
            post_id=post_id, tag_id=tag_id)
        ResultProxy = self.connection.execute(query)
        ResultProxy.close()

    # сохранить в базе автора
    # author = { 'name': str, 'url': str}
    def api_db_save_author(self, author:dict):
        a_id = self.get_table_id(self.t_authors, author['url'])
        if a_id is None:
            self.set_author(author)
            return self.get_table_id(self.t_authors, author['url'])
        return a_id

    # сохранить в базе комментарий автора
    def api_db_save_comment(self, post_id:int,  autor:dict, text:str):
        # comment = { 'text':str, 'author_id':int, 'post_id':int}
        comment = { 'post_id': post_id }
        comment['author_id'] = self.api_db_save_author(autor)
        comment['text'] = text
        self.set_comment(comment)

    # сохранить в базе пост вернет id поста в базе
    # post = { 'name':str, 'url':str, 'img_url':str, 'published':date }
    # author = { 'name': str, 'url': str}
    def api_db_save_post(self, post:dict, autor:dict):
        post_data = post.copy()
        post_data['author_id'] = self.api_db_save_author(autor)
        self.set_post(post_data)
        post_id = self.get_table_id(self.t_posts, post_data['url'])
        return post_id

    # сохранить в базе Тег и связать с постом
    def api_db_save_tag(self, post_id: int, tag_name: str, tag_url:str ):
        tag_id = self.get_table_id(self.t_tags, tag_url)
        if tag_id is None:
            tag_data = { 'url': tag_url, 'name': tag_name}
            self.set_tag(tag_data)
            tag_id = self.get_table_id(self.t_tags, tag_url)
        # делаем связь пост и тег
        self.set_tag_post(tag_id = tag_id, post_id=post_id)

    def api_db_select(self, table):
        self.connection = self.engine.connect()
        query = db.select([table])
        res_proxy = self.connection.execute(query)
        res_set = res_proxy.fetchall()
        res_proxy.close()
        return res_set


if __name__ == '__main__':
    authors = [
        {'name': 'A1_name', 'url': 'a1_url'},
        {'name': 'A2_name', 'url': 'a2_url'},
        {'name': 'A3_name', 'url': 'a3_url'},
        {'name': 'A4_name', 'url': 'a4_url'},
    ]
    posts = [
        {'url': 'p1_url', 'img_url': 'p1_img_url', 'published': dt.date.today()},
        {'url': 'p2_url', 'img_url': 'p2_img_url', 'published': dt.date.today()},
        {'url': 'p3_url', 'img_url': 'p3_img_url', 'published': dt.date.today()},
        {'url': 'p4_url', 'img_url': 'p4_img_url', 'published': dt.date.today()},
        {'url': 'p5_url', 'img_url': 'p5_img_url', 'published': dt.date.today()},
    ]

    user_db = DataBaseUtils()

    for a in authors:
        user_db.api_db_save_author(a)

    post_id = user_db.api_db_save_post( posts[0], authors[0] )
    user_db.api_db_save_comment(post_id, authors[3], 'post_1_author_4comment ')
    user_db.api_db_save_comment(post_id, authors[2], 'post_1_author_3comment ')
    user_db.api_db_save_tag(post_id, 'tag_1_name', 'tag_1_url' )

    post_id = user_db.api_db_save_post( posts[1], authors[0] )
    user_db.api_db_save_comment(post_id, authors[0], 'post_2_author_1comment ')
    user_db.api_db_save_comment(post_id, authors[3], 'post_2_author_4comment ')
    user_db.api_db_save_tag(post_id, 'tag_1_name', 'tag_1_url' )

    print(user_db.api_db_select(user_db.t_authors))
    print(user_db.api_db_select(user_db.t_posts))
    print(user_db.api_db_select(user_db.t_comments))
    print(user_db.api_db_select(user_db.t_tags))
    print(user_db.api_db_select(user_db.t_teg_post))

    print(1)


