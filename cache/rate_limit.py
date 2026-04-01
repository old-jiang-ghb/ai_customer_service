from core.redis import redis

# 接口限流redis实现
class RateLimiter:
    PREFIX = "rate:limit"
    WINDOW_SECONDS = 60  # 1分钟
    MAX_REQUESTS = 10     #默认每分钟十次

    @classmethod
    def is_allowed(cls, unique_id: str, max_requests: int = MAX_REQUESTS) -> bool:
        """
        unique_id: 用户ID / session_id / ip
        返回 True=允许, False=限流
        """
        key = f"{cls.PREFIX}:{unique_id}"

        # 计数+1（原子操作）
        count = redis.write().incr(key)

        # 第一次设置过期时间
        if count == 1:
            redis.write().expire(key, cls.WINDOW_SECONDS)

        return count <= max_requests