# ML Pipeline Design: CloudSync Semantic Search

## Overview
This document outlines the machine learning pipeline for CloudSync's hybrid search feature. The pipeline handles document ingestion, embedding generation, index management, and query processing.

## Architecture

### Ingestion Pipeline
```
File Upload → Text Extraction → Chunking → Embedding → Vector Store
```

1. **Text Extraction**: Extract text from supported file types
   - PDF: PyPDF2 with fallback to OCR for scanned documents
   - DOCX: python-docx for structured extraction
   - Images: Tesseract OCR
   - Code/Text: Direct UTF-8 read

2. **Chunking Strategy**
   - Recursive character text splitting
   - Chunk size: 512 characters (balances context and retrieval precision)
   - Overlap: 50 characters (ensures no context lost at boundaries)
   - Preserves paragraph and sentence boundaries where possible

3. **Embedding Generation**
   - Model: all-MiniLM-L6-v2 (384 dimensions)
   - Batch processing: 256 chunks per batch
   - Normalization: L2 normalization for cosine similarity
   - Throughput: ~2000 chunks/second on GPU, ~200/second on CPU

4. **Vector Store**
   - Development: ChromaDB (local, embedded)
   - Production: Pinecone (managed, scalable)
   - Index type: HNSW (Hierarchical Navigable Small World)
   - Distance metric: Cosine similarity

### Query Pipeline
```
Query → Embed → Vector Search ──┐
Query → Tokenize → BM25 Search ─┤→ RRF Merge → Rerank → Results
```

1. **Dual Retrieval**
   - Semantic: Embed query, find top-K nearest vectors
   - Lexical: BM25 scoring over inverted index (SQLite FTS5)

2. **Reciprocal Rank Fusion (RRF)**
   - Standard method for merging heterogeneous rankings
   - Score = Σ 1/(k + rank_i) across all retrieval methods
   - k=60 is the widely-accepted constant

3. **Optional Reranking**
   - Cross-encoder reranking for top-20 results (production only)
   - Model: cross-encoder/ms-marco-MiniLM-L-6-v2
   - Adds ~50ms latency but improves precision by 8-12%

## Monitoring
- Track NDCG@10, MRR, and Recall@20 weekly
- A/B test new models against production baseline
- Alert if search latency p95 exceeds 100ms
- Monitor embedding drift quarterly

## Scaling Considerations
- At 1M documents (~5M chunks): ChromaDB on single node is sufficient
- At 10M documents: Migrate to Pinecone with pod-based scaling
- At 100M documents: Consider sharding by tenant + dedicated pods for enterprise
- Embedding generation can be parallelized across GPU workers
