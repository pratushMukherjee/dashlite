import time
import json

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.chunk import Chunk
from app.models.activity import ActivityEvent
from app.services.llm_client import LLMClient
from app.schemas.summarize import SummarizeResponse

SUMMARIZE_PROMPT = """Summarize the following document content concisely. Highlight:
- Key points and findings
- Important decisions or recommendations
- Notable data or metrics

Document: {file_name}

Content:
{content}

Provide a clear, structured summary in 3-5 paragraphs using markdown formatting."""


class SummarizerService:
    def __init__(self, llm_client: LLMClient, db: AsyncSession):
        self.llm_client = llm_client
        self.db = db

    async def summarize(self, file_id: str, file_name: str) -> SummarizeResponse:
        start = time.time()

        # Get all chunks for this file
        result = await self.db.execute(
            select(Chunk).where(Chunk.file_id == file_id).order_by(Chunk.chunk_index)
        )
        chunks = result.scalars().all()

        if not chunks:
            return SummarizeResponse(
                file_id=file_id,
                file_name=file_name,
                summary="No content available to summarize.",
                latency_ms=0,
            )

        # Join chunks, truncate if too long
        full_text = "\n".join(c.text for c in chunks)
        if len(full_text) > 8000:
            full_text = full_text[:8000] + "\n\n[Content truncated for summarization]"

        prompt = SUMMARIZE_PROMPT.format(file_name=file_name, content=full_text)
        summary = self.llm_client.generate(
            prompt,
            system="You are DashLite, an AI assistant that summarizes documents clearly and concisely.",
            max_tokens=1024,
        )

        latency_ms = int((time.time() - start) * 1000)

        # Log activity
        activity = ActivityEvent(
            event_type="summary_generated",
            file_id=file_id,
            detail=json.dumps({"file_name": file_name}),
        )
        self.db.add(activity)
        await self.db.commit()

        return SummarizeResponse(
            file_id=file_id,
            file_name=file_name,
            summary=summary,
            latency_ms=latency_ms,
        )
