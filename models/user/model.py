from datetime import datetime

from sqlalchemy import Column,Integer,String,ForeignKey,Text
from sqlalchemy.orm import relationship
from extend.db import Base,LOCSESSION,ENGIN

import time

# 评论
class Comment(Base):
    __tablename__ = 'comment'
    id = Column(Integer, primary_key=True, autoincrement=True)  # 评论的唯一标识
    user_id = Column(Integer, ForeignKey('user.id'), nullable=False)  # 谁创建的评论，关联 User 表的 id
    reply_to_user_id = Column(Integer, ForeignKey('user.id'), nullable=True)  # @谁回复的，可以为空，表示这不是一条回复评论
    friends_circle_id = Column(Integer, ForeignKey('friendsCircle.id'), nullable=False)  # 关联到朋友圈的评论
    content = Column(Text, nullable=True)
    createTime = Column(Integer, nullable=False, default=lambda: int(datetime.now().timestamp()))  # 创建时间
    updateTime = Column(Integer, nullable=False, default=lambda: int(datetime.now().timestamp()))  # 更新时间
    # 关系
    user = relationship("User", foreign_keys=[user_id], back_populates="comments_created")  # 关联创建评论的用户
    reply_to_user = relationship("User", foreign_keys=[reply_to_user_id], back_populates="comments_received")  # 关联被回复的用户
    friends_circle = relationship("FriendsCircle", back_populates="comments")  # 关联到朋友圈
    isStatus = Column(Integer, nullable=False, default=0)  # 0:正常 1:删除 并不是真的删除，只是标记为删除  如果是删除了，那么评论也要删除

# 朋友圈
class FriendsCircle(Base):
    __tablename__ = 'friendsCircle'
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey('account.id'), nullable=False)
    content = Column(Text, nullable=True)
    createTime = Column(Integer, nullable=False, default=lambda: int(datetime.now().timestamp()))  # 创建时间
    updateTime = Column(Integer, nullable=False, default=lambda: int(datetime.now().timestamp()))  # 更新时间
    # 关系
    user = relationship("User", back_populates="friendsCircle")
    comments = relationship("Comment", back_populates="friends_circle", order_by="Comment.createTime")  # 关联的评论
    isStatus = Column(Integer, nullable=False, default=0)  # 0:正常 1:删除 并不是真的删除，只是标记为删除  如果是删除了，那么评论也要删除
    # 点赞
    isLike = Column(Integer, nullable=False, default=0)  # 是否点赞 0:未点赞 1:已点赞
    like = Column(Integer, nullable=False, default=0)  # 点赞数
    #公开状态
    isPublic= Column(Integer, nullable=False, default=0)  # 0:公开 1:私密

    #评论id
    comment_id = Column(Integer, ForeignKey('comment.id'), nullable=True)
    #评论人
    comment_user_id = Column(Integer, ForeignKey('user.id'), nullable=True)

# 用户信息
class User(Base):  # 用户信息
    __tablename__ = ' user'
    id = Column(Integer, primary_key=True, autoincrement=True)  # 自增主键
    uid = Column(String(32), nullable=False, default='')  # 用户唯一标识符 通过这个去获取用户相关的信息
    phone = Column(String(11), nullable=False, default='')  # 手机号
    account = Column(String(50), nullable=False, default='')  # 账号
    password = Column(String(60), nullable=False, default='', )  # 密码
    createTime = Column(Integer, nullable=False, default=lambda: int(datetime.now().timestamp()))  # 创建时间
    updateTime = Column(Integer, nullable=False, default=lambda: int(datetime.now().timestamp()))  # 更新时间
    user_type = Column(Integer, nullable=False, default=0)  # 用户类型 0:管理员 1:普通用户 2:游客
    email_str = Column(String(100), nullable=False, default='')  # 邮箱
    name_str = Column(String(30), nullable=False, default='')  # 昵称
    birthday = Column(Integer, nullable=False, default=None)  # 生日 用时间戳
    sex = Column(Integer, nullable=False, default=0)  # 0:男 1:女 2:未知
    # 省市区
    province_code = Column(Integer, nullable=False, default='')  # 省份code
    city_code = Column(Integer, nullable=False, default='')  # 城市code
    district_code = Column(Integer, nullable=False, default='')  # 区县code
    address = Column(String(100), nullable=False, default='')  # 详细地址
    isStatus = Column(Integer, nullable=False, default=0)  # 0:正常 1:封禁 2:删除
    ip_v64 = Column(String(56), nullable=False, default='')  # 注册ip
    vx_id = Column(String(100), nullable=False, default='')  # 微信id
    qq_id = Column(String(100), nullable=False, default='')  # qq号
    github_id = Column(String(100), nullable=False, default='')  # github号
    juejin_id = Column(String(100), nullable=False, default='')  # juejin号
    # 身份证
    id_card = Column(String(18), nullable=False, default='')  # 身份证号 18位 默认为空
    # 上一次登录时间
    last_login_time = Column(Integer, nullable=False, default=lambda: int(datetime.now().timestamp()))  # 上一次登录时间 默认当前时间
    # 浏览器类型
    browser_type = Column(String(100), nullable=False, default='chrome')  # 浏览器类型 默认chrome
    # 操作系统类型
    os_type = Column(String(100), nullable=False, default='windows')  # 操作系统类型 默认windows
    # 登录方式
    login_type = Column(Integer, nullable=False, default=0)  # 0:h5,1:pc,2:qq,3:wx,4:github,5:juejin,6:其他
    # 登陆多少天
    login_days = Column(Integer, nullable=False, default=0)  # 登陆多少天 默认0
    # 头像
    avatar = Column(String(255), nullable=False, default='')  # 头像 直接是url地址

    # 游戏
    game_str = Column(String(255), nullable=False, default='')  # 游戏 如：王者荣耀，绝地求生，英雄联盟，最多12个，用逗号隔开
    # 朋友圈绑定到用户
    friendsCircle = relationship("FriendsCircle", back_populates="user", order_by="FriendsCircle.create_time")
    # 职位
    job_str = Column(String(255), nullable=False, default='')  # 职位 如：前端工程师，后端工程师，产品经理，UI设计师，用逗号隔开
    # 公司
    company_str = Column(String(100), nullable=False, default='')  # 公司 如：腾讯，阿里巴巴，百度，京东
    # 婚姻状态
    marriage_status = Column(Integer, nullable=False, default=0)  # 0:未婚 1:已婚 2:离异 3:丧偶,4:恋爱中,5:单身,6:保密
    # 与评论表的关系
    comments_created = relationship("Comment", foreign_keys=[Comment.user_id], back_populates="user",
                                    order_by="Comment.createTime")  # 创建的评论
    comments_received = relationship("Comment", foreign_keys=[Comment.reply_to_user_id], back_populates="reply_to_user",
                                     order_by="Comment.createTime")  # 收到的回复