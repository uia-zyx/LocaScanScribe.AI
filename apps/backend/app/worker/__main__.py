import asyncio
import logging

from app.api.deps import get_document_job_queue, get_ingestion_service
from app.db.session import init_database

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def main() -> None:
    init_database()
    queue = get_document_job_queue()
    service = get_ingestion_service()
    logger.info("Document worker started")

    while True:
        document_id = queue.dequeue_processing()
        if document_id is None:
            continue

        logger.info("Processing document %s", document_id)
        asyncio.run(service.process_document(document_id))


if __name__ == "__main__":
    main()

