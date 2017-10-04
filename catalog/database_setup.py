import os
import sys
from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy import create_engine

Base = declarative_base()

class User(Base):
    __tablename__ = 'user'

    id = Column(Integer, primary_key = True)
    name = Column(String(80), nullable = False)
    email = Column(String(80), nullable = False)
    picture = Column(String(250))

class Category(Base):
    __tablename__ = 'category'

    id = Column(Integer, primary_key = True)
    name = Column(String(250), nullable = False)
    user_id = Column(Integer, ForeignKey('user.id'))
    user = relationship(User)

class CategoryItem(Base):
    __tablename__ = 'category_item'

    id = Column(Integer, primary_key = True)
    name = Column(String(80), nullable = False)
    description = Column(String(650))
    price = Column(String(8))
    itemtype = Column(String(250))
    category_id = Column(Integer,ForeignKey('category.id'))
    category_item = relationship(Category)
    user_id = Column(Integer, ForeignKey('user.id'))
    user = relationship(User)


    @property
    def serialize(self):
        # returns object data
        return {
        'id': self.id,
        'name': self.name,
        'description': self.description,
        'price': self.price,
        'itemtype': self.itemtype,
        }


engine = create_engine('postgresql://catalog:udacity@localhost/catalog')
Base.metadata.create_all(engine)

