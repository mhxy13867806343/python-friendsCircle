from datetime import datetime

from slowapi.errors import RateLimitExceeded
from fastapi import Request, HTTPException, status
from slowapi import Limiter
from slowapi.util import get_remote_address
from fastapi.responses import JSONResponse

limiter = Limiter(key_func=get_remote_address)

async def rate_limit_exceeded_handler(request: Request, exc: RateLimitExceeded):
    # 返回一个自定义的错误信息，这里我们只是简单地使用了 exc.detail 提供的信息
    host:str=request.headers.get('host')
    return JSONResponse(
        status_code=exc.status_code,
        content={
             "message": f"请求过于频繁，请稍后再试!!!,来自{host}客户端地址被请求限制,请稍后重启吧!!!",
                "code": status.HTTP_400_BAD_REQUEST,
            "data":{},
            "success": False
        }
    )