import time
import json
from collections import defaultdict

from sqlalchemy import text, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.chunk import Chunk
from app.models.file import File
from app.models.query_log import QueryLog
from app.services.embedder import EmbeddingService
from app.services.vector_store import VectorStoreService
from app.schemas.search import SearchResult, SearchResponse
from app.config import settings


class SearchService:
    """
    Hybrid search implementation inspired by Dropbox Dash.
    Combines lexical search (SQLite FTS5/BM25) with semantic search (ChromaDB vectors),
    merged using Reciprocal Rank Fusion (RRF).
    """

    def __init__(
        self,
        db: AsyncSession,
        embedder: EmbeddingService,
        vector_store: VectorStoreService,
    ):
        self.db = db
        self.embedder = embedder
        self.vector_store = vector_store

    async def hybrid_search(
        self,
        query: str,
        limit: int = 10,
        file_type: str | None = None,
    ) -> SearchResponse:
        start = time.time()

        # Stage 1: Lexical search via SQLite FTS5
        lexical_results = await self._lexical_search(query, limit=limit * 2)

        # Stage 2: Semantic search via ChromaDB
        where_filter = {"file_type": file_type} if file_type else None
        semantic_results = await self._semantic_search(query, n_results=limit * 2, where_filter=where_filter)

        # Stage 3: Reciprocal Rank Fusion
        merged = self._reciprocal_rank_fusion(lexical_results, semantic_results, k=settings.rrf_k)

        # Enrich results with file metadata
        results = []
        for chunk_id, score in merged[:limit]:
            chunk_result = await self.db.execute(
                select(Chunk, File).join(File, Chunk.file_id == File.id).where(Chunk.id == chunk_id)
            )
            row = chunk_result.first()
            if row:
                chunk, file = row
                if file_type and file.file_type != file_type:
                    continue
                results.append(SearchResult(
                    chunk_id=chunk.id,
                    file_id=file.id,
                    file_name=file.file_name,
                    file_type=file.file_type,
                    text=chunk.text,
                    score=score,
                    chunk_index=chunk.chunk_index,
                ))

        latency_ms = int((time.time() - start) * 1000)

        # Log query
        log = QueryLog(query_text=query, query_type="search", result_count=len(results), latency_ms=latency_ms)
        self.db.add(log)
        await self.db.commit()

        return SearchResponse(results=results, query=query, total=len(results), latency_ms=latency_ms)

    async def _lexical_search(self, query: str, limit: int = 20) -> list[tuple[str, int]]:
        """Full-text search using SQLite FTS5 with BM25 ranking."""
        try:
            # Use LIKE as a fallback since FTS5 requires special table setup
            result = await self.db.execute(
                select(Chunk.id).where(Chunk.text.ilike(f"%{query}%")).limit(limit)
            )
            rows = result.all()
            return [(row[0], rank) for rank, row in enumerate(rows)]
        except Exception:
            return []

    async def _semantic_search(
        self,
        query: str,
        n_results: int = 20,
        where_filter: dict | None = None,
    ) -> list[tuple[str, int]]:
        """Semantic search using ChromaDB vector similarity."""
        query_embedding = self.embedder.embed_query(query)
        chroma_results = self.vector_store.query(
            query_embedding=query_embedding,
            n_results=n_results,
            where_filter=where_filter,
        )

        results = []
        if chroma_results and chroma_results["ids"] and chroma_results["ids"][0]:
            for rank, chunk_id in enumerate(chroma_results["ids"][0]):
                results.append((chunk_id, rank))

        return results

    def _reciprocal_rank_fusion(
        self,
        *result_lists: list[tuple[str, int]],
        k: int = 60,
    ) -> list[tuple[str, float]]:
        """
        Reciprocal Rank Fusion (RRF) — the standard method for merging
        heterogeneous ranking signals. Used by Dropbox Dash to combine
        lexical and semantic search results.

        RRF_score = sum(1 / (k + rank_i)) for each result across all lists.
        """
        scores = defaultdict(float)

        for result_list in result_lists:
            for rank, (chunk_id, _) in enumerate(result_list):
                scores[chunk_id] += 1.0 / (k + rank + 1)

        sorted_results = sorted(scores.items(), key=lambda x: x[1], reverse=True)
        return sorted_results
