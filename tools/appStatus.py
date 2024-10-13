from fastapi import  status

from typing import Dict, Any, Optional
def httpCodeStatus(code: int = status.HTTP_400_BAD_REQUEST, message: str = "获取失败", data: Optional[dict] = None) -> dict:
    if data is None:
        data = {}
    return {
        "code": code,
        "msg": message,
        "data": data,
        "success": False if code >= 400 else True
    }