from fastapi import APIRouter,Depends,status,Request
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


userRouter = APIRouter()


@userRouter.post('/register',description="pc端注册",summary="pc端注册")
@limiter.limit("3/second", error_message="请求过于频繁，请稍后再试!!!")
def postPcRegistered(request: Request,userModel:UserInputBaseModel,db:Session = Depends(getDbSession)):
    account: str = userModel.account
    password: str = userModel.password
    if not account or not password:
        return httpCodeStatus(message="账号或密码不能为空")
    if len(account)<5 or len(account)>=30:
        return httpCodeStatus(message="账号长度必须在5-30之间")
    if len(password)<5 or len(password)>=30:
        return httpCodeStatus(message="密码长度必须在5-30之间")
    if not validate_password(password):
        return httpCodeStatus(message="密码格式不正确")
    t = ["admin"]
    if account not in t:
        return httpCodeStatus(message="pc端只能由特定账号进行注册操作,需要注册其他帐号的，请联系管理员")
    existing = db.query(User).filter(User.account == account).first()
    if existing is None:
        try:
            rTime = int(time.time())
            name =str(rTime) + account
            password = appToken.getHashPwd(password)
            result = User(
                account=account,
                password=password,
                name_str=name,
                login_type=1,
                uid=generate_uid(name_str=name, utype=0, login_type="pc"),
                user_type=0,
            )
            db.add(result)
            db.commit()
            db.flush()
            return httpCodeStatus(code=status.HTTP_200_OK, message="注册成功")
        except SQLAlchemyError as e:
            db.rollback()
            return httpCodeStatus(message="账号已存在")

@userRouter.post('/login',description="pc端登录",summary="pc端登录")
@limiter.limit("3/second", error_message="请求过于频繁，请稍后再试!!!")
def postPcLogin(request: Request,userModel:UserInputBaseModel,db:Session = Depends(getDbSession)):
    account: str = userModel.account
    password: str = userModel.password
    if not account or not password:
        return httpCodeStatus(message="账号或密码不能为空")
    if len(account)<5 or len(account)>=30:
        return httpCodeStatus(message="账号长度必须在5-30之间")
    if len(password)<5 or len(password)>=30:
        return httpCodeStatus(message="密码长度必须在5-30之间")
    if not validate_password(password):
        return httpCodeStatus(message="密码格式不正确")
    existing = db.query(User).filter(User.account == account).first()
    if existing is None:
        return httpCodeStatus(message="账号不存在")
    if not appToken.checkPassword(password, existing.password):
        return httpCodeStatus(message="密码错误")
    if existing.isStatus!=0:
        return httpCodeStatus(message="账号已被封禁或者删除,请联系管理员",)
    try:
        result=redis_db.get(key=account,dictKey='pc')
        if not result or result is None:
            data = {
                "id": existing.id,
                "uid": str(existing.uid),
                "phone": existing.phone,
                "account": existing.account,
                "createTime": str(existing.createTime),
                "updateTime": str(existing.updateTime),
                "userType": existing.user_type,
                "email": existing.email_str,
                "name": existing.name_str,
                "birthday": str(existing.birthday),
                "sex": existing.sex,
                "provinceCode": existing.province_code,
                "cityCode": existing.city_code,
                "districtCode": existing.district_code,
                "address": existing.address,
                "isStatus": existing.isStatus,
                "ip": existing.ip_v64,
                "vx": existing.vx_str,
                "qq": existing.qq_id,
                "github": existing.github_id,
                "juejin": existing.juejin_id,
                "card": existing.id_card,
                "lastLoginTime": existing.last_login_time,
                "browserType": existing.browser_type,
                "osType": existing.os_type,
                "loginType": existing.login_type,
                "loginDays": existing.login_days,
                "avatarUrl": existing.avatar,
                "game": existing.game_str,
                "job": existing.job_str,
                "company": existing.company_str,
                "marriageStatus": existing.marriage_status,
            }
            token = appToken.createToken(data, expires_delta)
            result: dict = {
                "token": token,
                "data": data
            }
            redis_db.set(key=account, dictKey='pc', value=result)
            return httpCodeStatus(code=status.HTTP_200_OK, message="登录成功", data=result)
        return httpCodeStatus(code=status.HTTP_200_OK, message="登录成功",
                              data=result)

    except SQLAlchemyError as e:
        return httpCodeStatus(message="登录失败")





@userRouter.post('/exchangeToken',description="pc端更新token",summary="pc端更新token")
@limiter.limit("3/second", error_message="请求过于频繁，请稍后再试!!!")
def postPcTokenExchange(request: Request,user: User = Depends(appToken.paseToken),
                        db:Session = Depends(getDbSession)):
    # 获取用户的token
    token = request.headers.get('Authorization')
    if not token or not user or token is None:
        return httpCodeStatus(message="用户信息已过期，无法更新用户信息", code=status.HTTP_401_UNAUTHORIZED)
    try:
        result=appToken.refreshToken(old_token=token)
        if not result or result is None:
            return httpCodeStatus(message="更新失败")
        data=db.query(User).filter(User.id == user.id).filter()
        result: dict = {
            "token": result,
            "data": data
        }
        redis_db.set(key=user.account, dictKey='pc', value=result)
        return httpCodeStatus(code=status.HTTP_200_OK, message="更新成功", data=result)
    except SQLAlchemyError as e:
        return httpCodeStatus(message="更新失败")