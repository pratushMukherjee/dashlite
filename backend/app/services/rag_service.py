import time
import json

from sqlalchemy.ext.asyncio import AsyncSession

from app.models.query_log import QueryLog
from app.models.activity import ActivityEvent
from app.services.search_service import SearchService
from app.services.llm_client import LLMClient
from app.schemas.ask import AskResponse, SourceCitation
from app.config import settings

SYSTEM_PROMPT = """You are DashLite, an AI assistant that answers questions based on the user's indexed documents.

Rules:
- Answer ONLY based on the provided sources. Do not use outside knowledge.
- If the sources don't contain enough information, say so clearly.
- Always cite which source(s) you used by referencing [Source N].
- Be concise but thorough. Use markdown formatting for readability."""

RAG_PROMPT_TEMPLATE = """Sources:
{context}

Question: {question}

Provide a clear, well-structured answer with source citations [Source N]."""


class RAGService:
    """
    Retrieval-Augmented Generation pipeline.
    Mirrors Dash's approach: retrieve relevant chunks, build context, generate answer.
    """

    def __init__(
        self,
        search_service: SearchService,
        llm_client: LLMClient,
        db: AsyncSession,
    ):
        self.search_service = search_service
        self.llm_client = llm_client
        self.db = db

    async def ask(self, question: str, max_sources: int = 5) -> AskResponse:
        start = time.time()

        # 1. Retrieve relevant chunks using hybrid search
        search_response = await self.search_service.hybrid_search(question, limit=max_sources)

        # 2. Build context with source tracking
        context_parts = []
        sources = []
        for i, result in enumerate(search_response.results):
            context_parts.append(f"[Source {i + 1}: {result.file_name}]\n{result.text}")
            sources.append(SourceCitation(
                file_id=result.file_id,
                file_name=result.file_name,
                chunk_text=result.text[:200],
                relevance_score=result.score,
            ))

        # 3. Generate answer
        if not context_parts:
            answer = "I couldn't find any relevant information in your indexed files. Try ingesting more documents or rephrasing your question."
        else:
            prompt = RAG_PROMPT_TEMPLATE.format(
                context="\n\n".join(context_parts),
                question=question,
            )
            answer = self.llm_client.generate(prompt, system=SYSTEM_PROMPT)

        latency_ms = int((time.time() - start) * 1000)

        # 4. Log query
        log = QueryLog(query_text=question, query_type="ask", result_count=len(sources), latency_ms=latency_ms)
        self.db.add(log)
        activity = ActivityEvent(event_type="query_ask", detail=json.dumps({"question": question[:100]}))
        self.db.add(activity)
        await self.db.commit()

        return AskResponse(answer=answer, sources=sources, question=question, latency_ms=latency_ms)

    async def ask_stream(self, question: str, max_sources: int = 5):
        """Streaming version for SSE endpoint."""
        search_response = await self.search_service.hybrid_search(question, limit=max_sources)

        context_parts = []
        sources = []
        for i, result in enumerate(search_response.results):
            context_parts.append(f"[Source {i + 1}: {result.file_name}]\n{result.text}")
            sources.append({
                "file_id": result.file_id,
                "file_name": result.file_name,
                "relevance_score": result.score,
            })

        if not context_parts:
            yield json.dumps({"type": "answer", "content": "No relevant information found."})
            return

        # Send sources first
        yield json.dumps({"type": "sources", "data": sources})

        # Stream answer
        prompt = RAG_PROMPT_TEMPLATE.format(
            context="\n\n".join(context_parts),
            question=question,
        )
        for chunk in self.llm_client.generate_stream(prompt, system=SYSTEM_PROMPT):
            yield json.dumps({"type": "answer", "content": chunk})
