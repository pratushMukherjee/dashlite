from pydantic import BaseModel


class SearchQuery(BaseModel):
    query: str
    file_type: str | None = None
    limit: int = 10


class SearchResult(BaseModel):
    chunk_id: str
    file_id: str
    file_name: str
    file_type: str
    text: str
    score: float
    chunk_index: int


class SearchResponse(BaseModel):
    results: list[SearchResult]
    query: str
    total: int
    latency_ms: int
