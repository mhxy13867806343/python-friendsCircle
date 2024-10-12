import re
import hashlib
import random
import string
from datetime import datetime
import uuid

# 生成用户 ID
def generate_uid(name_str:str='',utype:int=1,login_type:str="pc",
                 a:int=5,
                 b:int=20,
                 )->str:
    shex=uuid.uuid4().hex
    # 从哈希值中随机选择 5 到 20 个字符，包含字母、数字和特殊字符
    timestamp = int(datetime.now().timestamp()*1000)
    chars =string.digits + string.ascii_letters + string.punctuation
    uid_length = random.randint(a, b)
    uid = ''.join(random.choices( chars, k=uid_length))
    shex="".join(random.choices( shex, k=uid_length))
    result:str=f"{name_str}{timestamp}{uid}{utype}{login_type}{shex}"
    return result



# 验证用户名的正则表达式
def validate_username(value:str="")->bool:
    if not value:
        return False
    # 正则表达式：以字母开头，后面可以是字母、数字或特殊字符 _-.@
    pattern = r'^[A-Za-z][A-Za-z0-9_.@-]*$'
    return bool(re.match(pattern, value))

# 验证密码的正则表达式
def validate_password(value:str="")->bool:
    if not value:
        return False
    # 正则表达式：以字母开头，后面可以是字母、数字或特殊字符 _-.@，长度为 6-30 位
    pattern = r'^[A-Za-z][A-Za-z0-9_.@-]{5,29}$'
    return bool(re.match(pattern, value))