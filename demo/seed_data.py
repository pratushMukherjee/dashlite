"""
Seed script: Ingest all demo sample files into DashLite.
Run from the backend directory: python -m demo.seed_data
Or from project root: cd backend && python -c "import asyncio; from demo_seed import seed; asyncio.run(seed())"
"""

import asyncio
import sys
import os

# Add backend to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "backend"))


async def seed():
    from app.config import settings
    from app.db.session import init_db, AsyncSessionLocal
    from app.services.embedder import EmbeddingService
    from app.services.vector_store import VectorStoreService
    from app.services.ingest_service import IngestService

    print("Initializing database...")
    await init_db()

    print("Loading embedding model (first time may take a minute)...")
    embedder = EmbeddingService(model_name=settings.embedding_model)
    vector_store = VectorStoreService(persist_directory=settings.chroma_persist_dir)

    sample_dir = os.path.join(os.path.dirname(__file__), "sample_files")

    async with AsyncSessionLocal() as db:
        ingest_service = IngestService(db=db, embedder=embedder, vector_store=vector_store)

        print(f"Ingesting files from {sample_dir}...")
        results = await ingest_service.ingest_directory(sample_dir)

        print(f"\nResults:")
        print(f"  Success: {results['success']}")
        print(f"  Failed:  {results['failed']}")
        print(f"  Skipped: {results['skipped']}")

        for f in results.get("files", []):
            status_icon = "+" if f["status"] == "success" else "x"
            print(f"  [{status_icon}] {f['file']}")

    print("\nSeed complete! Start the app and try searching.")


if __name__ == "__main__":
    asyncio.run(seed())
