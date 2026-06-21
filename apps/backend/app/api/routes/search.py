from typing import Annotated

from fastapi import APIRouter, Depends

from app.api.deps import get_search_service
from app.api.schemas import SearchRequest, SearchResponse
from app.search.service import SearchService

router = APIRouter(prefix="/search", tags=["search"])


@router.post("", response_model=SearchResponse)
async def search(
    request: SearchRequest,
    service: Annotated[SearchService, Depends(get_search_service)],
) -> SearchResponse:
    return SearchResponse(items=await service.search(request))

