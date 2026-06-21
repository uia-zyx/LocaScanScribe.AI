from typing import Annotated

from fastapi import APIRouter, Depends, Header

from app.api.deps import get_document_repository, get_search_service
from app.api.openwebui_utils import (
    document_frontend_url,
    document_id_from_url,
    validate_openwebui_key,
)
from app.api.schemas import (
    OpenWebUILoaderRequest,
    OpenWebUILoaderResult,
    OpenWebUISearchRequest,
    OpenWebUISearchResult,
    SearchRequest,
)
from app.core.settings import Settings, get_settings
from app.ingestion.repository import DocumentRepository
from app.search.service import SearchService

router = APIRouter(prefix="/openwebui", tags=["openwebui"])


@router.post("/web-search", response_model=list[OpenWebUISearchResult])
async def openwebui_web_search(
    request: OpenWebUISearchRequest,
    settings: Annotated[Settings, Depends(get_settings)],
    search_service: Annotated[SearchService, Depends(get_search_service)],
    authorization: Annotated[str | None, Header()] = None,
    x_api_key: Annotated[str | None, Header()] = None,
) -> list[OpenWebUISearchResult]:
    validate_openwebui_key(settings, authorization, x_api_key)

    results = await search_service.search(SearchRequest(query=request.query, limit=request.count))
    return [
        OpenWebUISearchResult(
            link=document_frontend_url(settings, result.document_id),
            title=result.title,
            snippet="\n\n".join(snippet.phrase for snippet in result.snippets),
        )
        for result in results[: request.count]
    ]


@router.post("/web-loader", response_model=list[OpenWebUILoaderResult])
async def openwebui_web_loader(
    request: OpenWebUILoaderRequest,
    settings: Annotated[Settings, Depends(get_settings)],
    repository: Annotated[DocumentRepository, Depends(get_document_repository)],
    authorization: Annotated[str | None, Header()] = None,
    x_api_key: Annotated[str | None, Header()] = None,
) -> list[OpenWebUILoaderResult]:
    validate_openwebui_key(settings, authorization, x_api_key)

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
                page_content=document.markdown,
                metadata={
                    "source": document_frontend_url(settings, document.id),
                    "title": document.title,
                    "document_id": str(document.id),
                    "original_filename": document.original_filename,
                    "mime_type": document.mime_type,
                    "status": document.status,
                },
            )
        )

    return loaded
