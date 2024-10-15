from fastapi import APIRouter,Depends,status,Request
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session


from models.sysDict.model import SysDict, SysDictChild
from tools.appStatus import httpCodeStatus
from tools.appThrottling import limiter
from tools.db import getDbSession
from app.dicts.model import DictInputBaseChildModel,DictInputBaseModel
from tools.appOperation import getPaginatedList


dictRouter = APIRouter()

@dictRouter.get('/list',description="pc端字典列表",summary="pc端字典列表")
@limiter.limit("3/second", error_message="请求过于频繁，请稍后再试!!!")
async def getPcSysDictList(request: Request, isStatus: int = 0,name: str = '',pageNum: int = 1, pageSize: int = 20,db:Session = Depends(getDbSession)):
    try:
        d={
            "key":name,
            "status":isStatus,
        }
        result = getPaginatedList(model=SysDict, session=db, pageNum=pageNum, pageSize=pageSize,
                                    **d
                                  )
        return httpCodeStatus(code=status.HTTP_200_OK, message="获取成功", data=result)
    except SQLAlchemyError as e:
        return httpCodeStatus(code=status.HTTP_400_BAD_REQUEST, message="获取失败", data={})


@dictRouter.get('/child/list/{parentId}',description="pc端字典列表",summary="pc端字典列表")
@limiter.limit("3/second", error_message="请求过于频繁，请稍后再试!!!")
async def getChildPcSysDictList(request: Request, parentId:int=0,db:Session = Depends(getDbSession)):
    if not parentId:
        return httpCodeStatus(code=status.HTTP_400_BAD_REQUEST, message="父级id不能为空", data={})
    try:
        result = db.query(SysDictChild).filter(SysDictChild.dictId == parentId).all()
        return httpCodeStatus(code=status.HTTP_200_OK, message="获取成功", data=result)
    except SQLAlchemyError as e:
        return httpCodeStatus(code=status.HTTP_400_BAD_REQUEST, message="获取失败", data={})



@dictRouter.post('/add',description="pc端字典新增",summary="pc端字典新增")
@limiter.limit("3/second", error_message="请求过于频繁，请稍后再试!!!")
async def postPcSysDictAdd(request: Request, model:DictInputBaseModel,db:Session = Depends(getDbSession)):
    name = model.key
    value = model.value
    desc = model.desc
    if not name:
        return httpCodeStatus(code=status.HTTP_400_BAD_REQUEST, message="字典名称不能为空", data={})
    try:
        result = db.query(SysDict).filter(SysDict.key == name).first()
        if result:
            return httpCodeStatus(code=status.HTTP_400_BAD_REQUEST, message="字典名称已存在,请重新输入", data={})
        result=SysDict(key=name, value=value, desc=desc, status=0,children=[],
                       operatorParent='admin')
        db.add(result)
        db.commit()
        db.flush()
        return httpCodeStatus(code=status.HTTP_200_OK, message="新增成功", data={})
    except SQLAlchemyError as e:
        return httpCodeStatus(code=status.HTTP_400_BAD_REQUEST, message="字典名称已存在", data={})


@dictRouter.post('/child/add',description="pc端子字典新增",summary="pc端子字典新增")
@limiter.limit("3/second", error_message="请求过于频繁，请稍后再试!!!")
async def postPcChildSysDictAdd(request: Request, model:DictInputBaseModel,db:Session = Depends(getDbSession)):
    name = model.key
    value = model.value
    desc = model.desc
    id = model.id
    if not id:
        return  httpCodeStatus(code=status.HTTP_400_BAD_REQUEST, message="父级id不能为空", data={})
    if not name:
        return httpCodeStatus(code=status.HTTP_400_BAD_REQUEST, message="字典名称不能为空", data={})
    try:
        result = db.query(SysDictChild).filter(SysDictChild.id == id).first()
        if result and result.key == name:
            return httpCodeStatus(code=status.HTTP_400_BAD_REQUEST, message="字典名称已存在,请重新输入", data={})
        result=SysDictChild(key=name, value=value, desc=desc, status=0,dictId=id,
                       operatorChild='admin')
        db.add(result)
        db.commit()
        db.flush()
        return httpCodeStatus(code=status.HTTP_200_OK, message="新增子字典成功", data={})
    except SQLAlchemyError as e:
        return httpCodeStatus(code=status.HTTP_400_BAD_REQUEST, message="字典名称已存在", data={})