from functools import lru_cache

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.config import settings
from app.services.embedder import EmbeddingService
from app.services.vector_store import VectorStoreService
from app.services.search_service import SearchService
from app.services.llm_client import LLMClient
from app.services.rag_service import RAGService
from app.services.summarizer import SummarizerService
from app.services.agent_service import AgentService
from app.services.ingest_service import IngestService


@lru_cache()
def get_embedder() -> EmbeddingService:
    return EmbeddingService(model_name=settings.embedding_model)


@lru_cache()
def get_vector_store() -> VectorStoreService:
    return VectorStoreService(persist_directory=settings.chroma_persist_dir)


@lru_cache()
def get_llm_client() -> LLMClient:
    return LLMClient(api_key=settings.openai_api_key, model=settings.openai_model)


def get_search_service(
    db: AsyncSession = Depends(get_db),
    embedder: EmbeddingService = Depends(get_embedder),
    vector_store: VectorStoreService = Depends(get_vector_store),
) -> SearchService:
    return SearchService(db=db, embedder=embedder, vector_store=vector_store)


def get_rag_service(
    search_service: SearchService = Depends(get_search_service),
    llm_client: LLMClient = Depends(get_llm_client),
    db: AsyncSession = Depends(get_db),
) -> RAGService:
    return RAGService(search_service=search_service, llm_client=llm_client, db=db)


def get_summarizer_service(
    llm_client: LLMClient = Depends(get_llm_client),
    db: AsyncSession = Depends(get_db),
) -> SummarizerService:
    return SummarizerService(llm_client=llm_client, db=db)


def get_agent_service(
    search_service: SearchService = Depends(get_search_service),
    llm_client: LLMClient = Depends(get_llm_client),
    db: AsyncSession = Depends(get_db),
) -> AgentService:
    return AgentService(search_service=search_service, llm_client=llm_client, db=db)


def get_ingest_service(
    db: AsyncSession = Depends(get_db),
    embedder: EmbeddingService = Depends(get_embedder),
    vector_store: VectorStoreService = Depends(get_vector_store),
) -> IngestService:
    return IngestService(db=db, embedder=embedder, vector_store=vector_store)
