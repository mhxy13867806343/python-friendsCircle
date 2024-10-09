
from pydantic import BaseModel
from typing import Optional, List, Dict, Any, Union, TypeVar, Type, Callable, cast
class UserInputBaseModel(BaseModel):
    uid:Optional[str] = None
    isStatus:Optional[int] = None
    createTime:Optional[str] = None
    updateTime:Optional[str] = None
    id:Optional[int] = None
    account:Optional[str] = None
    password:Optional[str] = None
    name_str:Optional[str] = None
    sex:Optional[int] = None
    birthday:Optional[str] = None
    phone:Optional[str] = None
    email_str:Optional[str] = None
    address:Optional[str] = None
    province_code:Optional[int] = None
    city_code:Optional[int] = None
    district_code:Optional[int] = None
    ip_v64:Optional[str] = None
    vx_id:Optional[str] = None
    qq_id:Optional[str] = None
    juejin_id:Optional[str] = None
    github_id:Optional[str] = None
    id_card:Optional[str] = None
    last_login_time:Optional[str] = None
    browser_type:Optional[str] = None
    os_type:Optional[str] = None
    login_type:Optional[int] = None
    login_days:Optional[int] = None
    avatar:Optional[str] = None
    game_str:Optional[str] = None
    job_str:Optional[str] = None
    company_str:Optional[str] = None
    marriage_status:Optional[int] = None