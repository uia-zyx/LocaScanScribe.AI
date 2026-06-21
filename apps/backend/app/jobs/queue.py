from uuid import UUID

import redis

from app.core.settings import get_settings


class DocumentJobQueue:
    queue_name = "document-processing"

    def __init__(self) -> None:
        self.settings = get_settings()
        self.client = redis.Redis.from_url(self.settings.redis_url, decode_responses=True)

    def enqueue_processing(self, document_id: UUID) -> None:
        self.client.rpush(self.queue_name, str(document_id))

    def dequeue_processing(self, timeout: int = 5) -> UUID | None:
        item = self.client.blpop(self.queue_name, timeout=timeout)
        if item is None:
            return None

        _, document_id = item
        return UUID(document_id)
