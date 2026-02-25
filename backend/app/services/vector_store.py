"""
Persistent vector store using numpy + JSON.
Simple, dependency-free alternative to ChromaDB that works with any Python version.
For a portfolio project with hundreds of documents, this is fast enough (<10ms queries).
"""

import json
from pathlib import Path

import numpy as np


class VectorStoreService:
    def __init__(self, persist_directory: str = "./data/vectorstore"):
        self.persist_dir = Path(persist_directory)
        self.persist_dir.mkdir(parents=True, exist_ok=True)

        self._ids: list[str] = []
        self._embeddings: np.ndarray | None = None
        self._documents: list[str] = []
        self._metadatas: list[dict] = []

        self._load()

    def _load(self):
        index_path = self.persist_dir / "index.json"
        embeddings_path = self.persist_dir / "embeddings.npy"

        if index_path.exists() and embeddings_path.exists():
            with open(index_path, "r") as f:
                data = json.load(f)
            self._ids = data["ids"]
            self._documents = data["documents"]
            self._metadatas = data["metadatas"]
            self._embeddings = np.load(str(embeddings_path))
        else:
            self._ids = []
            self._embeddings = None
            self._documents = []
            self._metadatas = []

    def _save(self):
        index_path = self.persist_dir / "index.json"
        embeddings_path = self.persist_dir / "embeddings.npy"

        with open(index_path, "w") as f:
            json.dump({
                "ids": self._ids,
                "documents": self._documents,
                "metadatas": self._metadatas,
            }, f)

        if self._embeddings is not None:
            np.save(str(embeddings_path), self._embeddings)

    def add_chunks(
        self,
        ids: list[str],
        embeddings: list[list[float]],
        documents: list[str],
        metadatas: list[dict],
    ):
        new_embeddings = np.array(embeddings, dtype=np.float32)

        self._ids.extend(ids)
        self._documents.extend(documents)
        self._metadatas.extend(metadatas)

        if self._embeddings is None:
            self._embeddings = new_embeddings
        else:
            self._embeddings = np.vstack([self._embeddings, new_embeddings])

        self._save()

    def query(
        self,
        query_embedding: list[float],
        n_results: int = 10,
        where_filter: dict | None = None,
    ) -> dict:
        if self._embeddings is None or len(self._ids) == 0:
            return {"ids": [[]], "documents": [[]], "metadatas": [[]], "distances": [[]]}

        query_vec = np.array(query_embedding, dtype=np.float32)

        # Cosine similarity (embeddings are already normalized)
        similarities = self._embeddings @ query_vec

        # Apply metadata filter if provided
        valid_indices = list(range(len(self._ids)))
        if where_filter:
            valid_indices = [
                i for i in valid_indices
                if all(self._metadatas[i].get(k) == v for k, v in where_filter.items())
            ]

        if not valid_indices:
            return {"ids": [[]], "documents": [[]], "metadatas": [[]], "distances": [[]]}

        # Get top-N from valid indices
        valid_sims = [(i, similarities[i]) for i in valid_indices]
        valid_sims.sort(key=lambda x: x[1], reverse=True)
        top_indices = [i for i, _ in valid_sims[:n_results]]

        return {
            "ids": [[self._ids[i] for i in top_indices]],
            "documents": [[self._documents[i] for i in top_indices]],
            "metadatas": [[self._metadatas[i] for i in top_indices]],
            "distances": [[float(1 - similarities[i]) for i in top_indices]],
        }

    def delete_by_file(self, file_id: str):
        indices_to_keep = [
            i for i, m in enumerate(self._metadatas) if m.get("file_id") != file_id
        ]

        self._ids = [self._ids[i] for i in indices_to_keep]
        self._documents = [self._documents[i] for i in indices_to_keep]
        self._metadatas = [self._metadatas[i] for i in indices_to_keep]

        if self._embeddings is not None and indices_to_keep:
            self._embeddings = self._embeddings[indices_to_keep]
        else:
            self._embeddings = None

        self._save()

    def count(self) -> int:
        return len(self._ids)
