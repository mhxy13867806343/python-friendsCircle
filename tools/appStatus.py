from fastapi import  status

from typing import Dict, Any, Optional
def httpCodeStatus(
        code:int=status.HTTP_400_BAD_REQUEST,
                   message:str="获取数据失败",data:Optional[Dict[str, Any]]=None
                   )->Dict[str, Any]:
    return {
        "data":{
            "code":code,
            "message":f"{message}",
            "result":Optional[data]
        }
    }
