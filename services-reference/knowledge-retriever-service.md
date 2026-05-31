---
source_page_id: 622776
title: "knowledge-retriever-service"
---

# knowledge-retriever-service

**Layer:** 1 (Substrate) · **Port:** 8006 · **Status:** NEW in Phase 3 (extracted from `knowledge-graph-builder`)

## Purpose

`knowledge-retriever-service` is the substrate's read side. It exposes modality-appropriate retrieval shapes that all return the same `NodeResult` envelope, so agents and harnesses consume retrieved data uniformly without reasoning about which modality powered the retrieval.

Splitting from `knowledge-graph-service` is justified by three different concerns (Section 8): different access patterns (read-heavy, latency-critical), different multi-modal evolution paths, different governance and audit needs.

## Responsibilities

* Semantic search (text, document, code) via vector indexes
* Full-text search (text, document, code) via Lucene-style indexes
* Hybrid search (vector + full-text reranking)
* Graph traversal queries (Cypher, parameterised, ReBAC-bounded)
* Temporal slice queries (bitemporal data, point-in-time reads)
* Federation traversal across workspaces under ReBAC (Phase 5 brings the runtime side; the retriever owns the read mechanics)
* Future modalities (perceptual match, acoustic match, geometric query — additive, Section 9)

## Result envelope

Every retrieval returns `NodeResult` with consistent fields: node identifier, modality, content, provenance (source, ingestion time, ingestion source), retrieval-method metadata (which index was hit, what score, what was reranked). Agents do not need to know whether they got a semantic match or a graph-traversal match.

## Dependencies

* **Upstream:** Neo4j (read connection, separate role from the builder's write connection), Redis (query cache with `organization_id:graph_id:` prefixed keys), `auth-service` (for ReBAC checks on retrieval)
* **Downstream consumers:** `harness-runtime-service` (most retrieval volume), `application-gateway-service` (chat retrieval), customer integrations via MCP server exposure

## Security commitments

* Every retrieval is ReBAC-gated; an actor only sees what their effective scope allows
* `_effective_graph_ids` resolution per turn (existing pattern preserved); every retrieval scopes to this set
* Cache keys include `organization_id` and `graph_id` prefixes; cross-tenant cache hits are structurally impossible
* Cross-workspace retrieval requires explicit OHM `cross_workspace` declarations (Section 6.5 Threat 9.1)

## Migration path (Phase 3)

The retriever code already exists in `knowledge-graph-builder`. Migration is **extract, not rebuild**: move `retriever_service.py`, `retriever_factory.py`, retriever-side multi-tenant components, the full-text index service, the query cache, and chat-engine retrieval paths into a new deployment unit. The new service shares the Neo4j database with the builder but runs as a separate process with its own scaling profile.

## Related

* ADR-001 — Four-Layer Architecture
* Section 3 — Substrate layer (multi-modal commitments)
* Section 8 — Phase 3 + the graph retriever decision
* Section 9 — Future modalities (deferred to v2)
