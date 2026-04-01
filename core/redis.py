import redis
from redis.connection import ConnectionPool
from typing import Optional
from core import settings

REDIS_HOST = settings.REDIS_HOST
REDIS_PORT = settings.REDIS_PORT
REDIS_PASSWORD = settings.REDIS_PASSWORD
REDIS_DB = settings.REDIS_DB
MAX_CONNECTIONS = settings.MAX_CONNECTIONS
# 从节点
SLAVE_HOSTS = settings.SLAVE_HOSTS

# ====================
# 主节点连接池（写）
# ====================
master_pool = ConnectionPool(
    host=REDIS_HOST,
    port=REDIS_PORT,
    password=REDIS_PASSWORD,
    db=REDIS_DB,
    decode_responses=True,
    max_connections=MAX_CONNECTIONS,
    socket_timeout=3,
)
redis_master = redis.Redis(connection_pool=master_pool)

# ====================
# 从节点连接池（读）
# ====================
slave_pools = []
for slave in SLAVE_HOSTS:
    pool = ConnectionPool(
        host=slave["host"],
        port=slave["port"],
        password=REDIS_PASSWORD,
        db=REDIS_DB,
        decode_responses=True,
        max_connections=MAX_CONNECTIONS // len(SLAVE_HOSTS),
        socket_timeout=3,
    )
    slave_pools.append(redis.Redis(connection_pool=pool))

# ====================
# 轮询读从节点（负载均衡）
# ====================
current_slave_index = 0

def get_slave_client():
    global current_slave_index
    client = slave_pools[current_slave_index]
    current_slave_index = (current_slave_index + 1) % len(slave_pools)
    return client

# ====================
# 最终暴露：读写客户端
# ====================
class RedisClient:
    # 写 -> 主节点
    @staticmethod
    def write():
        return redis_master

    # 读 -> 从节点（轮询）
    @staticmethod
    def read():
        return get_slave_client()

redis = RedisClient()