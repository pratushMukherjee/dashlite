from datetime import datetime
from pydantic import BaseModel


class ActivityEventResponse(BaseModel):
    id: int
    event_type: str
    file_id: str | None = None
    detail: str | None = None
    created_at: datetime

    model_config = {"from_attributes": True}


class ActivityFeedResponse(BaseModel):
    events: list[ActivityEventResponse]
    total: int


class ActivityStatsResponse(BaseModel):
    total_files: int
    total_queries: int
    queries_today: int
    files_by_type: dict[str, int]
