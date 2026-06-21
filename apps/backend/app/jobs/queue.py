import logging
from uuid import UUID

import redis
from redis.exceptions import ConnectionError as RedisConnectionError
from redis.exceptions import TimeoutError as RedisTimeoutError

from app.core.settings import get_settings

logger = logging.getLogger(__name__)


class DocumentJobQueue:
    queue_name = "document-processing"

    def __init__(self) -> None:
        self.settings = get_settings()
        self.client = redis.Redis.from_url(
            self.settings.redis_url,
            decode_responses=True,
            health_check_interval=30,
            retry_on_timeout=True,
            socket_connect_timeout=5,
            socket_keepalive=True,
        )

    def enqueue_processing(self, document_id: UUID) -> None:
        self.client.rpush(self.queue_name, str(document_id))

    def dequeue_processing(self, timeout: int = 5) -> UUID | None:
        try:
            item = self.client.blpop(self.queue_name, timeout=timeout)
        except (RedisTimeoutError, RedisConnectionError):
            logger.warning("Redis queue read timed out or disconnected; retrying")
            return None

        if item is None:
            return None

        _, document_id = item
        return UUID(document_id)
