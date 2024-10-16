# 字典公共验证函数
import logging
from typing import Callable
from fastapi import  status
from sqlalchemy.exc import SQLAlchemyError

from tools.appFn import validate_format
from tools.appStatus import httpCodeStatus

logger = logging.getLogger(__name__)
def validate_dict_input(model, is_child: bool = False):
    """公共验证函数，用于验证字典输入数据"""
    if is_child and not model.id:
        return httpCodeStatus(message="字典id不能为空")
    if not model.key:
        return httpCodeStatus(message="字典名称不能为空")
    if not validate_format(model.key):
        return httpCodeStatus(message="字典名字只能是字母或者数字，不能包含特殊字符或者中文", data={})
    if not model.value:
        return httpCodeStatus(message="字典值不能为空")
    return None
def handle_db_operation(db_func: Callable[[], None]):
    if not db_func:
        return httpCodeStatus(message="数据库操作失败")
    """数据库操作处理器，简化错误处理逻辑"""
    try:
        db_func()
        return httpCodeStatus(code=status.HTTP_200_OK, message="操作成功", data={})
    except SQLAlchemyError as e:
        logger.error(f"数据库操作失败: {e}")
        return httpCodeStatus(message=f"操作失败: {str(e)}")

