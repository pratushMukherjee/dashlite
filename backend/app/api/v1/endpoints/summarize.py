from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.models.file import File
from app.schemas.summarize import SummarizeResponse
from app.services.summarizer import SummarizerService
from app.dependencies import get_summarizer_service

router = APIRouter()


@router.post("/{file_id}", response_model=SummarizeResponse)
async def summarize_file(
    file_id: str,
    summarizer: SummarizerService = Depends(get_summarizer_service),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(select(File).where(File.id == file_id))
    file = result.scalar_one_or_none()
    if not file:
        raise HTTPException(status_code=404, detail="File not found")

    return await summarizer.summarize(file_id, file.file_name)
