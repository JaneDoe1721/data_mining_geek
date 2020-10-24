from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

from sqlalchemy import (
    Column,
    Integer,
    String,
    ForeignKey,
    Table
)
"""
one to one 
one to many
many to many
many to one
"""

Base = declarative_base()

tag_post = Table(
    'tag_post',
    Base.metadata,
    Column('post_id', Integer, ForeignKey('post.id')),
    Column('tag_id', Integer, ForeignKey('tag.id'))
)


class Post(Base):
    __tablename__ = 'post'
    id = Column(Integer, autoincrement=True, primary_key=True)
    url = Column(String, unique=True, nullable=False)
    title = Column(String, unique=False, nullable=False)
    img_url = Column(String, unique=False, nullable=True)
    date = Column(Integer, unique=False, nullable=True)
    writer_id = Column(Integer, ForeignKey('writer.id'))
    writer = relationship('Writer', back_populates='posts')
    tag = relationship('Tag', secondary=tag_post, back_populates='posts')
    comment = relationship('Comments', back_populates='posts')

    def __init__(self, title: str, url: str, img_url: str, date: int, tags: list = None,):
        self.title = title
        self.url = url
        self.img_url = img_url
        self.date = date
        if tags:
            self.tag.extend(tags)


class Writer(Base):
    __tablename__ = 'writer'
    id = Column(Integer, autoincrement=True, primary_key=True)
    name = Column(String, unique=False, nullable=False)
    url = Column(String, unique=True, nullable=False)
    posts = relationship('Post')

    def __init__(self, name, url):
        self.name = name
        self.url = url


class Tag(Base):
    __tablename__ = 'tag'
    id = Column(Integer, autoincrement=True, primary_key=True)
    name = Column(String, unique=False, nullable=False)
    url = Column(String, unique=True, nullable=False)
    posts = relationship('Post', secondary=tag_post)

    def __init__(self, name, url):
        self.name = name
        self.url = url


class Comments(Base):
    __tablename__ = 'comments'
    id = Column(Integer, autoincrement=True, primary_key=True)
    user_id = Column(Integer, ForeignKey('writer.id'))
    full_name = Column(String, unique=False, nullable=False)
    text = Column(String, unique=False, nullable=False)
