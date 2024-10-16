from fastapi import status
from typing import Dict, Any, Optional, Union


def httpCodeStatus(
        code: int = status.HTTP_400_BAD_REQUEST,
        message: str = "获取失败",
        data: Optional[Union[dict, list]] = None
) -> dict:
    if data is None:
        data = {}

    return {
        "code": code,
        "msg": message,
        "data": data,  # 确保返回的 data 保持原始的类型
        "success": False if code >= 400 else True
    }