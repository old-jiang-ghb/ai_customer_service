import logging
import os
import json
from logging.handlers import TimedRotatingFileHandler
from core import settings
from logging_loki import LokiHandler
from utils.context_utils import trace_id_ctx

# ==========================
# 日志目录
# ==========================
LOG_DIR = settings.LOGGING_SAVE_DIR
os.makedirs(LOG_DIR, exist_ok=True)

# ==========================
# 1. 全局 Logger
# ==========================
log = logging.getLogger("ai_customer_service")
log.setLevel(logging.INFO)
log.handlers.clear()  # 清空默认 handler，避免重复
log.propagate = False

# ==========================
# 2. 通用日志格式（文本格式，用于文件）
# ==========================
text_formatter = logging.Formatter(
    "%(asctime)s | %(levelname)s | %(filename)s:%(lineno)d | %(message)s"
)

# ==========================
# 3. 按天切割文件日志（修复多进程安全）
# ==========================
file_handler = TimedRotatingFileHandler(
    f"{LOG_DIR}/info.log",
    when="midnight",
    interval=1,
    backupCount=30,
    encoding="utf-8",
    delay=True  # 修复多进程下文件切割问题
)
file_handler.setFormatter(text_formatter)
log.addHandler(file_handler)

# ==========================
# 4. 控制台输出
# ==========================
console_handler = logging.StreamHandler()
console_handler.setFormatter(text_formatter)
log.addHandler(console_handler)

# ==========================
# 5. Loki 处理器（JSON格式 + 标签 + 超时）
# ==========================
class LokiJsonFormatter(logging.Formatter):
    def format(self, record):
        # 从上下文拿 trace_id → 任何地方都能拿！
        trace_id = trace_id_ctx.get()
        log_record = {
            "time": self.formatTime(record),
            "level": record.levelname,
            "filename": record.filename,
            "line": record.lineno,
            "message": record.getMessage(),
            "service": "ai_customer_service",
            "env": "dev",
            "trace_id": trace_id
        }
        return json.dumps(log_record, ensure_ascii=False)

try:
    loki_handler = LokiHandler(
        url=settings.LOKI_URL,
        tags={
            "service": "ai_customer_service",
            "env": "dev",
            "app": "fastapi"
        },
        version="1"
    )
    # 重点：Loki 使用 JSON 格式！！！
    loki_handler.setFormatter(LokiJsonFormatter())
    log.addHandler(loki_handler)
except Exception as e:
    # 修复：这里不能用 log.warning，会报错
    print(f"[Logging] Loki 连接失败: {str(e)}")