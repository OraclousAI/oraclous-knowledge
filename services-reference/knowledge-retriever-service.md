# knowledge-retriever-service

**Layer:** 1 (Substrate) · **Port:** 8006 · **Status:** NEW in Phase 3

## Purpose

`knowledge-retriever-service` is the substrate's read side. It exposes modality-appropriate retrieval shapes that all return the same `NodeResult` envelope.

## Responsibilities

- Semantic search via vector indexes
- Full-text search via Lucene-style indexes
- Hybrid search (vector + full-text reranking)
- Graph traversal queries (Cypher, parameterised, ReBAC-bounded)
- Temporal slice queries
- Federation traversal across workspaces under ReBAC (read mechanics)

## Result envelope

Every retrieval returns `NodeResult` with: node identifier, modality, content, provenance, retrieval-method metadata.
