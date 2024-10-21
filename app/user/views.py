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
from tools.appUserTools import getAppUserInfo
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
            user_info = getAppUserInfo(request)
            # 你可以直接访问 user_info 中的各个字段
            browser_type = user_info['browser_type']
            os_type = user_info['os_type']
            login_type = user_info['login_type']
            client_ip = user_info['client_ip']
            result = User(
                account=account,
                password=password,
                name_str=name,
                browser_type=browser_type,
                os_type=os_type,
                login_type=login_type,
                uid=generate_uid(name_str=name, utype=0, login_type="pc"),
                user_type=0,
                ip_v64=client_ip,
            )
            db.add(result)
            db.commit()
            db.flush()
            return httpCodeStatus(code=status.HTTP_200_OK, message="注册成功")
        except SQLAlchemyError as e:
            db.rollback()
            return httpCodeStatus(message="账号已存在")


def get_user_data(account:str,db:Session):
    try:
        # 从 Redis 中获取数据
        result = redis_db.get(key=account)
        if isinstance(result, dict):
            return result
        # 如果 Redis 中没有数据，从数据库对象生成字典
        existing = db.query(User).filter(User.account == account).first()
        if existing is None:
            return None
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
        # 将数据写入 Redis 缓存
        redis_db.set(key=account,  value=data)
        return data
    except SQLAlchemyError as e:
        return httpCodeStatus(message="获取用户信息失败", code=status.HTTP_401_UNAUTHORIZED)


@userRouter.post('/login', description="pc端登录", summary="pc端登录")
@limiter.limit("3/second", error_message="请求过于频繁，请稍后再试!!!")
def postPcLogin(request: Request, userModel: UserInputBaseModel, db: Session = Depends(getDbSession)):
    account: str = userModel.account
    password: str = userModel.password
    if not account or not password:
        return httpCodeStatus(message="账号或密码不能为空")
    if len(account) < 5 or len(account) >= 30:
        return httpCodeStatus(message="账号长度必须在5-30之间")
    if len(password) < 5 or len(password) >= 30:
        return httpCodeStatus(message="密码长度必须在5-30之间")
    if not validate_password(password):
        return httpCodeStatus(message="密码格式不正确")
    data = get_user_data(account, db)
    if data is None:
        return httpCodeStatus(message="账号不存在或登录失败")
    if not appToken.checkPassword(password, data['password']):
        return httpCodeStatus(message="密码错误")
    if data['isStatus'] != 0:
        return httpCodeStatus(message="账号已被封禁或者删除,请联系管理员")

    token = appToken.createToken(data, expires_delta)
    result = {
        "token": token,
        "data": data
    }
    return httpCodeStatus(code=status.HTTP_200_OK, message="登录成功", data=result)


@userRouter.get('/info',description="pc端获取用户信息",summary="pc端获取用户信息")
@limiter.limit("3/second", error_message="请求过于频繁，请稍后再试!!!")
def getUserInfo(request: Request,user: User = Depends(appToken.paseToken),
                        db:Session = Depends(getDbSession)):
    # 获取用户的token
    h401=status.HTTP_401_UNAUTHORIZED
    token = get_headers_token(request, user)
    if not token:
        return httpCodeStatus(message="用户信息已过期，无法获取用户信息", code=h401)
    try:
        result=redis_db.parse_redis_result(key=user.account)
        if result:
            return httpCodeStatus(code=status.HTTP_200_OK, message="获取成功", data=result)
        return httpCodeStatus(message="用户信息已过期，无法获取用户信息", code=h401)
    except SQLAlchemyError as e:
        return httpCodeStatus(message="获取用户信息失败", code=h401)

@userRouter.put('/info',description="pc端更新用户信息",summary="pc端更新用户信息")
@limiter.limit("3/second", error_message="请求过于频繁，请稍后再试!!!")
def putUserInfo(request: Request, model: UserInputBaseModel,user: User = Depends(appToken.paseToken),
                        db:Session = Depends(getDbSession)):
    token = get_headers_token(request,user)
    if not token:
        return httpCodeStatus(message="用户信息已过期，无法更新用户信息", code=status.HTTP_401_UNAUTHORIZED)
    try:
        result = get_user_data(user.account, db)
        if result is None:
            return httpCodeStatus(message="用户信息获取失败")
        # 更新用户信息
        result['phone']=model.phone   or ""
        result['updateTime']=model.updateTime or ""
        result['email_str']=model.email_str or ""
        result['name_str']=model.name_str or ""
        result['birthday']=model.birthday
        result['sex']=model.sex  or ""
        result['province_code']=model.province_code or ""
        result['city_code']=model.city_code or ""
        result['district_code']=model.district_code or ""
        result['address']=model.address or ""
        result['qq_id']=model.qq_id or ""
        result['vx_id']=model.vx_id or ""
        result['github_id']=model.github_id or ""
        result['juejin_id']=model.juejin_id or ""
        result['avatar']=model.avatar  or ""
        result['game_str']=model.game_str or ""
        result['job_str']=model.job_str or ""
        result['company_str']=model.company_str or ""
        result['marriage_status']=model.marriage_status or ""
        result['id_card']=model.id_card or ""
        # 更新数据库
        db.query(User).filter(User.id == user.id).update(result)
        db.commit()
        # 更新 Redis 缓存
        redis_db.set(key=user.account,  value=result)
        return httpCodeStatus(code=status.HTTP_200_OK, message="更新成功")
    except SQLAlchemyError as e:
        db.rollback()
        return httpCodeStatus(message="更新用户信息失败", code=status.HTTP_401_UNAUTHORIZED)
# 用于刷新 Token 请求时的处理
@userRouter.post('/exchangeToken', description="pc端更新token", summary="pc端更新token")
@limiter.limit("3/second", error_message="请求过于频繁，请稍后再试!!!")
def postPcTokenExchange(request: Request, user: User = Depends(appToken.paseToken),
                        db: Session = Depends(getDbSession)):
    # 获取用户的 token
    token = get_headers_token(request,user)
    try:
        # 刷新 Token
        new_token = appToken.refreshToken(old_token=token)
        if not new_token:
            return httpCodeStatus(message="更新失败")

        # 从 Redis 或数据库获取最新用户信息
        data = get_user_data( user.account, db)
        if data is None:
            return httpCodeStatus(message="用户信息获取失败")

        # 更新 Redis 中的用户信息，确保缓存同步更新
        data['lastLoginTime'] = str(datetime.utcnow())
        redis_db.set(key=user.account,  value=data)

        result = {
            "token": new_token,
            "data": data
        }
        return httpCodeStatus(code=status.HTTP_200_OK, message="更新成功", data=result)
    except SQLAlchemyError as e:
        return httpCodeStatus(message="更新失败")






# 获取请求头中的 token
def get_headers_token(request: Request,user: User = Depends(appToken.paseToken)):
    # 获取用户的 token
    token = request.headers.get('Authorization')
    if not token or not user or token is None:
        return httpCodeStatus(message="用户信息已过期，无法更新用户信息", code=status.HTTP_401_UNAUTHORIZED)
    return token