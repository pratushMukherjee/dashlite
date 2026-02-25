import os
import json
from pathlib import Path
from datetime import datetime, timezone

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.file import File
from app.models.chunk import Chunk
from app.models.activity import ActivityEvent
from app.services.file_processor import FileProcessor
from app.services.chunker import TextChunker
from app.services.embedder import EmbeddingService
from app.services.vector_store import VectorStoreService
from app.utils.file_types import is_supported, get_file_type
from app.config import settings


class IngestService:
    def __init__(
        self,
        db: AsyncSession,
        embedder: EmbeddingService,
        vector_store: VectorStoreService,
    ):
        self.db = db
        self.embedder = embedder
        self.vector_store = vector_store
        self.file_processor = FileProcessor()
        self.chunker = TextChunker(
            chunk_size=settings.chunk_size,
            chunk_overlap=settings.chunk_overlap,
        )

    async def ingest_file(self, file_path: str) -> File:
        path = Path(file_path).resolve()

        # Check if already indexed
        existing = await self.db.execute(
            select(File).where(File.file_path == str(path))
        )
        if existing.scalar_one_or_none():
            raise ValueError(f"File already indexed: {path}")

        # Process file
        processed = await self.file_processor.process_file(str(path))

        # Create File record
        file_record = File(
            file_path=str(path),
            file_name=processed.metadata["file_name"],
            file_type=processed.metadata["file_type"],
            file_size=processed.metadata["file_size"],
            content_hash=processed.content_hash,
            page_count=processed.metadata.get("page_count"),
            status="processing",
        )
        self.db.add(file_record)
        await self.db.flush()

        try:
            # Chunk text
            text_chunks = self.chunker.chunk_text(processed.text)

            if not text_chunks:
                file_record.status = "indexed"
                file_record.chunk_count = 0
                file_record.indexed_at = datetime.now(timezone.utc)
                await self.db.commit()
                return file_record

            # Save chunks to DB
            chunk_records = []
            for tc in text_chunks:
                chunk_record = Chunk(
                    file_id=file_record.id,
                    chunk_index=tc.chunk_index,
                    text=tc.text,
                    char_start=tc.char_start,
                    char_end=tc.char_end,
                    token_count=len(tc.text.split()),
                )
                self.db.add(chunk_record)
                chunk_records.append(chunk_record)

            await self.db.flush()

            # Generate embeddings
            texts = [c.text for c in chunk_records]
            embeddings = self.embedder.embed_texts(texts)

            # Add to vector store
            self.vector_store.add_chunks(
                ids=[c.id for c in chunk_records],
                embeddings=embeddings,
                documents=texts,
                metadatas=[
                    {
                        "file_id": file_record.id,
                        "file_name": file_record.file_name,
                        "file_type": file_record.file_type,
                        "chunk_index": c.chunk_index,
                    }
                    for c in chunk_records
                ],
            )

            # Update file record
            file_record.status = "indexed"
            file_record.chunk_count = len(chunk_records)
            file_record.indexed_at = datetime.now(timezone.utc)

            # Log activity
            activity = ActivityEvent(
                event_type="file_added",
                file_id=file_record.id,
                detail=json.dumps({"file_name": file_record.file_name, "chunks": len(chunk_records)}),
            )
            self.db.add(activity)

            await self.db.commit()
            return file_record

        except Exception as e:
            file_record.status = "error"
            file_record.error_message = str(e)
            await self.db.commit()
            raise

    async def ingest_directory(self, directory_path: str) -> dict:
        results = {"success": 0, "failed": 0, "skipped": 0, "files": []}

        for root, _, files in os.walk(directory_path):
            for filename in sorted(files):
                file_path = os.path.join(root, filename)

                if not is_supported(file_path):
                    results["skipped"] += 1
                    continue

                try:
                    file_record = await self.ingest_file(file_path)
                    results["success"] += 1
                    results["files"].append({"file": filename, "status": "success", "id": file_record.id})
                except ValueError:
                    results["skipped"] += 1
                except Exception as e:
                    results["failed"] += 1
                    results["files"].append({"file": filename, "status": "error", "error": str(e)})

        return results

    async def delete_file(self, file_id: str):
        result = await self.db.execute(select(File).where(File.id == file_id))
        file = result.scalar_one_or_none()
        if not file:
            raise ValueError("File not found")

        # Remove from vector store
        self.vector_store.delete_by_file(file_id)

        # Log activity
        activity = ActivityEvent(
            event_type="file_deleted",
            file_id=file_id,
            detail=json.dumps({"file_name": file.file_name}),
        )
        self.db.add(activity)

        # Delete from DB (cascades to chunks)
        await self.db.delete(file)
        await self.db.commit()
