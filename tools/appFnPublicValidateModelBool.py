# 字典公共验证函数
import io
import logging
import os
from datetime import datetime
from typing import Callable, List
from fastapi import status, UploadFile
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
# 通用文件保存函数
async def uploadsSaveFile(file: UploadFile, url: str) -> str:
    if not url:
        return httpCodeStatus(message="文件保存路径不能为空", code=status.HTTP_400_BAD_REQUEST)
    try:
        # 设置根保存路径
        base_upload_path = "upload"
        if not os.path.exists(base_upload_path):
            os.makedirs(base_upload_path)
        # 将目标路径拼接到根保存路径下
        full_destination_path = os.path.join(base_upload_path, url)

        # 创建保存路径的目录（如果不存在）
        os.makedirs(os.path.dirname(full_destination_path), exist_ok=True)
        # 重置文件指针到开头位置，以防止之前被消费
        file.file.seek(0)

        # 读取文件内容
        content = await file.read()
        # 读取并保存文件
        with open(full_destination_path, "wb") as f:
            f.write(content)
            # 打印/记录保存路径以用于调试
        print(f"File saved at: {full_destination_path}")
        return f"/{base_upload_path}/{url}"
    except SQLAlchemyError as e:
        return httpCodeStatus(message="文件保存失败", code=status.HTTP_500_INTERNAL_SERVER_ERROR)
    except Exception as e:
        return httpCodeStatus(message=f"文件保存失败: {e}", code=status.HTTP_500_INTERNAL_SERVER_ERROR)
def get_date_folder() -> str:
    return datetime.now().strftime("%Y-%m-%d")


# 文件验证函数
# 文件验证函数：验证文件类型
async def uploadValidateFile(file: UploadFile, extensions: List[str]=None) -> dict:
    if extensions is None:
        allowed_extensions=[".jpg", ".jpeg", ".png"]
    # 验证文件扩展名
    if not any(file.filename.lower().endswith(ext) for ext in allowed_extensions):
        return {
            "code": 400,
            "message": f"文件类型错误，仅支持以下格式: {', '.join(allowed_extensions)}"
        }

    content = await file.read()
    if not content:
        return httpCodeStatus(message="文件内容为空", code=status.HTTP_400_BAD_REQUEST)
    # 重置文件指针以供后续使用
    file.file.seek(0)
    return httpCodeStatus(code=status.HTTP_200_OK, message="文件验证通过", data={
        "content": content,
    })


# 文件保存函数
async def uploadsSaveFile(file: UploadFile, url: str) -> str:
    if not url:
        return httpCodeStatus(message="文件保存路径不能为空", code=status.HTTP_400_BAD_REQUEST)
    try:
        # 设置根保存路径
        base_upload_path = "upload"
        if not os.path.exists(base_upload_path):
            os.makedirs(base_upload_path)

        # 将目标路径拼接到根保存路径下
        full_destination_path = os.path.join(base_upload_path, url)

        # 创建保存路径的目录（如果不存在）
        os.makedirs(os.path.dirname(full_destination_path), exist_ok=True)

        # 读取并保存文件
        content = await file.read()
        with open(full_destination_path, "wb") as f:
            f.write(content)

        print(f"File saved at: {full_destination_path}")
        return f"/{base_upload_path}/{url}"

    except SQLAlchemyError:
        return httpCodeStatus(message="文件保存失败", code=status.HTTP_500_INTERNAL_SERVER_ERROR)
    except Exception as e:
        return httpCodeStatus(message=f"文件保存失败: {e}", code=status.HTTP_500_INTERNAL_SERVER_ERROR)