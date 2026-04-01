import time
from functools import wraps
from utils.logger_utils import log
# ====================== 重试装饰器（自动重试3次） ======================
def retry(max_retries=3, delay=1):
    def decorator(func):
        log.info(f"装饰器执行重试,方法：{func.__name__}")
        @wraps(func)
        def wrapper(*args, **kwargs):
            for i in range(max_retries):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    if i < max_retries - 1:
                        log.warn(f"{func.__name__}失败，{delay}秒后重试 {i+1}/{max_retries}")
                        time.sleep(delay)
                    else:
                        log.error(f"重试全部失败:{func.__name__},请及时查看原因")
                        raise e
        return wrapper
    return decorator