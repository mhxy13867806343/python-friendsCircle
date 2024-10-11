from fastapi import APIRouter,Depends,status
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session
import time
from datetime import datetime, timedelta
from tools import appToken
from app.user.model import UserInputBaseModel
from models.user.model import User
from tools.appStatus import httpCodeStatus
from tools.appRedis import RedisDB
from tools.appVariable import EXPIRE_TIME
from tools.db import getDbSession

redis_db = RedisDB()
expires_delta = timedelta(minutes=EXPIRE_TIME)


router = APIRouter()







@router.post('/registered',description="h5/pc端注册",summary="h5/pc端注册")
def registered(userModel:UserInputBaseModel,reg_type:str="pc",db:Session = Depends(getDbSession)):
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
        rTime = int(time.time())
        name=str('--')+str(rTime)+str(account)+str('--')
        password = appToken.getHashPwd(password)

        resultSql = User(
            id=None,
            uid=None,
            phone=None,
            account=account,
            password=password,
            name_str=name,
            email_str=None,
            createTime=datetime.now(),
            updateTime=datetime.now(),
            birthday=None,
            sex=None,
            province_code=None,
            city_code=None,
            district_code=None,
            address=None,
            isStatus=0,
            ip_v64=None,
            vx_id=None,
            qq_id=None,
            github_id=None,
            juejin_id=None,
            id_card=None,
            last_login_time=None,
            browser_type=None,
            os_type=None,
            login_type="h5",
            login_days=0,
            avatar=None,
        )
        db.add(resultSql)
        db.commit()
        db.flush()
        return httpCodeStatus(code=status.HTTP_200_OK, message="注册成功")
    return httpCodeStatus(message="账号已存在")