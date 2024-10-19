import redis
import json

# 连接 Redis 数据库
client = redis.StrictRedis(
    host='localhost',  # Redis 服务器的主机名
    port=6379,  # Redis 端口
    db=0,  # 使用的数据库编号
    decode_responses=True  # 确保以字符串的形式读取数据
)

# 获取键 'value1' 的值
key = 'value1'
value = client.get(key)

if value:
    try:
        # 尝试将字符串转换为 JSON 格式
        json_value = json.loads(value)

        # 如果成功，将 JSON 数据打印出来
        print("JSON 格式数据：",json_value)
        if not isinstance(json_value, dict):
            print(f"不是 JSON 格式数据：{json_value}")
        else:
            for k, v in json_value.items():
                print(f"{k}: {v}")
    except json.JSONDecodeError:
        # 如果不是 JSON 格式，判断是否为简单的字符串或数字
        if "=" in value and ";" in value:
            # 假定是类似 'a=1;b=2' 的格式，进行分割
            pairs = value.split(';')
            for pair in pairs:
                if '=' in pair:
                    k, v = pair.split('=')
                    print(f"{k.strip()}: {v.strip()}")
        else:
            # 如果既不是 JSON，也不是键值对格式，直接输出原始值
            print(f"原始值：{value}")
else:
    print(f"The key '{key}' does not exist in Redis.")
