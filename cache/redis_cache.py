from core.redis import redis

# redis正常读取
class RedisCache:
    PREFIX = "redis:cache:"
    EXPIRE = 1800  # 缓存半小时

    @classmethod
    def get(cls, unique: str):
        key = cls.PREFIX + unique
        return redis.read().get(key)

    @classmethod
    def set(cls, unique: str, value: str, expire: int = EXPIRE):
        key = cls.PREFIX + unique
        redis.write().setex(key, expire, value)
