from datetime import datetime
from pydantic import BaseModel


class FileResponse(BaseModel):
    id: str
    file_path: str
    file_name: str
    file_type: str
    file_size: int
    chunk_count: int
    status: str
    error_message: str | None = None
    created_at: datetime
    indexed_at: datetime | None = None

    model_config = {"from_attributes": True}


class FileListResponse(BaseModel):
    files: list[FileResponse]
    total: int


class FileStatsResponse(BaseModel):
    total_files: int
    total_chunks: int
    files_by_type: dict[str, int]
    total_size_bytes: int
