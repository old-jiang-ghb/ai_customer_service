import logging
import os
from logging.handlers import TimedRotatingFileHandler
from core import settings
from logging_loki import LokiHandler
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
loki_handler = LokiHandler(
    url="http://localhost:3100/loki/api/v1/push",  # Loki 默认地址
    tags={
        "service": "ai_customer_service",  # 你的服务名
        "env": "dev",                     # 环境
        "app": "fastapi"                  # 应用类型
    },
    version="1"
)
loki_handler.setLevel(logging.INFO)

# 全局 logger
log = logging.getLogger("ai_customer_service")
log.setLevel(logging.INFO)
log.addHandler(handler)
log.addHandler(console_handler)
log.addHandler(loki_handler)
log.propagate = False