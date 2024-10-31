import time
import logging
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
from app.home.model import FunctionalVersionModel
from tools.appOperation import getPaginatedList
# 初始化日志
logger = logging.getLogger(__name__)

# 创建字典路由
homeRouter = APIRouter()

create_logger(log_folder='logger',other_log="homes_log_")
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
    result=db.query(User).filter(User.id==user).first()
    if not result:
        return httpCodeStatus(message="用户不存在")
    if result.user_type==0:
        return httpCodeStatus(message="用户无权限进行创建操作")
    if not title or len(title)==0:
        return httpCodeStatus(message="标题不能为空")
    if not content or len(content)==0:
        return httpCodeStatus(message="内容不能为空")
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
    result = db.query(User).filter(User.id == user).first()
    if not result:
        return httpCodeStatus(message="用户不存在")
    if result.user_type == 0:
        return httpCodeStatus(message="用户无权限进行创建操作")
    if not title or len(title)==0:
        return httpCodeStatus(message="标题不能为空")
    if not content or len(content)==0:
        return httpCodeStatus(message="内容不能为空")
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

@homeRouter.delete('/version/delete/{vid}',description="功能删除",summary="功能删除")
@limiter.limit("5/minute", error_message="请求过于频繁，请稍后再试!!!")
async def homeDelete(request: Request, vid:int,db: Session = Depends(getDbSession),

user:User=Depends(appToken.paseToken),
                     ):
    if not vid:
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