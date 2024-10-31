from fastapi import FastAPI,APIRouter
from starlette.middleware.base import BaseHTTPMiddleware
from extend.db import Base, ENGIN # 导入数据库相关模块
from app.home.views import homeRouter
from app.user.views import userRouter
from app.dicts.views import dictRouter
from app.pcds.views import pcdsRouter
import uvicorn

from tools.appMount import staticMount
from tools.appRate import appLimitRate
from tools.appStarlette import appCORSMiddleware, appTokenValidationMiddleware, appGZipMiddleware, \
    appHttpsRedirectMiddleware

app = FastAPI()

v1_router = APIRouter(prefix="/v1")
# 将各个模块的路由添加到带前缀的路由器
v1_router.include_router(homeRouter, prefix="/home", tags=["首页管理"])
v1_router.include_router(userRouter, prefix="", tags=["用户管理"])
v1_router.include_router(dictRouter, prefix="/pc", tags=["字典管理"])
v1_router.include_router(pcdsRouter, prefix="", tags=["地区管理"])


app.include_router(v1_router)


#初始化函数操作
def  appMain(apps: FastAPI)->FastAPI:
    #appTokenValidationMiddleware(apps)
    appGZipMiddleware(apps)
    #appHttpsRedirectMiddleware(apps)
    appCORSMiddleware(apps)
    staticMount(apps)
    appLimitRate(apps)
    return apps


appMain(app)



Base.metadata.create_all(bind=ENGIN)


if __name__ == "__main__":
    uvicorn.run("main:app", host="localhost", port=8000, reload=True)