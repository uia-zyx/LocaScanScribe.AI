from functools import lru_cache

from app.db.session import get_session_factory, init_database
from app.ingestion.repository import DocumentRepository
from app.ingestion.service import IngestionService
from app.jobs.queue import DocumentJobQueue
from app.parsers.registry import ParserRegistry
from app.search.embeddings import EmbeddingClient
from app.search.service import SearchService
from app.search.vector_store import VectorStore
from app.storage.object_store import ObjectStore


@lru_cache
def get_object_store() -> ObjectStore:
    return ObjectStore()


@lru_cache
def get_document_repository() -> DocumentRepository:
    init_database()
    return DocumentRepository(
        session_factory=get_session_factory(),
        object_store=get_object_store(),
    )


@lru_cache
def get_embedding_client() -> EmbeddingClient:
    return EmbeddingClient()


@lru_cache
def get_vector_store() -> VectorStore:
    return VectorStore(embedding_client=get_embedding_client())


@lru_cache
def get_document_job_queue() -> DocumentJobQueue:
    return DocumentJobQueue()


def get_ingestion_service() -> IngestionService:
    return IngestionService(
        repository=get_document_repository(),
        parser_registry=ParserRegistry(),
        vector_store=get_vector_store(),
    )


def get_search_service() -> SearchService:
    return SearchService(
        repository=get_document_repository(),
        vector_store=get_vector_store(),
    )

