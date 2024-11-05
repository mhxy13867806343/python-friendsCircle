import time
import logging
from datetime import datetime
from typing import List

from IPython.core.release import description
from fastapi import APIRouter, Depends, status, Request
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session
from fastapi import status as httpStatus
from models.home.model import Carousel,FunctionalVersion
from models.user.model import User
from tools import appToken
from tools.appStatus import httpCodeStatus
from tools.appThrottling import limiter
from tools.apploggin import create_logger
from tools.db import getDbSession
from app.home.model import FunctionalVersionModel, CarouselModel
from tools.appOperation import getPaginatedList
# 初始化日志
logger = logging.getLogger(__name__)

# 创建字典路由
homeRouter = APIRouter()

create_logger(log_folder='logger',other_log="homes_log_")

@homeRouter.get('/carousel/list', description="轮播列表", summary="轮播列表")
@limiter.limit("10/minute")
async def homeCarouselList(request: Request, db: Session = Depends(getDbSession),pageNum: int = 1, pageSize: int = 10,
type:int=0,
hidden:int=0,
                           ):

    #当时时间戳
    now_time=int(datetime.now().timestamp())
    expired_items = db.query(Carousel).filter(now_time >= Carousel.end_time, Carousel.is_status == 0).all()
    if expired_items:
        for item in expired_items:
            item.is_status = 1
        try:
            db.commit()  # 提交更新到数据库
            db.refresh()
        except SQLAlchemyError as e:
            db.rollback()  # 如果有异常，回滚事务
            logging.error(f"数据库更新失败: {e}")
            return httpCodeStatus(code=httpStatus.HTTP_500_INTERNAL_SERVER_ERROR, message="数据库更新失败")
    d={
        "type":type,
        "is_hidden":hidden,
        "is_status":0
    }
    result = getPaginatedList(model=Carousel, session=db, pageNum=pageNum, pageSize=pageSize, **d)
    return httpCodeStatus(code=httpStatus.HTTP_200_OK, message="获取成功", data=result)

@homeRouter.post('/carousel/add',description="轮播新增",summary="轮播新增")
@limiter.limit("5/minute", error_message="请求过于频繁，请稍后再试!!!")
async def homeAdd(request: Request,data:CarouselModel, db: Session = Depends(getDbSession),
                  user:User=Depends(appToken.paseToken),
                  ):
    title:str=data.title
    content:str=data.content
    result=refCarouselQueryContent(db=db,user=user,title=title,content=content)
    try:
        db.add(Carousel(title=title,content=content,
                                 create_user=result.name_str or "admin"))
        db.commit()
        db.flush()
        return httpCodeStatus(code=httpStatus.HTTP_200_OK, message="新增成功", data={})
    except SQLAlchemyError as e:
        logger.error(f"新增功能失败: {e}")
        db.rollback()
        return httpCodeStatus(message="新增失败")

@homeRouter.put('/carousel/edit',description="轮播编辑",summary="轮播编辑")
@limiter.limit("5/minute", error_message="请求过于频繁，请稍后再试!!!")
async def homeEdit(request: Request,data:CarouselModel, db: Session = Depends(getDbSession),
                  user:User=Depends(appToken.paseToken),
                  ):
    title:str=data.title
    content:str=data.content
    id:int=data.id
    if not id:
        return httpCodeStatus(message="id不能为空，无法进行编辑")
    result=refCarouselQueryContent(db=db,user=user,title=title,content=content)
    try:
        now_time = int(datetime.now().timestamp())
        new= db.query(Carousel).filter(Carousel.id==id,Carousel.is_status==0,now_time<Carousel.end_time).first()
        new.title = title
        new.content = content
        new.update_time = int(time.time())
        db.commit()
        db.flush()
        return httpCodeStatus(code=httpStatus.HTTP_200_OK, message="编辑成功", data={})
    except SQLAlchemyError as e:
        logger.error(f"编辑功能失败: {e}")
        db.rollback()
        return httpCodeStatus(message="编辑失败")

@homeRouter.delete('/carousel/delete/{id}',description="轮播删除",summary="轮播删除")
@limiter.limit("5/minute", error_message="请求过于频繁，请稍后再试!!!")
async def homeDelete(request: Request,id:int, db: Session = Depends(getDbSession),user:User=Depends(appToken.paseToken),):

    try:
        if not id:
            return httpCodeStatus(message="id不能为空")
        result = db.query(User).filter(User.id == user).first()
        if not result:
            return httpCodeStatus(message="用户不存在")
        if result.user_type == 0:
            return httpCodeStatus(message="用户无权限进行创建操作")
        now_time = int(datetime.now().timestamp())
        new = db.query(Carousel).filter(Carousel.id == id, Carousel.is_status == 0,
                                        now_time < Carousel.end_time).first()
        if new:
            new.is_status=1
            db.commit()
            db.flush()
            return httpCodeStatus(message="删除成功")
        return httpCodeStatus(message="数据不存在,无法进行删除")
    except SQLAlchemyError as e:
        logger.error(f"删除功能失败: {e}")
        db.rollback()
        return httpCodeStatus(message="删除失败")
@homeRouter.get('/version/list', description="功能列表", summary="功能列表")
@limiter.limit("10/minute")
async def homeList(request: Request, db: Session = Depends(getDbSession),pageNum: int = 1, pageSize: int = 10):
    d={}
    result = getPaginatedList(model=FunctionalVersion, session=db, pageNum=pageNum, pageSize=pageSize, **d)
    return httpCodeStatus(code=httpStatus.HTTP_200_OK, message="获取成功", data=result)

@homeRouter.get('/version/first', description="功能最新的一条列表", summary="功能最新的一条列表")
@limiter.limit("10/minute")
async def homeList(request: Request, db: Session = Depends(getDbSession)):
    result=db.query(FunctionalVersion).order_by(FunctionalVersion.create_time.desc()).first()
    if result:
        return httpCodeStatus(code=httpStatus.HTTP_200_OK, message="获取成功", data=[result])
    return httpCodeStatus(code=httpStatus.HTTP_200_OK, message="获取成功", data=[])

@homeRouter.post('/version/add',description="功能新增",summary="功能新增")
@limiter.limit("5/minute", error_message="请求过于频繁，请稍后再试!!!")
async def homeAdd(request: Request,data:FunctionalVersionModel, db: Session = Depends(getDbSession),
                  user:User=Depends(appToken.paseToken),
                  ):
    title:str=data.title
    content:str=data.content
    version:str=data.version
    result=refCarouselQueryContent(db=db,user=user,title=title,content=content)
    if not result:
        return result
    try:
        db.add(FunctionalVersion(title=title,content=content,version=version,
                                 create_user=result.name_str or "admin"))
        db.commit()
        db.flush()
        return httpCodeStatus(code=httpStatus.HTTP_200_OK, message="新增成功", data={})
    except SQLAlchemyError as e:
        logger.error(f"新增功能失败: {e}")
        db.rollback()
        return httpCodeStatus(message="新增失败")

@homeRouter.put('/version/update',description="功能更新",summary="功能更新")
@limiter.limit("5/minute", error_message="请求过于频繁，请稍后再试!!!")
async def homeUpdate(request: Request,data:FunctionalVersionModel, db: Session = Depends(getDbSession),

user:User=Depends(appToken.paseToken),
                     ):
    id=data.id
    title:str=data.title
    content:str=data.content
    version:str=data.version

    if not id:
        return httpCodeStatus(message="id不能为空")
    result = refCarouselQueryContent(db=db, user=user, title=title, content=content)
    try:
        result= db.query(FunctionalVersion).filter(FunctionalVersion.id==id).filter()
        if result:
            result.update({"title":title,"content":content,"version":version,"update_time":int(time.time())})
            db.commit()
            db.flush()
            return httpCodeStatus(message="更新成功")
        return httpCodeStatus(message="数据不存在")
    except SQLAlchemyError as e:
        logger.error(f"更新功能失败: {e}")
        db.rollback()
        return httpCodeStatus(message="更新失败")

@homeRouter.delete('/version/delete/{id}',description="功能删除",summary="功能删除")
@limiter.limit("5/minute", error_message="请求过于频繁，请稍后再试!!!")
async def homeDelete(request: Request, id:int,db: Session = Depends(getDbSession),

user:User=Depends(appToken.paseToken),
                     ):
    if not id:
        return httpCodeStatus(message="id不能为空")
    result = db.query(User).filter(User.id == user).first()
    if not result:
        return httpCodeStatus(message="用户不存在")
    if result.user_type == 0:
        return httpCodeStatus(message="用户无权限进行创建操作")
    try:
        result= db.query(FunctionalVersion).filter(FunctionalVersion.id==vid).first()
        if result:
            result.is_status=1
            db.commit()
            db.flush()
            return httpCodeStatus(message="删除成功")
        return httpCodeStatus(message="数据不存在")
    except SQLAlchemyError as e:
        logger.error(f"删除功能失败: {e}")
        db.rollback()
        return httpCodeStatus(message="删除失败")


def refCarouselQueryContent(db,user,title,content):
    result = db.query(User).filter(User.id == user).first()
    if not result:
        return httpCodeStatus(message="用户不存在")
    if result.user_type == 0:
        return httpCodeStatus(message="用户无权限进行创建操作")
    if not title or len(title) == 0:
        return httpCodeStatus(message="标题不能为空")
    if not content or len(content) == 0:
        return httpCodeStatus(message="内容不能为空")
    return result