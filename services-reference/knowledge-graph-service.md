---
confluence_id: "753832"
title: "knowledge-graph-service"
---

# knowledge-graph-service

**Layer:** 1 (Substrate) · **Port:** 8003 · **Status:** **Hollow today — R3.5 step 1 rebuilds it real.** Shipped as a stub: a `GraphNodeService` class is defined *inside* a route file (`api/v1/endpoints/graphs.py`) and ingestion is not real. R3.5 builds the genuine recipe/primitive/unified-graph ingestion per ADR-022, end-to-end.

## Honest current reality

R3 marked this service "done" but it is **hollow**. The write side does not really ingest: there is a `GraphNodeService` defined inside the `graphs.py` endpoint module (a §21 violation — a non-`BaseModel` class living in `routes/`), and the multi-modal pipelines described below do not exist as working code. Real graph-building logic still sits, undeleted, in the legacy `knowledge-graph-builder` and in `oraclous-backend/oraclous-core-service` (~6,300 LOC of dead-but-real logic across the R2/R3 services). This page describes the **R3.5 target**, not what runs today.

R3.5 makes `knowledge-graph-service` the **first** service rebuilt (graph-first per-service order, ORAA-4 §R3.5). It is rebuilt REAL and signed off by Reza before the dependent [knowledge-retriever-service](knowledge-retriever-service.md) starts.

## Purpose (R3.5 target)

`knowledge-graph-service` is the substrate's **write side**. It owns ingestion — turning raw inputs into graph nodes and relationships — plus schema management, analytics, and provenance writes. The read side is [knowledge-retriever-service](knowledge-retriever-service.md). After R3.5 step 3, **organisation/membership management leaves this service** and moves to [identity-org-service](identity-org-service.md); the graph keeps only the ReBAC *edges*, not the org domain logic.

## Ingestion model (ADR-022)

Ingestion is **recipe-driven**, not per-source code. A concern-driven **recipe** is a reusable spec that turns any source into the **unified graph** via a small set of **primitives**, so a new source type does not require a new code path. The R3.5 ingestion surface covers, per ADR-022 and the legacy spec pinned to `develop @ 84152635`:

* **text**
* **PDF**
* **DOCX**
* **Markdown (MD)**
* **CSV**
* **JSON**
* **code** (via the code-parser path)
* **temporal** (bitemporal facts feeding point-in-time reads on the retriever)

Each modality is stored as nodes in one unified graph with modality-appropriate indexes; the recipe expresses *what to extract and how to relate it*, the primitives do the writing.

## Responsibilities (R3.5 target)

* Recipe + primitive ingestion across text / PDF / DOCX / MD / CSV / JSON / code / temporal into the unified graph (ADR-022)
* Schema management (`schema_manager.py`, schema endpoints)
* ReBAC graph maintenance: workspace hierarchy, cross-workspace relationships, agent scopes, delegations, and the membership/subgraph-grant **edges** written on behalf of [identity-org-service](identity-org-service.md)
* Multi-tenant write wrappers enforcing `organization_id` and `graph_id`
* Analytics: community detection, centrality, graph-shape characterisation (write side runs detection; read APIs live in the retriever)
* Provenance writes (universal sink for every action)
* Background job orchestration for long-running ingestion pipelines

## What does NOT live here

* **Retrieval queries** — [knowledge-retriever-service](knowledge-retriever-service.md)
* **Organisation / member / invitation management** — moves to [identity-org-service](identity-org-service.md) in R3.5 step 3 (orgs leave the graph service)
* **Tool / capability execution** — [capability-registry-service](capability-registry-service.md)
* **Chat persistence and public chat APIs** — [application-gateway-service](application-gateway-service.md) when it is built last

## Security commitments

* `organization_id` filter mandatory on every write path
* Cypher injection prevention via parameterised queries (the `test_cypher_injection.py` suite is preserved)
* Per-graph indexes and `graph_id`-scoped writes; cross-tenant writes structurally impossible
* Decompression-bomb protection via a `MAX_DECOMPRESSED_BYTES` cap on uploaded archives

## Architecture conformance (ORAA-4 §21)

The `GraphNodeService`-in-a-route violation is fixed by the rebuild: package root `services/knowledge-graph-service/src/oraclous_knowledge_graph_service/` with `routes/` (parse → one service call → HTTP map only), all ingestion/recipe logic in `services/`, the only Neo4j/Postgres/Redis access in `repositories/(+models.py)`, Pydantic-only `schema/`, `core/{config,dependencies,lifespan}.py`, `migrations/`. No business logic in handlers; no non-`BaseModel` classes or DB drivers in `routes/`.

## Definition of Done (ORAA-4 §22)

Done only when all 8 gates pass — and "merged PR + green stub-tests" satisfies none of them. Required: structurally conformant; not hollow (`check_no_stubs` zero findings + `claimed_done` flipped in `service_status.yaml`); runs (`docker compose up` healthy, `GET /health` 200); real endpoints (integration ingest of each modality vs real Neo4j via testcontainers, no stub/501); end-to-end smoke (`tests/smoke/smoke.sh` ingesting a real file of each kind, run as the docker-required `r3_5_gate` job); Reza personally tests and signs off (`needs-human` held until accepted). Per §23: one service, ≤6 coarse vertical slices, each cutting all layers and ending in a passing smoke.

## Related

* ADR-022 — recipe / primitive / unified-graph ingestion model (the R3.5 spec)
* ADR-001 — Four-Layer Architecture
* ADR-006 — Organisation as Outermost Tenancy Unit
* [knowledge-retriever-service](knowledge-retriever-service.md) — the read side (R3.5 step 2)
* [identity-org-service](identity-org-service.md) — takes over org management (R3.5 step 3)
* Section 3 — Substrate layer
