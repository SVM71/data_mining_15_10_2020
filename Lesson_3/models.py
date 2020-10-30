from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy import (
    Column,
    Integer,
    String,
    ForeignKey,
    Table,
    Date
)

Base = declarative_base()

t_teg_post = Table(
    'table_teg_post', Base.metadata,
    Column('post_id', Integer, ForeignKey('table_posts.id')),
    Column('tag_id', Integer, ForeignKey('table_tag.id'))
)

class Post(Base):
    Base.__tablename__ = 'table_posts'
    id = Column(Integer, autoincrement=True, primary_key=True)
    url = Column(Integer, unique=True, nullable=False)
    name = Column(Integer, unique=False, nullable=False)
    img_url = Column(String, unique=False, nullable=True)
    published = Column(Date, unique=False, nullable=False)
    author_id = Column(Integer, ForeignKey('table_author.id'))
    author = relationship("Author", back_populates="posts" ) # backpopulate -> название поля в таблице
    tag = relationship("Tag", secondary=t_teg_post, back_populates="posts" )

class Author(Base):
    Base.__tablename__ = 'table_author'
    id = Column(Integer, autoincrement=True, primary_key=True)
    name = Column(String, unique=False, nullable=False)
    url = Column(String, unique=True, nullable=False)
    posts = relationship("Post")

class Comment(Base):
    Base.__tablename__ = 'table_comments'
    id = Column(Integer, autoincrement=True, primary_key=True)
    comment_text = Column(String, unique=False, nullable=False)
    comment_author_id = Column(Integer, ForeignKey('table_author.id'))
    comment_post_id = Column(Integer, ForeignKey('table_posts.id'))

class Tag(Base):
    Base.__tablename__ = 'table_tag'
    id = Column(Integer, autoincrement=True, primary_key=True)
    name = Column(String, unique=False, nullable=False)
    url = Column(String, unique=True, nullable=False)
    posts = relationship("Post", secondary=t_teg_post)
