from redis.exceptions import TimeoutError as RedisTimeoutError

from app.jobs.queue import DocumentJobQueue


class TimeoutRedisClient:
    def blpop(self, queue_name: str, timeout: int):
        raise RedisTimeoutError("Timeout reading from socket")


def test_dequeue_processing_treats_redis_timeout_as_empty_queue() -> None:
    queue = DocumentJobQueue.__new__(DocumentJobQueue)
    queue.client = TimeoutRedisClient()

    assert queue.dequeue_processing() is None
