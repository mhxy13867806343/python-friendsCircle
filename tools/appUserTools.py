from fastapi import FastAPI, Request
from user_agents import parse
from typing import Optional

def getAppUserInfo(request: Request)->Optional[dict]:
    user_agent_str = request.headers.get('User-Agent') # 获取User-Agent
    user_agent = parse(user_agent_str) # 解析User-Agent

    # 获取浏览器类型
    browser_type = user_agent.browser.family # 获取浏览器类型

    # 获取操作系统类型
    os_type = user_agent.os.family # 获取操作系统类型

    # 根据User-Agent判断登录方式是PC还是移动端
    login_type = 1 if user_agent.is_mobile else 0  # 1 表示移动端，0 表示PC端
    client_ip = request.client.host  # 获取客户端IP地址
    return {
        "browser_type": browser_type,
        "os_type": os_type,
        "login_type": login_type,
        "client_ip": client_ip
    }