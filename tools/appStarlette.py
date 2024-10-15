from typing import Optional
from fastapi import Request, HTTPException, BackgroundTasks
from fastapi.middleware import Middleware
from fastapi.middleware.cors import CORSMiddleware  # CORS
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.middleware.httpsredirect import HTTPSRedirectMiddleware
from fastapi.responses import JSONResponse
from jose import JWTError
from starlette.middleware.base import BaseHTTPMiddleware
import  tools.appToken as appToken

from tools.appStatus import httpCodeStatus


class TokenValidationMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):

        authorization: str = request.headers.get("Authorization")
        if not authorization or not authorization.startswith("Bearer "):
            return httpCodeStatus(code=401, message="token 无效")
        token: str = authorization.split(" ")[1]
        if not self.isTokenValid(token):
            return httpCodeStatus(code=401, message="token 无效")
        response = await call_next(request)
        return response

    def isTokenValid(self, token: str) -> Optional[int]:
        try:
            payload = appToken.paseToken(token)
            # 在此可以根据需求检查 payload 中的具体信息
            return payload if payload else None

        except JWTError:
            return False


def appTokenValidationMiddleware(app):
    app.add_middleware(TokenValidationMiddleware)
    return app


#添加中间件

#跨域相关配置
def appCORSMiddleware(app):
    # 将 router 添加到 app 中
    origins = [
        "*"

    ]  # 也可以设置为"*"，即为所有。
    # CORS
    app.add_middleware(
        CORSMiddleware,
        allow_origins=origins,  # 允许访问的源
        allow_credentials=True,  # 支持 cookie
        allow_methods=["*"],  # 允许使用的请求方法
        allow_headers=["*"]  # 允许携带的 Headers
    )
    return app


def appGZipMiddleware(app, min_size=1000, compresslevel=5):
    app.add_middleware(GZipMiddleware, minimum_size=min_size, compresslevel=compresslevel)
    return app


def appHttpsRedirectMiddleware(app):
    app.add_middleware(HTTPSRedirectMiddleware)
    return app
