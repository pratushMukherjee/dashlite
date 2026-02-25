from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.models.file import File
from app.models.chunk import Chunk
from app.schemas.file import FileResponse, FileListResponse, FileStatsResponse

router = APIRouter()


@router.get("", response_model=FileListResponse)
async def list_files(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    file_type: str | None = Query(None),
    db: AsyncSession = Depends(get_db),
):
    query = select(File).order_by(File.created_at.desc())
    if file_type:
        query = query.where(File.file_type == file_type)

    count_query = select(func.count()).select_from(File)
    if file_type:
        count_query = count_query.where(File.file_type == file_type)

    total = (await db.execute(count_query)).scalar() or 0
    result = await db.execute(query.offset(skip).limit(limit))
    files = result.scalars().all()

    return FileListResponse(files=[FileResponse.model_validate(f) for f in files], total=total)


@router.get("/stats", response_model=FileStatsResponse)
async def file_stats(db: AsyncSession = Depends(get_db)):
    total_files = (await db.execute(select(func.count()).select_from(File))).scalar() or 0
    total_chunks = (await db.execute(select(func.count()).select_from(Chunk))).scalar() or 0
    total_size = (await db.execute(select(func.coalesce(func.sum(File.file_size), 0)))).scalar() or 0

    type_rows = (await db.execute(
        select(File.file_type, func.count()).group_by(File.file_type)
    )).all()
    files_by_type = {row[0]: row[1] for row in type_rows}

    return FileStatsResponse(
        total_files=total_files,
        total_chunks=total_chunks,
        files_by_type=files_by_type,
        total_size_bytes=total_size,
    )


@router.get("/{file_id}", response_model=FileResponse)
async def get_file(file_id: str, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(File).where(File.id == file_id))
    file = result.scalar_one_or_none()
    if not file:
        raise HTTPException(status_code=404, detail="File not found")
    return FileResponse.model_validate(file)


@router.get("/{file_id}/content")
async def get_file_content(file_id: str, db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(Chunk).where(Chunk.file_id == file_id).order_by(Chunk.chunk_index)
    )
    chunks = result.scalars().all()
    if not chunks:
        raise HTTPException(status_code=404, detail="No content found for this file")
    full_text = " ".join(c.text for c in chunks)
    return {"file_id": file_id, "content": full_text, "chunk_count": len(chunks)}
