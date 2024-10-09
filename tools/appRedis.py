import redis
import schedule
import time
import logging

from appStatus import httpCodeStatus as httpStatus
from tools.appVariable import EXPIRE_TIME
from tools.apploggin import create_logger

# 定义一些状态码
statusCode = {
    12000: 12000,  # 用户未找到，删除失败
    12001: 12001,  # 用户已存在
    60000: 60000,  # Redis 未启动
    130001: 13001  # 临时数据不存在
}

# Redis 键的前缀配置
rd = {
    "user_prefix": "user:"
}

create_logger()


def get_redis_clientKey(key: str = '',message:str="当前用户不存在，请先注册")->str:
    if not key or key is None or key == '' or len(key) == 0:
        return httpStatus(message=message, data={}, code=statusCode[12001])
    return key

class RedisDB:
    def __init__(self, host='localhost', port=6379, db=0, decode_responses=True):
        # 初始化 Redis 连接
        self.redis_client = redis.Redis(host=host, port=port, db=db, decode_responses=decode_responses)

    def is_running(self):
        """检查 Redis 是否运行中"""
        try:
            return self.redis_client.ping()
        except (redis.exceptions.ConnectionError, redis.exceptions.TimeoutError) as e:
            error_message = "Redis 未运行"
            print(error_message)
            logging.error(f"{error_message}: {str(e)}")
            return False

    def __repr__(self):
        return f'<RedisDB {self.redis_client}>'

    def get(self, key: str = ''):
        if not key or key is None or key =='' or len(key) == 0:
            return httpStatus(message="无法获取用户信息!!!!", data={}, code=statusCode[12001])
        """从 Redis 获取用户信息"""
        full_key = f"{rd.get('user_prefix')}{key}"
        user_data = self.redis_client.hgetall(full_key)
        if not user_data:
            return None
        return user_data

    def set(self, key: str = '', value: dict = {}):
        result=get_redis_clientKey(key)
        if result:
            """将用户信息存储到 Redis"""
            full_key = f"{rd.get('user_prefix')}{key}"
            # 如果用户不存在则存储新信息，否则更新现有信息
            self.redis_client.hset(full_key, mapping=value)
            self.redis_client.expire(full_key, EXPIRE_TIME)  # 设置过期时间
            return httpStatus(message="存储成功", data={})

    def delete(self, key: str = ''):
        result = get_redis_clientKey(key)
        if result:
            """删除用户信息"""
            full_key = f"{rd.get('user_prefix')}{key}"
            if self.get(key) is not None:  # 如果用户存在
                self.redis_client.delete(full_key)
                return httpStatus(message="删除成功", data={})
            return httpStatus(message="用户未找到, 删除失败", data={}, code=statusCode[12000])

def check_redis():
    """检查 Redis 服务状态"""
    redis_db = RedisDB()
    if not redis_db.is_running():
        # 可以记录日志或发送通知以提醒管理员 Redis 未运行
        print("Redis 未运行，请检查服务状态。")
        logging.error("Redis 未运行，请检查服务状态。")
        return httpStatus(message="Redis 未运行，请检查服务状态", data={}, code=statusCode[60000])

# 使用 schedule 库定时检查 Redis 状态
schedule.every(600).seconds.do(check_redis)  # 每隔 600 秒检查一次 Redis 是否运行

# 主循环，定时运行计划任务
while True:
    schedule.run_pending()
    time.sleep(1)