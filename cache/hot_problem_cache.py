import json
import hashlib
from core.redis import redis

class HotQACache:
    PREFIX = "qa:hot"
    EXPIRE = 3600  # 缓存1小时

    @classmethod
    def _get_key(cls, question: str):
        # 对问题做简单清洗+哈希，避免key太长
        q = question.strip().lower()
        hash_obj = hashlib.md5(q.encode("utf-8"))
        return f"{cls.PREFIX}:{hash_obj.hexdigest()}"

    @classmethod
    def get(cls, question: str):
        key = cls._get_key(question)
        data = redis.read().get(key)  # 读：走从节点
        return json.loads(data) if data else None

    @classmethod
    def set(cls, question: str, answer: str):
        key = cls._get_key(question)
        # 写：走主节点
        redis.write().setex(key, cls.EXPIRE, json.dumps({
            "answer": answer,
            "cached": True
        }, ensure_ascii=False))