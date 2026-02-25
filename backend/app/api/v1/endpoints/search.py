from fastapi import APIRouter, Depends, Query

from app.schemas.search import SearchResponse
from app.services.search_service import SearchService
from app.dependencies import get_search_service

router = APIRouter()


@router.get("", response_model=SearchResponse)
async def search_files(
    q: str = Query(..., min_length=1),
    file_type: str | None = Query(None),
    limit: int = Query(10, ge=1, le=50),
    search_service: SearchService = Depends(get_search_service),
):
    return await search_service.hybrid_search(q, limit=limit, file_type=file_type)
