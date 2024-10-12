from fastapi import APIRouter,Depends,status
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session
import time
from datetime import datetime, timedelta
from tools import appToken
from app.user.model import UserInputBaseModel
from models.user.model import User
from tools.appFn import validate_password, generate_uid
from tools.appStatus import httpCodeStatus
from tools.appRedis import RedisDB
from tools.appThrottling import limiter
from tools.appVariable import EXPIRE_TIME
from tools.db import getDbSession

redis_db = RedisDB()
expires_delta = timedelta(minutes=EXPIRE_TIME)


router = APIRouter()


@router.post('/pcreg',description="pc端注册",summary="pc端注册")
@limiter.limit("1/minute", error_message="请求过于频繁，请稍后再试!!!")
def pcRegistered(userModel:UserInputBaseModel,db:Session = Depends(getDbSession)):
    account: str = userModel.account
    password: str = userModel.password
    if not account or not password:
        return httpCodeStatus(message="账号或密码不能为空")
    if len(account)<6 or len(account)>=30:
        return httpCodeStatus(message="账号长度必须在6-30之间")
    if len(password)<6 or len(password)>=30:
        return httpCodeStatus(message="密码长度必须在6-30之间")
    if not validate_password(password):
        return httpCodeStatus(message="密码格式不正确")
    t = ["admin"]
    if account not in t:
        return httpCodeStatus(message="pc端只能由特定账号进行注册操作,需要注册其他帐号的，请联系管理员")
    existing = db.query(User).filter(User.account == account).first()
    if existing is None:
        try:
            rTime = int(time.time())
            name = str('--') + str(rTime) + str(account) + str('--')
            password = appToken.getHashPwd(password)
            result = User(
                account=account,
                password=password,
                name_str=name,
                login_type="pc",
                uid=generate_uid(name_str=name, utype=0, login_type="pc"),
            )
            db.add(result)
            db.commit()
            db.flush()
            return httpCodeStatus(code=status.HTTP_200_OK, message="注册成功")
        except SQLAlchemyError as e:
            db.rollback()
            return httpCodeStatus(message="账号已存在")






@router.post('/registered',description="h5/pc端注册",summary="h5/pc端注册")
def h5Registered(userModel:UserInputBaseModel,reg_type:str="pc",db:Session = Depends(getDbSession)):
    account:str=userModel.account
    password:str=userModel.password
    if not account or not password:
        return httpCodeStatus(message="账号或密码不能为空", data={})
    if reg_type=='pc':
        t = ["admin"]
        if reg_type not in t:
            return httpCodeStatus(message="pc端只能由特定账号进行注册操作,需要注册其他帐号的，请联系管理员")
    existing = db.query(User).filter(User.account == account).first()
    if existing is None:
        try:
            rTime = int(time.time())
            name = str('--') + str(rTime) + str(account) + str('--')
            password = appToken.getHashPwd(password)
            result = User(
                account=account,
                password=password,
                name_str=name,
                login_type="pc",
                uid=generate_uid(name_str=name, utype=0, login_type="pc"),
            )
            db.add(result)
            db.commit()
            db.flush()
            return httpCodeStatus(code=status.HTTP_200_OK, message="注册成功")
        except SQLAlchemyError as e:
            db.rollback()
            return httpCodeStatus(message="账号已存在")
