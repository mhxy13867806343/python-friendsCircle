from datetime import datetime
from sqlalchemy import Column, Integer, String, ForeignKey, Text
from sqlalchemy.orm import relationship
from extend.db import Base

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
    isStatus = Column(Integer, nullable=False, default=0)  # 0:正常 1:删除

    # 关系
    user = relationship("User", foreign_keys=[user_id], back_populates="comments_created")  # 关联创建评论的用户
    reply_to_user = relationship("User", foreign_keys=[reply_to_user_id], back_populates="comments_received")  # 关联被回复的用户
    friends_circle = relationship("FriendsCircle", back_populates="comments")  # 关联到朋友圈

# 朋友圈
class FriendsCircle(Base):
    __tablename__ = 'friendsCircle'
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey('user.id'), nullable=False)  # 关联发布朋友圈的用户
    content = Column(Text, nullable=True)
    createTime = Column(Integer, nullable=False, default=lambda: int(datetime.now().timestamp()))  # 创建时间
    updateTime = Column(Integer, nullable=False, default=lambda: int(datetime.now().timestamp()))  # 更新时间
    isStatus = Column(Integer, nullable=False, default=0)  # 0:正常 1:删除
    isLike = Column(Integer, nullable=False, default=0)  # 是否点赞 0:未点赞 1:已点赞
    like = Column(Integer, nullable=False, default=0)  # 点赞数
    isPublic = Column(Integer, nullable=False, default=0)  # 0:公开 1:私密

    # 关系
    user = relationship("User", foreign_keys=[user_id], back_populates="friendsCircle")  # 关联发布朋友圈的用户
    comments = relationship("Comment", back_populates="friends_circle", order_by="Comment.createTime")  # 关联的评论

# 用户信息
class User(Base):  # 用户信息
    __tablename__ = 'user'
    id = Column(Integer, primary_key=True, autoincrement=True)  # 自增主键
    uid = Column(String(32), nullable=False, default='')  # 用户唯一标识符
    phone = Column(String(11), nullable=False, default='')  # 手机号
    account = Column(String(50), nullable=False, default='')  # 账号
    password = Column(String(60), nullable=False, default='')  # 密码
    createTime = Column(Integer, nullable=False, default=lambda: int(datetime.now().timestamp()))  # 创建时间
    updateTime = Column(Integer, nullable=False, default=lambda: int(datetime.now().timestamp()))  # 更新时间
    user_type = Column(Integer, nullable=False, default=0)  # 用户类型 0:普通用户 1:管理员 2:超级管理员
    email_str = Column(String(100), nullable=False, default='')  # 邮箱
    name_str = Column(String(30), nullable=False, default='')  # 昵称
    birthday = Column(Integer, nullable=False, default=lambda: int(datetime.now().timestamp()))  # 生日
    sex = Column(Integer, nullable=False, default=0)  # 性别
    province_code = Column(String(100), nullable=False, default='')  # 省份code
    city_code = Column(String(100), nullable=False, default='')  # 城市code
    district_code = Column(String(100), nullable=False, default='')  # 区县code
    address = Column(String(100), nullable=False, default='')  # 详细地址
    isStatus = Column(Integer, nullable=False, default=0)  # 0:正常 1:封禁 2:删除
    ip_v64 = Column(String(56), nullable=False, default='')  # 注册ip
    vx_id = Column(String(100), nullable=False, default='')  # 微信id
    qq_id = Column(String(100), nullable=False, default='')  # qq号
    github_id = Column(String(100), nullable=False, default='')  # github号
    juejin_id = Column(String(100), nullable=False, default='')  # juejin号
    id_card = Column(String(18), nullable=False, default='')  # 身份证号
    last_login_time = Column(Integer, nullable=False, default=lambda: int(datetime.now().timestamp()))  # 上一次登录时间
    browser_type = Column(String(100), nullable=False, default='chrome')  # 浏览器类型
    os_type = Column(String(100), nullable=False, default='windows')  # 操作系统类型
    login_type = Column(Integer, nullable=False, default=0)  # 登录方式 用户类型 0pc 1mobile
    login_days = Column(Integer, nullable=False, default=0)  # 登陆多少天
    avatar = Column(String(255), nullable=False, default='')  # 头像
    game_str = Column(String(255), nullable=False, default='')  # 游戏
    job_str = Column(String(255), nullable=False, default='')  # 职位
    company_str = Column(String(100), nullable=False, default='')  # 公司
    marriage_status = Column(Integer, nullable=False, default=0)  # 婚姻状态

    # 关系
    friendsCircle = relationship("FriendsCircle", back_populates="user", order_by="FriendsCircle.createTime")  # 关联的朋友圈
    comments_created = relationship("Comment", foreign_keys=[Comment.user_id], back_populates="user", order_by="Comment.createTime")  # 创建的评论
    comments_received = relationship("Comment", foreign_keys=[Comment.reply_to_user_id], back_populates="reply_to_user", order_by="Comment.createTime")  # 收到的回复
