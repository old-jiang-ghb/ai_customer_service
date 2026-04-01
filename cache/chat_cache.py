import json
from core.redis import redis

class ChatHistoryCache:
    """
    聊天历史缓存
    - 只保留最近10条
    - 1小时自动过期
    - 读写分离
    """
    KEY_PREFIX = "chat:history"
    EXPIRE = 3600  # 1小时
    MAX_MESSAGES = 10  # 只保留最近10条消息

    @classmethod
    def get_key(cls, session_id):
        return f"{cls.KEY_PREFIX}:{session_id}"

    @classmethod
    def get(cls, session_id):
        """读：从从节点读取"""
        key = cls.get_key(session_id)
        data = redis.read().get(key)
        return json.loads(data) if data else []

    @classmethod
    def set(cls, session_id, messages):
        """写：写入主节点"""
        key = cls.get_key(session_id)
        messages = messages[-cls.MAX_MESSAGES:]  # 截断最近10条
        redis.write().setex(key, cls.EXPIRE, json.dumps(messages, ensure_ascii=False))

    @classmethod
    def add_message(cls, session_id, history_type, detail):
        messages = cls.get(session_id)
        messages.append({"history_type": history_type, "detail": detail})
        cls.set(session_id, messages)