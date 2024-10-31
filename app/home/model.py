from datetime import datetime
from pydantic import BaseModel
from typing import Optional, List
from pydantic import Field


class FunctionalVersionModel(BaseModel):
    title: Optional[str]="标题"
    id: Optional[int]=None
    content: Optional[str]="测试内容"
    version:  Optional[str]='0.0.1测试版本号'