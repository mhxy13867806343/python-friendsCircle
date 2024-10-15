from datetime import datetime
from pydantic import BaseModel
from typing import Optional, List
from pydantic import Field

# 通用字段模型
class SysBaseDictModel(BaseModel):
    id: Optional[int] = None
    key: Optional[str] = None
    value: Optional[str] = None
    desc: Optional[str] = None
    status: Optional[int] = 0
    createTime: Optional[int] = Field(default_factory=lambda: int(datetime.now().timestamp()))
    updateTime: Optional[int] = Field(default_factory=lambda: int(datetime.now().timestamp()))



# 字典子项模型
class DictInputBaseChildModel(SysBaseDictModel):
    dictId: Optional[int] = None
    operatorChild: Optional[str] = 'admin'
# 字典父模型
class DictInputBaseModel(SysBaseDictModel):
    children: Optional[List[DictInputBaseChildModel]] = []
    operatorParent: Optional[str] = 'admin'