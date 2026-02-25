from pydantic_settings import BaseSettings
from pathlib import Path


class Settings(BaseSettings):
    # API Keys
    openai_api_key: str = ""

    # Paths
    watched_directory: str = "./demo/sample_files"
    chroma_persist_dir: str = "./data/vectorstore"
    sqlite_url: str = "sqlite+aiosqlite:///./data/dashlite.db"

    # Models
    embedding_model: str = "all-MiniLM-L6-v2"
    openai_model: str = "gpt-4o-mini"

    # Server
    backend_host: str = "0.0.0.0"
    backend_port: int = 8000
    frontend_url: str = "http://localhost:5173"

    # Search Tuning
    chunk_size: int = 512
    chunk_overlap: int = 50
    search_default_limit: int = 10
    rrf_k: int = 60
    rag_max_sources: int = 5
    rag_max_context_tokens: int = 3000

    model_config = {"env_file": ["../.env", ".env"], "env_file_encoding": "utf-8"}


settings = Settings()
