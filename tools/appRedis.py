import redis
import schedule
import json
import time
import logging
from typing import Optional
from fastapi import status
from .appStatus import httpCodeStatus as httpStatus
from tools.appVariable import EXPIRE_TIME
from tools.apploggin import create_logger

# 定义一些状态码
statusCode = {
    12000: 12000,  # 用户未找到，删除失败
    12001: 12001,  # 用户已存在
    60000: 60000,  # Redis 未启动
    130001: 13001,  # 临时数据不存在
90002:90002, #解析失败
}

create_logger()

def get_redis_clientKey(key: str = '',message:str="当前用户不存在，请先注册")->str:
    if not key or key is None or key == '' or len(key) == 0:
        return httpStatus(message=message, data={}, code=statusCode[12001])
    return key

class RedisDB:
    def __init__(self, host='localhost', port=6379, db=0, decode_responses=True,password=None,

                 ):
        # 初始化 Redis 连接
        self.redis_client = redis.Redis(
            host=host,
            port=port,
            db=db,
            decode_responses=decode_responses,
            password=password
    )
        self.firstDb=db


    def is_running(self):
        """检查 Redis 是否运行中"""
        try:
            return self.redis_client.ping()
        except (redis.exceptions.ConnectionError, redis.exceptions.TimeoutError) as e:
            error_message = "Redis 未运行"
            print(error_message)
            logging.error(f"{error_message}: {str(e)}")
            return False

    #关闭
    def close(self)->None:
        """在对象删除时关闭 Redis 连接"""
        try:
            if self.redis_client:
                self.redis_client.close()
                self.redis_client = None
                logging.info("已关闭 Redis 连接")
        except Exception as e:
            logging.error(f"关闭 Redis 连接时出错: {str(e)}")
    def __repr__(self)->Optional[str]:
        return f'<RedisDB {self.redis_client}>'
    def __str__(self)->Optional[str]:
        return f'<RedisDB {self.redis_client}>'
    def __del__(self)->Optional[None]:
        """在对象删除时关闭 Redis 连接"""
        self.close()
    def __bool__(self)->bool:
        pass
    def __len__(self)->int:
        pass
    def __getitem__(self, item):
        pass

    #解析redis返回值
    def parse_redis_result(self,key:str="")->dict:
        dresult: dict = {}
        result =get_redis_clientKey(key)
        if not result:
            return httpStatus(message="无法解析redis返回值",code=statusCode[90002])
        result=self.redis_client.get(key)
        if not result:
            return httpStatus(message="redis中无此数据",code=statusCode[90002])
        try:
            json_value = json.loads(key)
            print(json_value,type(json_value))

            if not isinstance(json_value,dict):
                return httpStatus(message="解析失败",code=statusCode[90002])
            for k,v in json_value.items():
                dresult[k]=v
            return dresult
        except json.JSONDecodeError as e:
            # 如果不是 JSON 格式，判断是否为简单的字符串或数字
            if "=" in key and ";" in key:
                # 假定是类似 'a=1;b=2' 的格式，进行分割
                pairs = key.split(';')
                for pair in pairs:
                    if '=' in pair:
                        k, v = pair.split('=')
                        dresult[k.strip()] = v.strip()
                return dresult
            else:
                # 如果既不是 JSON，也不是键值对格式，直接输出原始值
                return httpStatus(message="解析失败",code=statusCode[90002])


    def get(self,key:str='',dictKey:str='pc')->dict:
        result =get_redis_clientKey(key)
        if result:
            """从 Redis 获取用户信息"""
            full_key = f"{dictKey}{key}"
            user_data = self.redis_client.hgetall(full_key)
            if not user_data:
                return httpStatus(message="用户未找到",)
            # 延长过期时间，保持数据活跃
            self.redis_client.expire(full_key, EXPIRE_TIME)
            return user_data

    def set(self,key:str='',dictKey:str='pc',value:dict={})->dict:
        result = get_redis_clientKey(key)
        if result:
            """将用户信息存储到 Redis"""
            full_key = f"{dictKey}{key}"
            # 如果用户不存在则存储新信息，否则更新现有信息
            self.redis_client.hset(full_key, mapping=value)
            self.redis_client.expire(full_key, EXPIRE_TIME)  # 设置过期时间
            return httpStatus(message="存储成功",code=200)
    def delete(self,key:str='',dictKey:str='pc')->dict:
        result = get_redis_clientKey(key)
        if result:
            """删除用户信息"""
            full_key = f"{dictKey}{key}"
            if self.get(key=key,dictKey=dictKey) is not None:  # 如果用户存在
                self.redis_client.delete(full_key)
                return httpStatus(message="删除成功",code=200)
            return httpStatus(message="用户未找到, 删除失败")
    def put(self,key:str='user',dictKey:str='user',):
        if self.get(key,dictKey) is not None:
            return self.set(key,dictKey)
        return httpStatus(message="用户未找到, 更新失败")
    def patch(self,key:str='user',dictKey:str='user',):
        pass
    def head(self,key:str='user',dictKey:str='user',):
        pass
    def options(self,key:str='user',dictKey:str='user',):
        pass
    def trace(self,key:str='user',dictKey:str='user',):
        pass
    def check_redis(self):
        """检查 Redis 服务状态"""
        if not self.is_running():
            # 可以记录日志或发送通知以提醒管理员 Redis 未运行
            print("Redis 未运行，请检查服务状态。")
            logging.error("Redis 未运行，请检查服务状态。")
            return httpStatus(message="Redis 未运行，请检查服务状态",)
        return httpStatus(message="Redis 运行正常", code=200)

    # 定时检查 Redis 状态
    #特定情况使用，一般不使用
    def open_redis_schedule(self,i:int=99)->None:
        # 使用 schedule 库定时检查 Redis 状态
        schedule.every(600).seconds.do(self.check_redis)  # 每隔 600 秒检查一次 Redis 是否运行
        # 主循环，定时运行计划任务
        if i<=10:
            while True:
                schedule.run_pending()
                time.sleep(1)
        else:
            schedule.run_all()
    def stop(self):
        pass
    def start(self):
        pass

