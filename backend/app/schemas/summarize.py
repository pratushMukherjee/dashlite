from pydantic import BaseModel


class SummarizeResponse(BaseModel):
    file_id: str
    file_name: str
    summary: str
    latency_ms: int
