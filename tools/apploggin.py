import logging
import os
from datetime import datetime
# 配置日志记录，根据当前日期动态创建日志文件
def create_logger(log_folder:str="circlelog",other_log:str="redis_errors_",
         file_max_size:int=2 * 1024 * 1024 * 1024,
         format:str='%(asctime)s - %(levelname)s - %(message)s'
         )->logging:
    if not os.path.exists(log_folder):
        os.makedirs(log_folder)
    if not os.path.exists(other_log):
        os.makedirs(other_log)
    current_date = datetime.now().strftime('%Y-%m-%d')
    log_filename = f'{log_folder}/{other_log}{current_date}.log'

    # 检查日志文件大小是否超过 2GB，如果超过则删除
    if os.path.exists(log_filename) and os.path.getsize(log_filename) >file_max_size:
        os.remove(log_filename)

    logging.basicConfig(filename=log_filename, level=logging.ERROR,
                        format=format)
