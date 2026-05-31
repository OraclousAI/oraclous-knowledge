---
confluence_id: "753832"
title: "knowledge-graph-service"
---

# knowledge-graph-service

**Layer:** 1 (Substrate) · **Port:** 8003 · **Status:** Renamed from `knowledge-graph-builder` in Phase 3; ingest-only after retriever extraction

## Purpose

`knowledge-graph-service` is the substrate's write side. It owns ingestion (turning raw inputs into graph nodes and relationships), schema management, analytics, and ReBAC graph maintenance. The read side lives in `knowledge-retriever-service` (Phase 3 split).

## Responsibilities

* Multi-modal ingestion: text, documents (PDF, DOCX), structured data (CSV, JSON, relational), code, temporal data
* ReBAC graph maintenance (workspace hierarchy, cross-workspace relationships, agent scopes, delegations)
* Schema management (`schema_manager.py`, schema endpoints)
* Multi-tenant component wrappers for write paths (`MultiTenantVectorRetriever` etc., enforcing `organization_id` and `graph_id`)
* Analytics: community detection, centrality, graph-shape characterisation (write side runs detection; read APIs live in the retriever)
* Provenance writes (universal sink for every action in the platform)
* Code ingestion via `code_parser_service.py`
* Background job orchestration (`background_jobs.py`) for long-running ingestion pipelines

## Dependencies

* **Upstream:** Neo4j (graph storage), Postgres (chat persistence and other relational data — moves to gateway in Phase 6), Redis (ingestion job queues)
* **Downstream consumers:** all services that depend on the knowledge graph (which is most of them)

## What does NOT live here

* **Retrieval queries** — moved to `knowledge-retriever-service` in Phase 3
* **AgentExecutor and toolkit** — moved to `harness-runtime-service` in Phase 4
* **Chat persistence and chat APIs** — moved to `application-gateway-service` in Phase 6
* **Published agents and integration keys** — moved to `application-gateway-service` in Phase 6

## Multi-modal commitments

Per Section 3, every modality is stored as nodes in the knowledge graph with modality-appropriate indexes. The write side adds modality-specific ingestion pipelines; the substrate stays uniform.

v1 modalities: text, documents, structured, code, temporal. Future modalities (images, audio, video, design, 3D) are additive — Section 9 documents them as deferred to v2 with explicit when-in-scope criteria.

## Security commitments

* All multi-tenant isolation defences preserved through Phase 3 (parameterised Cypher with `graph_id`, RLS where applicable, per-graph indexes)
* `organization_id` filter is mandatory on every write path from Phase 0.5 forward
* Cypher injection prevention through parameterised queries (the existing `test_cypher_injection.py` suite is preserved)
* Decompression bomb protection via `MAX_DECOMPRESSED_BYTES` cap

## Migrations

**Organisation backfill (A1 cutover, ORA-24).** A one-time, idempotent migration scopes a pre-A1 deployment's substrate data to an organisation — adding and backfilling `organisation_id` across the Postgres tenant tables, the Neo4j org-scoped nodes/relationships, and the Redis query cache (a cold-start flush of legacy un-scoped `qcache:` keys). Each store has a tested rollback that preserves data. Code lives in `oraclous_substrate.migrations.org_backfill`; the production run is gated on A2 (ORA-17) + A3 (ORA-18). Operator procedure: [Runbook — Organisation Backfill Migration (ORA-24)](https://oraclous.atlassian.net/wiki/spaces/OP/pages/2260996).

## Related

* ADR-001 — Four-Layer Architecture
* ADR-006 — Organisation as Outermost Tenancy Unit
* Section 3 — Substrate layer
* Section 8 — Phase 3 (knowledge graph decomposition)
* Runbook — Organisation Backfill Migration (ORA-24)
