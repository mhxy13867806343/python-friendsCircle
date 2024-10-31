from typing import List

from fastapi import APIRouter, Depends, status, Request, UploadFile, File
from numpy.f2py.crackfortran import expectbegin
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session
import time
from datetime import datetime, timedelta, date
from tools import appToken
from app.user.model import UserInputBaseModel
from models.user.model import User
from tools.appFn import validate_password, generate_uid
from tools.appFnPublicValidateModelBool import uploadsSaveFile, get_date_folder, uploadValidateFile
from tools.appStatus import httpCodeStatus
from tools.appRedis import RedisDB
from tools.appThrottling import limiter
from tools.appUserTools import getAppUserInfo
from tools.appVariable import EXPIRE_TIME
from tools.db import getDbSession

redis_db = RedisDB()
expires_delta = timedelta(minutes=EXPIRE_TIME)


userRouter = APIRouter()


@userRouter.post('/register', description="pc端注册", summary="pc端注册")
@limiter.limit("3/second", error_message="请求过于频繁，请稍后再试!!!")
def postPcRegistered(request: Request, userModel: UserInputBaseModel, db: Session = Depends(getDbSession)):
    account: str = userModel.account
    password: str = userModel.password

    # 1. 检查账号和密码是否为空
    if not account or not password:
        return httpCodeStatus(message="账号或密码不能为空")

    # 2. 验证账号长度
    if len(account) < 5 or len(account) >= 30:
        return httpCodeStatus(message="账号长度必须在5-30之间")

    # 3. 验证密码长度
    if len(password) < 5 or len(password) >= 30:
        return httpCodeStatus(message="密码长度必须在5-30之间")

    # 4. 验证密码格式
    if not validate_password(password):
        return httpCodeStatus(message="密码格式不正确，提示:以字母开头，后面可以是字母、数字或特殊字符 _-.@，长度为 6-30 位")
    types=["admin"]
    if  (userModel.user_type==0) and (account not in types):
        return httpCodeStatus(message="用户类型不正确")
    # 6. 检查账号是否已经存在
    existing = db.query(User).filter(User.account == account).first()
    if existing is not None:
        return httpCodeStatus(message="账号已存在")
    # 7. 注册新用户
    try:
        ctime = int(time.time())
        name = str(ctime) + account
        password = appToken.getHashPwd(password)
        user_info = getAppUserInfo(request)
        # 直接访问 user_info 中的各个字段
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
            user_type=userModel.user_type,
            ip_v64=client_ip,
            is_login=0
        )
        db.add(result)
        db.commit()
        db.flush()
        return httpCodeStatus(code=status.HTTP_200_OK, message="注册成功")
    except SQLAlchemyError as e:
        db.rollback()
        return httpCodeStatus(message="服务器内部错误")

def saveUserInfo(account:str,existing:User):
    data = {
        "id": existing.id,
        "uid": str(existing.uid),
        "phone": existing.phone,
        "account": existing.account,
        "create_time": str(existing.create_time),
        "update_time": str(existing.update_time),
        "user_type": existing.user_type,
        "email_str": existing.email_str,
        "name_str": existing.name_str,
        "birthday": str(existing.birthday),
        "sex": existing.sex,
        "province_code": existing.province_code,
        "city_code": existing.city_code,
        "district_code": existing.district_code,
        "address_str": existing.address_str,
        "is_status": existing.is_status,
        "ip_v64": existing.ip_v64,
        "vx_id": existing.vx_id,
        "qq_id": existing.qq_id,
        "github_id": existing.github_id,
        "juejin_id": existing.juejin_id,
        "id_card": existing.id_card,
        "last_login_time": existing.last_login_time,
        "browser_type": existing.browser_type,
        "os_type": existing.os_type,
        "login_type": existing.login_type,
        "login_days": existing.login_days,
        "avatar_url": existing.avatar_url,
        "game_str": existing.game_str,
        "job_str": existing.job_str,
        "company_str": existing.company_str,
        "marriage_status": existing.marriage_status,
        "is_login": existing.is_login
    }
    # 将数据写入 Redis 缓存
    setRedisInfo(account,data)
    return data

def get_user_data(account: str, db: Session):
    try:
        # 1. 尝试从 Redis 中获取数据
        result = redis_db.get(key=account)
        if result:
            return result  # 这里直接返回 Redis 缓存的数据

        # 2. Redis 中没有数据，从数据库中获取
        existing = db.query(User).filter(User.account == account).first()
        if existing is None:
            return None  # 如果数据库也没有找到，则返回 None

        # 3. 将数据库获取到的数据保存到 Redis，并返回
        data = saveUserInfo(account, existing)
        return data
    except SQLAlchemyError as e:
        # 记录错误日志并返回错误状态
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
        return httpCodeStatus(message="密码格式不正确,提示:以字母开头，后面可以是字母、数字或特殊字符 _-.@，长度为 6-30 位")
    data = get_user_data(account, db)
    if not data:
        user = db.query(User).filter(User.account == account).first()
        if not user:
            return httpCodeStatus(message="账号不存在")
        data=saveUserInfo(account,user)
    if not appToken.checkPassword(password, data['password']):
        return httpCodeStatus(message="密码错误")
    if data.get("is_status") != 0:
        return httpCodeStatus(message="账号已被封禁或者删除,请联系管理员")

        # 4. 处理登录天数
    data = update_login_status(data)
    #获取上次登录时间 第一次登陆，肯定是注册的时间了
        # 4. 获取上次登录时间并更新为当前时间
    token = appToken.createToken(data, expires_delta)
    result = {
        "token": token,
        "data": data
    }
    setRedisInfo(account,data)
    return httpCodeStatus(code=status.HTTP_200_OK, message="登录成功", data=result)


@userRouter.get('/info',description="获取用户信息",summary="获取用户信息")
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
            result = update_login_status(result)
            return httpCodeStatus(code=status.HTTP_200_OK, message="获取成功", data=result)
        return httpCodeStatus(message="用户信息已过期，无法获取用户信息", code=h401)
    except SQLAlchemyError as e:
        return httpCodeStatus(message="获取用户信息失败", code=h401)

@userRouter.post('/update',description="更新用户信息",summary="更新用户信息")
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
        result['update_time']=model.update_time or ""
        result['email_str']=model.email_str or ""
        result['name_str']=model.name_str or ""
        result['birthday']=model.birthday
        result['sex']=model.sex  or ""
        result['province_code']=model.province_code or ""
        result['city_code']=model.city_code or ""
        result['district_code']=model.district_code or ""
        result['address_str']=model.address_str or ""
        result['qq_id']=model.qq_id or ""
        result['vx_id']=model.vx_id or ""
        result['github_id']=model.github_id or ""
        result['juejin_id']=model.juejin_id or ""
        result['avatar_url']=model.avatar_url  or ""
        result['game_str']=model.game_str or ""
        result['job_str']=model.job_str or ""
        result['company_str']=model.company_str or ""
        result['marriage_status']=model.marriage_status or ""
        result['id_card']=model.id_card or ""
        # 更新数据库
        db.query(User).filter(User.id == user.id).update(result)
        db.commit()
        # 更新 Redis 缓存
        setRedisInfo(user.account,result)
        return httpCodeStatus(code=status.HTTP_200_OK, message="更新成功")
    except SQLAlchemyError as e:
        db.rollback()
        return httpCodeStatus(message="更新用户信息失败", code=status.HTTP_401_UNAUTHORIZED)
# 用于刷新 Token 请求时的处理

@userRouter.post('/logout', description="退出登录", summary="退出登录")
@limiter.limit("3/second", error_message="请求过于频繁，请稍后再试!!!")
def postPcLogout(request: Request, user: User = Depends(appToken.paseToken)):
    redis_db.delete(key=user.account)
    return httpCodeStatus(code=status.HTTP_200_OK, message="退出成功")





# 1. 上传接口 - 头像上传，仅支持单文件上传
@userRouter.post('/upload/avatar', description='用户头像上传接口',summary="用户头像上传接口")
@limiter.limit("3/second", error_message="请求过于频繁，请稍后再试!!!")
async def upload_avatar(
        request: Request,
    file: UploadFile = File(...),
user: User = Depends(appToken.paseToken),
    db:Session = Depends(getDbSession),
):
    """
    用户头像上传接口，仅支持上传一个文件。
    """
    # 获取当前用户信息
    result=db.query(User).filter(User.id ==user).first()
    if not result:
        return httpCodeStatus(message="不能进行上传操作,请重新登录", code=status.HTTP_401_UNAUTHORIZED)
    # 文件保存路径（用户头像目录），日期文件夹中
    try:
        date_folder = get_date_folder()
        destination_path = f"{result.id}-{result.uid}-{result.name_str}/{date_folder}/avatar/{file.filename}"
        content=await uploadValidateFile(file,["jpg","png","jpeg"])
        if not content:
            return
        try:
            saved_path = await uploadsSaveFile(file, destination_path)
            data = {
                "avatar_url": file.filename,
                "path": saved_path
            }
            # 更新用户头像信息
            result.avatar_url = file.filename
            db.commit()
            # 更新 Redis 缓存
            setRedisInfo(result.account,result)
            db.refresh(result)
            return httpCodeStatus(code=status.HTTP_200_OK, message="文件上传成功", data=data)
        except SQLAlchemyError as e:
            db.rollback()
            return httpCodeStatus(message="文件上传失败", code=status.HTTP_500_INTERNAL_SERVER_ERROR)
    except SQLAlchemyError as e:
        return httpCodeStatus(message="数据库操作失败", code=status.HTTP_500_INTERNAL_SERVER_ERROR)
    except Exception as e:
        return httpCodeStatus(message="文件上传失败", code=status.HTTP_500_INTERNAL_SERVER_ERROR)

# 2. 上传接口 - 公共上传，支持批量上传
@userRouter.post('/upload/public',description='公共批量上传接口', summary="公共批量上传接口")
async def upload_public_files( request: Request,files: List[UploadFile] = File(...)):
    """
    允许任何人使用的公共上传接口，支持批量上传文件。
    """
    upload_results = {"success": [], "failed": []}
    date_folder = get_date_folder()

    for file in files:

        validation = await uploadValidateFile(file, ["jpg", "png", "jpeg"])
        if validation["code"] != 200:
            upload_results["failed"].append({"file_name": file.filename, "reason": validation["message"]})
            continue
        destination_path = f"{date_folder}/public/{file.filename}"
        saved_path = await uploadsSaveFile(file, destination_path)
        upload_results["success"].append({"file_url": file.filename, "path": saved_path})

    return httpCodeStatus(code=status.HTTP_200_OK, message="文件上传成功", data=upload_results)

# 3. 上传接口 - 用户上传，支持批量上传
@userRouter.post('/upload/user', summary="用户批量上传接口")
async def upload_user_files(
        request: Request,
    files: List[UploadFile] = File(...),
        user: User = Depends(appToken.paseToken),
        db: Session = Depends(getDbSession),
):
    result=db.query(User).filter(User.id ==user).first()
    if not result:
        return httpCodeStatus(message="不能进行上传操作,请重新登录", code=status.HTTP_401_UNAUTHORIZED)

    # 批量处理文件上传
    upload_results = {"success": [], "failed": []}
    date_folder = get_date_folder()

    for file in files:
        content = await uploadValidateFile(file, ["jpg", "png", "jpeg"])
        if not content:
            return
        # 文件保存到 upload/yyyy-mm-dd/{username} 目录中
        destination_path = f"{result.id}-{result.uid}-{result.name_str}/{date_folder}/files/{file.filename}"
        saved_path = await uploadsSaveFile(file, destination_path)
        if isinstance(saved_path, str):
            upload_results["success"].append({"file_name": file.filename, "path": saved_path})
        else:
            upload_results["failed"].append({"file_name": file.filename, "reason": "文件保存失败"})
    return httpCodeStatus(code=status.HTTP_200_OK, message="文件上传成功", data=upload_results)


# 获取请求头中的 token
def get_headers_token(request: Request,user: User = Depends(appToken.paseToken)):
    # 获取用户的 token
    token = request.headers.get('Authorization')
    if not token or not user or token is None:
        return httpCodeStatus(message="用户信息已过期，无法更新用户信息", code=status.HTTP_401_UNAUTHORIZED)
    return token
def setRedisInfo(key,value)->None:
    redis_db.set(key=key, value=value)


def is_today_timestamp(timestamp: int) -> bool:
    """
    判断给定的 Unix 时间戳是否是今天
    :param timestamp: Unix 时间戳
    :return: 如果是今天返回 True，否则返回 False
    """
    # 将时间戳转换为 datetime 对象
    given_date = datetime.fromtimestamp(timestamp).date()

    # 获取当前日期
    current_date = date.today()

    # 判断是否是今天
    return given_date == current_date



# 更新登录状态 比如用户登录，情况
def update_login_status(data: dict) -> dict:
    try:
        login_days = data.get('login_days', 0)
        last_login_time = data.get("last_login_time")

        if last_login_time and is_today_timestamp(last_login_time):
            is_login = 1
        else:
            is_login = 0
        data["is_login"] = is_login
        if data["is_login"] == 0:
            data['login_days'] = login_days + 1
            data["last_login_time"] = int(datetime.now().timestamp())
            data["is_login"] = 1
            # 生成 30 60 90 120 150 180 210 240 270 300 330 360
        day30 = [x * 30 for x in range(1, 13)]
        if login_days <= day30[-1]:
            if login_days in day30:
                return httpCodeStatus(message="您已经连续登录超过" + str(login_days) + "天!!!")
        # 每3年提示一次
        if login_days % 3 * 365 == 0:
            return httpCodeStatus(message="您已经连续登录超过" + str(login_days) + "天!!!")
        # 获取上次登录时间 第一次登陆，肯定是注册的时间了
        # 4. 获取上次登录时间并更新为当前时间
        return data
    except Exception as e:
        return httpCodeStatus(message="更新登录状态失败")
    except SQLAlchemyError as e:
        return httpCodeStatus(message="更新登录状态失败")
