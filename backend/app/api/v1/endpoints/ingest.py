import os
from pathlib import Path

from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.services.ingest_service import IngestService
from app.dependencies import get_ingest_service

router = APIRouter()


class IngestFileRequest(BaseModel):
    file_path: str


class IngestDirectoryRequest(BaseModel):
    directory_path: str


@router.post("")
async def ingest_file(
    request: IngestFileRequest,
    background_tasks: BackgroundTasks,
    ingest_service: IngestService = Depends(get_ingest_service),
):
    path = Path(request.file_path)
    if not path.exists():
        raise HTTPException(status_code=400, detail=f"File not found: {request.file_path}")

    file_record = await ingest_service.ingest_file(str(path))
    return {"message": "File ingested successfully", "file_id": file_record.id, "status": file_record.status}


@router.post("/directory")
async def ingest_directory(
    request: IngestDirectoryRequest,
    ingest_service: IngestService = Depends(get_ingest_service),
):
    dir_path = Path(request.directory_path)
    if not dir_path.exists() or not dir_path.is_dir():
        raise HTTPException(status_code=400, detail=f"Directory not found: {request.directory_path}")

    results = await ingest_service.ingest_directory(str(dir_path))
    return {
        "message": f"Ingested {results['success']} files, {results['failed']} failed, {results['skipped']} skipped",
        "details": results,
    }


@router.delete("/{file_id}")
async def delete_file(
    file_id: str,
    ingest_service: IngestService = Depends(get_ingest_service),
):
    await ingest_service.delete_file(file_id)
    return {"message": "File removed from index"}
