import json
import time
import logging
from typing import List

from fastapi import APIRouter, Depends, status, Request
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session
from fastapi import status as httpStatus
from models.pcds.model import Province, City, District, Street
from tools.appFnPublicValidateModelBool import validate_dict_input, handle_db_operation
from tools.appStatus import httpCodeStatus
from tools.appThrottling import limiter
from tools.apploggin import create_logger
from app.pcds.model import ProvinceModel, CityModel, DistrictModel, StreetModel
from tools.db import getDbSession
from app.pcds.model import PCDSModel
from tools.appOperation import getPaginatedList, getFilteredList

# 创建字典路由
pcdsRouter = APIRouter()



@pcdsRouter.get('/province', description="省列表", summary="省列表")
@limiter.limit("10/minute")
async def get_cities_by_province_code(request: Request,code: str="",name: str="",db: Session = Depends(getDbSession)):
    data={
        "code": code,
        "name": name
    }
    cities = getFilteredList(model=Province, session=db, **data)
    return httpCodeStatus(code=httpStatus.HTTP_200_OK, data=cities, message="获取成功")

@pcdsRouter.get('/city', description="市列表", summary="市列表")
@limiter.limit("10/minute")
async def get_districts_by_city_code(request: Request,code: str="",db: Session = Depends(getDbSession)):
    if not code:
        return httpCodeStatus(code=httpStatus.HTTP_400_BAD_REQUEST, message="市id不能为空")
    cities = db.query(City).join(Province).filter(Province.code == code).all()
    return httpCodeStatus(code=httpStatus.HTTP_200_OK, data=cities, message="获取成功")

@pcdsRouter.get('/district', description="区列表", summary="区列表")
@limiter.limit("10/minute")
def get_districts_by_city_code(request: Request, code: str="",db: Session = Depends(getDbSession)):
    if not code:
        return httpCodeStatus(code=httpStatus.HTTP_400_BAD_REQUEST, message="区id不能为空")
    districts = db.query(District).join(City).filter(City.code == code).all()
    return httpCodeStatus(code=httpStatus.HTTP_200_OK, data=districts, message="获取成功")
@pcdsRouter.get('/street', description="街道列表", summary="街道列表")
@limiter.limit("10/minute")
def get_streets_by_district_code(request: Request, code: str="",db: Session = Depends(getDbSession)):
    if not code:
        return httpCodeStatus(code=httpStatus.HTTP_400_BAD_REQUEST, message="街道id不能为空")
    streets = db.query(Street).join(District).filter(District.code ==code).all()
    return httpCodeStatus(code=httpStatus.HTTP_200_OK, data=streets, message="获取成功")