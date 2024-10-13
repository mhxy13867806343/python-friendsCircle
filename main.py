from fastapi import FastAPI,APIRouter
from starlette.middleware.base import BaseHTTPMiddleware
from extend.db import Base, ENGIN # 导入数据库相关模块
from app.user.views import userRouter

from tools.appAddMiddleware import appAddMiddleware
import uvicorn

from tools.appMount import staticMount
from tools.appRate import appLimitRate

app = FastAPI()

v1_router = APIRouter(prefix="/v1")
# 将各个模块的路由添加到带前缀的路由器
v1_router.include_router(userRouter, prefix="/pc", tags=["用户管理"])


app.include_router(v1_router)


appAddMiddleware(app)

staticMount(app)
appLimitRate(app)
Base.metadata.create_all(bind=ENGIN)

if __name__ == "__main__":
    uvicorn.run("main:app", host="localhost", port=8000, reload=True)