from typing import Optional

import redis

class ValueNotReadyError(Exception):
    pass

class RedisLockClient:

    def __init__(self, **redis_kwargs):
        self.redis_client = redis.Redis(**redis_kwargs)

    def put(self, key: str, data: Optional[str] = None):
        self.redis_client.lpush(key, data)

    def pop(self, key: str, timeout = 30):
        try:
            return self.redis_client.blpop(key, timeout)[1]
        except TypeError:
            raise ValueNotReadyError