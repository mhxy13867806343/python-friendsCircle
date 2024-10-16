import logging
import os
from datetime import datetime
from logging.handlers import RotatingFileHandler

# 配置日志记录，根据当前日期动态创建日志文件
def create_logger(log_folder: str = "circlelog",
                  other_log: str = "redis_errors_",
                  file_max_size: int = 2 * 1024 * 1024 * 1024,
                  format: str = '%(asctime)s - %(levelname)s - %(message)s') -> logging.Logger:
    # 创建日志目录
    if not os.path.exists(log_folder):
        os.makedirs(log_folder)

    current_date = datetime.now().strftime('%Y-%m-%d')
    log_filename = f'{log_folder}/{other_log}{current_date}.log'

    # 设置日志记录器
    logger = logging.getLogger(other_log)
    logger.setLevel(logging.ERROR)

    # 防止重复添加处理器
    if not logger.hasHandlers():
        # 使用 RotatingFileHandler 管理日志文件大小
        handler = RotatingFileHandler(log_filename, maxBytes=file_max_size, backupCount=1)
        handler.setLevel(logging.ERROR)

        # 创建日志格式化程序，并将最新的时间放在最前面
        formatter = logging.Formatter(format)
        handler.setFormatter(formatter)

        # 添加处理器到记录器
        logger.addHandler(handler)

    return logger