import json
from datetime import datetime, timezone

from sqlalchemy.ext.asyncio import AsyncSession

from app.models.activity import ActivityEvent


class ActivityService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def log_event(
        self,
        event_type: str,
        file_id: str | None = None,
        detail: dict | None = None,
    ):
        event = ActivityEvent(
            event_type=event_type,
            file_id=file_id,
            detail=json.dumps(detail) if detail else None,
        )
        self.db.add(event)
        await self.db.commit()
