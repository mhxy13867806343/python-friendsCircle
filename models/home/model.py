from datetime import datetime
from sqlalchemy import Column, Integer, String, ForeignKey, Text
from sqlalchemy.orm import relationship
from extend.db import Base


#轮播图
class Carousel(Base):
    __tablename__ = 'carousel'
    id = Column(Integer, primary_key=True, autoincrement=True)
    title = Column(String(40), nullable=False,default='')  # 标题
    type=Column(Integer, nullable=False,default=0)  # 类型 img=0,text=1 video=2
    img_url = Column(String(255), nullable=False)  # 图片地址 要上传
    link_url = Column(String(255), nullable=False)  # 跳转地址 不需上传，直接使用url
    video_url = Column(String(255), nullable=False) # 视频地址不进行上传，直接使用url
    content = Column(Text, nullable=False,default='')  # 描述
    is_hidden = Column(Integer, nullable=False,default=0) # 是否隐藏 0显示 1隐藏
    text = Column(Text, nullable=False,default='') # 文本
    priority = Column(Integer, default=0)  # 优先级，越大越靠前
    is_status = Column(Integer, nullable=False,default=0)  # 状态 0正常 1删除
    createTime = Column(Integer, nullable=False, default=lambda: int(datetime.now().timestamp()))  # 创建时间
    updateTime = Column(Integer, nullable=False, default=lambda: int(datetime.now().timestamp()))  # 更新时间
    #结束时间 +30天
    end_time = Column(Integer, nullable=False, default=lambda: int(datetime.now().timestamp())+2592000)  # 结束时间
    create_user=Column(String(30), nullable=False,default='admin')  # 创建人
    browse_count = Column(Integer, nullable=False, default=0)  # 浏览次数


