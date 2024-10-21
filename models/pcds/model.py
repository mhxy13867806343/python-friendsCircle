from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from extend.db import Base

# 省表
class Province(Base):
    __tablename__ = 'provinces'

    id = Column(Integer, primary_key=True, autoincrement=True)
    code = Column(String(10), nullable=False)
    name = Column(String(50), nullable=False)
    lv = Column(Integer, nullable=False, default=0)
    cities = relationship('City', back_populates='province')

# 市表
class City(Base):
    __tablename__ = 'cities'

    id = Column(Integer, primary_key=True, autoincrement=True)
    province_id = Column(Integer, ForeignKey('provinces.id'))
    code = Column(String(10), nullable=False)
    name = Column(String(50), nullable=False)
    lv = Column(Integer, nullable=False, default=1)
    province = relationship('Province', back_populates='cities')
    districts = relationship('District', back_populates='city')

# 区/县表
class District(Base):
    __tablename__ = 'districts'

    id = Column(Integer, primary_key=True, autoincrement=True)
    city_id = Column(Integer, ForeignKey('cities.id'))
    code = Column(String(10), nullable=False)
    name = Column(String(50), nullable=False)
    lv = Column(Integer, nullable=False, default=2)
    city = relationship('City', back_populates='districts')
    streets = relationship('Street', back_populates='district')

# 街道表
class Street(Base):
    __tablename__ = 'streets'

    id = Column(Integer, primary_key=True, autoincrement=True)
    district_id = Column(Integer, ForeignKey('districts.id'))
    code = Column(String(15), nullable=False)
    name = Column(String(50), nullable=False)
    lv = Column(Integer, nullable=False, default=3)
    district = relationship('District', back_populates='streets')
