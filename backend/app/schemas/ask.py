from pydantic import BaseModel


class AskRequest(BaseModel):
    question: str
    max_sources: int = 5


class SourceCitation(BaseModel):
    file_id: str
    file_name: str
    chunk_text: str
    relevance_score: float


class AskResponse(BaseModel):
    answer: str
    sources: list[SourceCitation]
    question: str
    latency_ms: int
