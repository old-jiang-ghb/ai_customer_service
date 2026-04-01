import logging
import os
from logging.handlers import TimedRotatingFileHandler
from core import settings

# 日志存放目录
LOG_DIR = settings.LOGGING_SAVE_DIR
os.makedirs(LOG_DIR, exist_ok=True)

# 日志格式（企业标准）
formatter = logging.Formatter(
    "%(asctime)s | %(levelname)s | %(filename)s:%(lineno)d | %(message)s"
)

# 按天切割
handler = TimedRotatingFileHandler(
    f"{LOG_DIR}/info.log",
    when="midnight",  # 每天凌晨切割
    interval=1,
    backupCount=30,  # 保留30天
    encoding="utf-8"
)
handler.setFormatter(formatter)
handler.setLevel(logging.INFO)

# 控制台输出
console_handler = logging.StreamHandler()
console_handler.setFormatter(formatter)
console_handler.setLevel(logging.INFO)

# 全局 logger
log = logging.getLogger("app")
log.setLevel(logging.INFO)
log.addHandler(handler)
log.addHandler(console_handler)
log.propagate = False