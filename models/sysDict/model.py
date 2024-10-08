from datetime import datetime

from sqlalchemy import Column,Integer,String,ForeignKey
from sqlalchemy.orm import relationship
from extend.db import Base,LOCSESSION,ENGIN

import time

class SysDict(Base):
    __tablename__ = 'sysDict'
    id = Column(Integer, primary_key=True, autoincrement=True)  # 自增主键
    key = Column(String(100), nullable=False, default='') # 名称 如性别
    type = Column(String(50), nullable=False, default='') # 类型 如 0:系统 1:业务
    value = Column(String(50), nullable=False, default='') # 值 如 sex
    desc = Column(String(200), nullable=False, default='') # 描述 如 0:男 1:女 2:未知
    createTime = Column(Integer, nullable=False, default=lambda: int(datetime.now().timestamp()))  # 创建时间
    updateTime = Column(Integer, nullable=False, default=lambda: int(datetime.now().timestamp()))  # 更新时间
    status = Column(Integer, default=0) # 0:正常 1:禁用
    children = relationship("SysDictChild", backref="parent", lazy="dynamic") # 子项

    #谁操作的
    operatorParent = Column(String(100), nullable=False, default='') #操作人


class SysDictChild(Base):
    __tablename__ = 'sysDictChild'
    id = Column(Integer, primary_key=True, autoincrement=True)  # 自增主键
    dictId = Column(Integer, ForeignKey('sysDict.id'), nullable=False, default=0) # 字典id
    key = Column(String(100), nullable=False, default='') # 名称 如性别
    value = Column(String(50), nullable=False, default='') # 值 如 sex
    desc = Column(String(200), nullable=False, default='') # 描述 如 0:男 1:女 2:未知
    createTime = Column(Integer, nullable=False, default=lambda: int(datetime.now().timestamp()))  # 创建时间
    updateTime = Column(Integer, nullable=False, default=lambda: int(datetime.now().timestamp()))  # 更新时间
    status = Column(Integer, default=0,nullable=False) # 0:正常 1:禁用
    #谁操作的
    operatorChild = Column(String(100), nullable=False, default='')
