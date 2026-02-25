# Embedding Model Evaluation Results

## Experiment Overview
Evaluated three embedding models for the CloudSync semantic search feature. Goal: find the best balance of search quality, latency, and cost for our hybrid search pipeline.

## Models Tested
1. **all-MiniLM-L6-v2** (sentence-transformers, 384 dimensions)
2. **text-embedding-3-small** (OpenAI, 1536 dimensions)
3. **nomic-embed-text-v1.5** (Nomic AI, 768 dimensions)

## Dataset
- 50,000 document chunks from production data (anonymized)
- 200 human-labeled query-relevance pairs for evaluation
- File types: PDF (40%), DOCX (25%), TXT/MD (20%), Code (15%)

## Results

### Search Quality (NDCG@10)
| Model | NDCG@10 | MRR | Recall@20 |
|-------|---------|-----|-----------|
| all-MiniLM-L6-v2 | 0.72 | 0.68 | 0.85 |
| text-embedding-3-small | 0.78 | 0.74 | 0.89 |
| nomic-embed-text-v1.5 | 0.75 | 0.71 | 0.87 |

### Latency (p95)
| Model | Embed Single Query | Embed 100 Chunks | Vector Search (50K) |
|-------|-------------------|-------------------|---------------------|
| all-MiniLM-L6-v2 | 8ms | 120ms | 15ms |
| text-embedding-3-small | 45ms (API) | 2100ms (API) | 25ms |
| nomic-embed-text-v1.5 | 12ms | 180ms | 20ms |

### Cost Analysis (Monthly, 1M queries)
| Model | Embedding Cost | Infrastructure | Total |
|-------|---------------|----------------|-------|
| all-MiniLM-L6-v2 | $0 (local) | $200/mo (GPU) | $200/mo |
| text-embedding-3-small | $500/mo (API) | $100/mo | $600/mo |
| nomic-embed-text-v1.5 | $0 (local) | $250/mo (GPU) | $250/mo |

## Hybrid Search Impact
When combining with BM25 using Reciprocal Rank Fusion (k=60):
- all-MiniLM-L6-v2 + BM25: NDCG@10 = **0.81** (+12.5% vs embedding alone)
- text-embedding-3-small + BM25: NDCG@10 = **0.84** (+7.7%)
- nomic-embed-text-v1.5 + BM25: NDCG@10 = **0.82** (+9.3%)

## Recommendation
**all-MiniLM-L6-v2** is the recommended model for initial deployment:
- Hybrid search closes the quality gap (0.81 vs 0.84 NDCG@10)
- 5.6x faster query embedding than the API-based alternative
- 3x cheaper monthly cost
- No external API dependency (important for enterprise data privacy)

For enterprise tier with stricter quality requirements, consider upgrading to nomic-embed-text-v1.5 which offers a better quality/cost tradeoff than OpenAI.

## Next Steps
- Integrate all-MiniLM-L6-v2 into the search pipeline
- A/B test hybrid search vs current keyword-only search in production
- Monitor NDCG@10 and user satisfaction metrics post-launch
