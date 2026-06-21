from typing import Annotated

from fastapi import APIRouter, Depends, Header, Request

from app.api.deps import get_document_repository
from app.api.openwebui_utils import (
    document_frontend_url,
    document_id_from_url,
    request_base_url,
    validate_openwebui_key,
)
from app.api.schemas import (
    OpenWebUILoaderRequest,
    OpenWebUILoaderResult,
    OpenWebUISearchRequest,
    OpenWebUISearchResult,
)
from app.core.settings import Settings, get_settings
from app.ingestion.repository import DocumentRepository
from app.search.chunking import chunk_markdown

router = APIRouter(prefix="/openwebui", tags=["openwebui"])


@router.post("/web-search", response_model=list[OpenWebUISearchResult])
async def openwebui_web_search(
    request: OpenWebUISearchRequest,
    http_request: Request,
    settings: Annotated[Settings, Depends(get_settings)],
    repository: Annotated[DocumentRepository, Depends(get_document_repository)],
    authorization: Annotated[str | None, Header()] = None,
    x_api_key: Annotated[str | None, Header()] = None,
) -> list[OpenWebUISearchResult]:
    validate_openwebui_key(settings, authorization, x_api_key)

    base_url = request_base_url(http_request)
    return _keyword_search_documents(repository, request.query, request.count, base_url)


@router.post("/web-loader", response_model=list[OpenWebUILoaderResult])
async def openwebui_web_loader(
    request: OpenWebUILoaderRequest,
    http_request: Request,
    settings: Annotated[Settings, Depends(get_settings)],
    repository: Annotated[DocumentRepository, Depends(get_document_repository)],
    authorization: Annotated[str | None, Header()] = None,
    x_api_key: Annotated[str | None, Header()] = None,
) -> list[OpenWebUILoaderResult]:
    validate_openwebui_key(settings, authorization, x_api_key)

    base_url = request_base_url(http_request)
    loaded: list[OpenWebUILoaderResult] = []
    for url in request.urls:
        document_id = document_id_from_url(url)
        if document_id is None:
            continue

        document = repository.get(document_id, include_content=False)
        if document is None or not document.markdown:
            continue

        loaded.append(
            OpenWebUILoaderResult(
                page_content=_truncate_loader_content(
                    document.markdown,
                    settings.openwebui_loader_max_chars,
                ),
                metadata={
                    "source": document_frontend_url(base_url, document.id),
                    "title": document.title,
                    "document_id": str(document.id),
                    "original_filename": document.original_filename,
                    "mime_type": document.mime_type,
                    "status": str(document.status),
                },
            )
        )

    return loaded


def _keyword_search_documents(
    repository: DocumentRepository,
    query: str,
    count: int,
    base_url: str,
) -> list[OpenWebUISearchResult]:
    normalized_query = query.casefold().strip()
    if not normalized_query:
        return []

    results: list[OpenWebUISearchResult] = []
    for document in repository.list():
        markdown = document.markdown or ""
        if normalized_query not in markdown.casefold():
            continue

        snippets: list[str] = []
        for chunk in chunk_markdown(document.id, markdown):
            if normalized_query in chunk.text.casefold():
                snippets.append(_snippet(chunk.text, query))
            if len(snippets) >= 3:
                break

        results.append(
            OpenWebUISearchResult(
                link=document_frontend_url(base_url, document.id),
                title=document.title,
                snippet="\n\n".join(snippets) or _snippet(markdown, query),
            )
        )

        if len(results) >= count:
            break

    return results


def _snippet(text: str, query: str, radius: int = 180) -> str:
    position = text.casefold().find(query.casefold())
    if position < 0:
        return text[: radius * 2].strip()

    start = max(position - radius, 0)
    end = min(position + len(query) + radius, len(text))
    return text[start:end].strip()


def _truncate_loader_content(markdown: str, max_chars: int) -> str:
    if max_chars <= 0 or len(markdown) <= max_chars:
        return markdown

    return (
        markdown[:max_chars].rstrip()
        + "\n\n_The recognized document is longer; open the source link for the full text._"
    )
