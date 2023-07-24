import pytest
import redis

from src.redis_lock import RedisLockClient

@pytest.fixture(scope="session")
def redis_lock_client_config():
    return {
        "host": "localhost",
        "port": 6379,
        "decode_responses": True
    }

@pytest.fixture
def redis_lock_client(redis_lock_client_config):
    return RedisLockClient(**redis_lock_client_config)

@pytest.fixture(scope="session")
def redis_client(redis_lock_client_config):
    return redis.Redis(**redis_lock_client_config)