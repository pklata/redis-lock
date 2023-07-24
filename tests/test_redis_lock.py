import multiprocessing
import threading
import queue

import pytest

from src.redis_lock import ValueNotReadyError, RedisLockClient


def test_value_put_and_is_on_redis(redis_lock_client, redis_client):
    redis_lock_client.put("key1", "value1")

    assert redis_client.lpop("key1") == "value1"

def test_value_put_and_pop(redis_lock_client, redis_client):
    redis_lock_client.put("key1", "value1")
    assert redis_lock_client.pop("key1") == "value1"

def test_pop_timeout(redis_lock_client, redis_client):
    with pytest.raises(ValueNotReadyError):
        assert redis_lock_client.pop("key1", timeout=1)

def test_consumer_thread_awaits_for_result(redis_lock_client_config):
    def consumer_thread(result_list):
        client = RedisLockClient(**redis_lock_client_config)
        result_list.append(client.pop("key1"))
    def producer_thread():
        client = RedisLockClient(**redis_lock_client_config)
        client.put("key1", "value1")

    result_list = []
    consumer_thread_ = threading.Thread(target=consumer_thread, args=(result_list,))
    producer_thread_ = threading.Thread(target=producer_thread)
    consumer_thread_.start()
    assert not result_list
    producer_thread_.start()
    consumer_thread_.join()
    producer_thread_.join()
    assert result_list == ["value1"]

def test_consumer_process_awaits_for_result(redis_lock_client_config):
    def consumer_process(result_queue):
        client = RedisLockClient(**redis_lock_client_config)
        result_queue.put(client.pop("key1"))
    def producer_process():
        client = RedisLockClient(**redis_lock_client_config)
        client.put("key1", "value1")

    result_queue = multiprocessing.Queue()
    consumer_process_ = multiprocessing.Process(target=consumer_process, args=(result_queue,))
    producer_process_ = multiprocessing.Process(target=producer_process)
    consumer_process_.start()
    with pytest.raises(queue.Empty):
        result_queue.get_nowait()
    producer_process_.start()
    consumer_process_.join()
    producer_process_.join()
    assert result_queue.get_nowait() == "value1"