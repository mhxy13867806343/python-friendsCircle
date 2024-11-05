from datetime import datetime
from pydantic import BaseModel
from typing import Optional, List
from pydantic import Field

class FcunctionalModel(BaseModel):
    id: Optional[int] = None
    content: Optional[str] = "测试内容"
    title: Optional[str] = "标题"

class CarouselModel(FcunctionalModel):
    img_url: Optional[str] = ""
    link_url: Optional[str] = ""
    type: Optional[int] = 0
    text: Optional[str] = ""

class FunctionalVersionModel(FcunctionalModel):

    version:  Optional[str]='0.0.1测试版本号'