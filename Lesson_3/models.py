from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy import (
    Column,
    Integer,
    String,
    ForeignKey,
    Table
)

Base = declarative_base()

t_teg_post = Table(
    't_teg_post', Base.metadata,
    Column('post_id', Integer, ForeignKey('t_posts.id')),
    Column('tag_id', Integer, ForeignKey('t_tag.id'))
)

class Post(Base):
    Base.__tablename__ = 't_posts'
    id = Column(Integer, autoincrement=True, primary_key=True)
    url = Column(Integer, unique=True, nullable=False)
    img_url = Column(String, unique=False, nullable=True)
    author_id = Column(Integer, ForeignKey('t_author.id'))
    author = relationship("Author", back_populates="posts" ) # backpopulate -> название поля в таблице
 #   tag = relationship("Tag", secondary=t_teg_post, back_populates="posts" )

class Author(Base):
    Base.__tablename__ = 't_author'
    id = Column(Integer, autoincrement=True, primary_key=True)
    name = Column(String, unique=False, nullable=False)
    url = Column(String, unique=True, nullable=False)
    posts = relationship("Post")

class Tag(Base):
    Base.__tablename__ = 't_tag'
    id = Column(Integer, autoincrement=True, primary_key=True)
    name = Column(String, unique=False, nullable=False)
    url = Column(String, unique=True, nullable=False)
    posts = relationship("Post", secondary=t_teg_post)
