from fastapi import APIRouter, Depends, Query
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime, timezone, timedelta

from app.db.session import get_db
from app.models.activity import ActivityEvent
from app.models.file import File
from app.models.query_log import QueryLog
from app.schemas.activity import ActivityEventResponse, ActivityFeedResponse, ActivityStatsResponse

router = APIRouter()


@router.get("/feed", response_model=ActivityFeedResponse)
async def activity_feed(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
):
    total = (await db.execute(select(func.count()).select_from(ActivityEvent))).scalar() or 0
    result = await db.execute(
        select(ActivityEvent).order_by(ActivityEvent.created_at.desc()).offset(skip).limit(limit)
    )
    events = result.scalars().all()
    return ActivityFeedResponse(
        events=[ActivityEventResponse.model_validate(e) for e in events],
        total=total,
    )


@router.get("/stats", response_model=ActivityStatsResponse)
async def activity_stats(db: AsyncSession = Depends(get_db)):
    total_files = (await db.execute(select(func.count()).select_from(File))).scalar() or 0
    total_queries = (await db.execute(select(func.count()).select_from(QueryLog))).scalar() or 0

    today_start = datetime.now(timezone.utc).replace(hour=0, minute=0, second=0, microsecond=0)
    queries_today = (await db.execute(
        select(func.count()).select_from(QueryLog).where(QueryLog.created_at >= today_start)
    )).scalar() or 0

    type_rows = (await db.execute(
        select(File.file_type, func.count()).group_by(File.file_type)
    )).all()
    files_by_type = {row[0]: row[1] for row in type_rows}

    return ActivityStatsResponse(
        total_files=total_files,
        total_queries=total_queries,
        queries_today=queries_today,
        files_by_type=files_by_type,
    )
