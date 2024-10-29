from datetime import datetime
from pydantic import BaseModel
from typing import Optional
from pydantic import Field
class UserInputBaseModel(BaseModel):
    uid: Optional[str] = None
    user_type: Optional[int] = 0
    isStatus: Optional[int] = 0
    createTime: Optional[int] =  Field(default_factory=lambda: int(datetime.now().timestamp()))
    updateTime: Optional[int] = Field(default_factory=lambda: int(datetime.now().timestamp()))
    id: Optional[int] = None
    account: Optional[str] = None
    password: Optional[str] = None
    name_str: Optional[str] = None
    sex: Optional[int] =0
    birthday: Optional[int] =  Field(default_factory=lambda: int(datetime.now().timestamp()))  # 使用整数时间戳
    phone: Optional[str] = None
    email_str: Optional[str] = None
    address: Optional[str] = None
    province_code: Optional[str] = None
    city_code: Optional[str] = None
    district_code: Optional[str] = None
    ip_v64: Optional[str] = None
    vx_id: Optional[str] = None
    qq_id: Optional[str] = None
    juejin_id: Optional[str] = None
    github_id: Optional[str] = None
    id_card: Optional[str] = None
    last_login_time: Optional[int] = Field(default_factory=lambda: int(datetime.now().timestamp()))  # 使用整数时间戳
    browser_type: Optional[str] = 'chrome'
    os_type: Optional[str] = 'windows'
    login_type: Optional[int] = 0
    login_days: Optional[int] = 0
    avatar: Optional[str] = None
    game_str: Optional[str] = None
    job_str: Optional[str] = None
    company_str: Optional[str] = None
    marriage_status: Optional[int] = 0