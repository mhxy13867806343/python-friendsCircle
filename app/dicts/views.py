import time
import logging
from fastapi import APIRouter, Depends, status, Request
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from models.sysDict.model import SysDict, SysDictChild
from tools.appFnPublicValidateModelBool import validate_dict_input, handle_db_operation
from tools.appStatus import httpCodeStatus
from tools.appThrottling import limiter
from tools.apploggin import create_logger
from tools.db import getDbSession
from app.dicts.model import DictInputBaseChildModel, DictInputBaseModel
from tools.appOperation import getPaginatedList
# 初始化日志
logger = logging.getLogger(__name__)

# 创建字典路由
dictRouter = APIRouter()

create_logger(log_folder='logger',other_log="dict_log_")




@dictRouter.get('/list', description="pc端字典列表", summary="pc端字典列表")
@limiter.limit("10/minute", error_message="请求过于频繁，请稍后再试!!!")
async def getPcSysDictList(request: Request, isStatus: int = 0, name: str = '', pageNum: int = 1, pageSize: int = 20, db: Session = Depends(getDbSession)):
    d = {
        "key": name,
        "status": isStatus,
    }
    if d.get('status') != 0:
        return httpCodeStatus(message="已禁用或者删除的字典无法进行操作")
    result = getPaginatedList(model=SysDict, session=db, pageNum=pageNum, pageSize=pageSize, **d)
    return httpCodeStatus(code=status.HTTP_200_OK, message="获取成功", data=result)


@dictRouter.get('/child/list/{parentId}', description="pc端子字典列表", summary="pc端子字典列表")
@limiter.limit("10/minute", error_message="请求过于频繁，请稍后再试!!!")
async def getChildPcSysDictList(request: Request, parentId: int = 0, db: Session = Depends(getDbSession)):
    if not parentId:
        return httpCodeStatus(message="父级id不能为空")
    try:
        result = db.query(SysDictChild).filter(SysDictChild.dictId == parentId, SysDictChild.status == 0).all()
        return httpCodeStatus(code=status.HTTP_200_OK, message="获取成功", data=result)
    except SQLAlchemyError as e:
        logger.error(f"获取子字典列表失败: {e}")
        return httpCodeStatus(message="获取失败")


@dictRouter.post('/add', description="pc端字典新增", summary="pc端字典新增")
@limiter.limit("5/minute", error_message="请求过于频繁，请稍后再试!!!")
async def postPcSysDictAdd(request: Request, model: DictInputBaseModel, db: Session = Depends(getDbSession)):
    validation_error = validate_dict_input(model)
    if validation_error:
        return validation_error

    def db_func():
        existing_dict = db.query(SysDict).filter(SysDict.key == model.key).first()
        if existing_dict:
            if existing_dict.status != 0:
                raise ValueError("已禁用或者删除的字典无法进行操作")
            raise ValueError("字典名称已存在,请重新输入")
        new_dict = SysDict(key=model.key, value=model.value, desc=model.desc, status=0, operatorParent='admin')
        db.add(new_dict)
        db.commit()

    return handle_db_operation(db_func)


@dictRouter.post('/child/add', description="pc端子字典新增", summary="pc端子字典新增")
@limiter.limit("5/minute", error_message="请求过于频繁，请稍后再试!!!")
async def postChildPcSysDictAdd(request: Request, model: DictInputBaseChildModel, db: Session = Depends(getDbSession)):
    validation_error = validate_dict_input(model, is_child=True)
    if validation_error:
        return validation_error

    def db_func():
        existing_child = db.query(SysDictChild).filter(SysDictChild.key == model.key, SysDictChild.dictId == model.id).first()
        if existing_child:
            if existing_child.status != 0:
                raise ValueError("已禁用或者删除的子字典无法进行操作")
            raise ValueError("子字典名称已存在,请重新输入")
        new_child = SysDictChild(key=model.key, value=model.value, desc=model.desc, status=0, dictId=model.id, operatorChild='admin')
        db.add(new_child)
        db.commit()

    return handle_db_operation(db_func)


@dictRouter.put('/child/edit', description="pc端子字典编辑", summary="pc端子字典编辑")
@limiter.limit("5/minute", error_message="请求过于频繁，请稍后再试!!!")
async def updateChildPcSysDictAdd(request: Request, model: DictInputBaseChildModel, db: Session = Depends(getDbSession)):
    validation_error = validate_dict_input(model, is_child=True)
    if validation_error:
        return validation_error

    def db_func():
        child_to_update = db.query(SysDictChild).filter(SysDictChild.id == model.id).first()
        if not child_to_update:
            raise ValueError("子字典未找到,无法编辑")
        if child_to_update.status != 0:
            raise ValueError("已禁用或者删除的子字典无法进行操作")
        child_to_update.key = model.key
        child_to_update.value = model.value
        child_to_update.desc = model.desc
        child_to_update.updateTime = int(time.time())
        child_to_update.operatorChild = 'admin'
        db.commit()

    return handle_db_operation(db_func)


@dictRouter.delete('/child/delete', description="pc端子字典删除", summary="pc端子字典删除")
@limiter.limit("5/minute", error_message="请求过于频繁，请稍后再试!!!")
async def deleteChildPcSysDict(request: Request, model: DictInputBaseChildModel, db: Session = Depends(getDbSession)):
    if not model.id:
        return httpCodeStatus(message="子字典id不能为空")

    def db_func():
        child_to_delete = db.query(SysDictChild).filter(SysDictChild.id == model.id).first()
        if not child_to_delete:
            raise ValueError("子字典未找到,无法删除")
        if child_to_delete.status != 0:
            raise ValueError("已禁用或者删除的子字典无法进行操作")
        child_to_delete.status = 1
        child_to_delete.updateTime = int(time.time())
        db.commit()

    return handle_db_operation(db_func)


@dictRouter.put('/edit', description="pc端字典编辑", summary="pc端字典编辑")
@limiter.limit("5/minute", error_message="请求过于频繁，请稍后再试!!!")
async def updatePcSysDictAdd(request: Request, model: DictInputBaseModel, db: Session = Depends(getDbSession)):
    validation_error = validate_dict_input(model)
    if validation_error:
        return validation_error

    def db_func():
        dict_to_update = db.query(SysDict).filter(SysDict.id == model.id).first()
        if not dict_to_update:
            raise ValueError("字典名称未找到,无法编辑")
        if dict_to_update.status != 0:
            raise ValueError("已禁用或者删除的字典无法进行操作")
        dict_to_update.key = model.key
        dict_to_update.value = model.value
        dict_to_update.desc = model.desc
        dict_to_update.updateTime = int(time.time())
        dict_to_update.operatorParent = 'admin'
        db.commit()

    return handle_db_operation(db_func)


@dictRouter.delete('/delete', description="pc端字典删除", summary="pc端字典删除")
@limiter.limit("5/minute", error_message="请求过于频繁，请稍后再试!!!")
async def deletePcSysDict(request: Request, model: DictInputBaseModel, db: Session = Depends(getDbSession)):
    if not model.id:
        return httpCodeStatus(message="字典id不能为空")

    def db_func():
        dict_to_delete = db.query(SysDict).filter(SysDict.id == model.id).first()
        if not dict_to_delete:
            raise ValueError("字典名称未找到,无法删除")
        if dict_to_delete.status != 0:
            raise ValueError("已禁用或者删除的字典无法进行操作")
        dict_to_delete.status = 1
        dict_to_delete.updateTime = int(time.time())
        db.commit()

    return handle_db_operation(db_func)