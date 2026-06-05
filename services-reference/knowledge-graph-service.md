---
confluence_id: "753832"
title: "knowledge-graph-service"
---

# knowledge-graph-service

**Layer:** 1 (Substrate) · **Port:** 8003 · **Status:** **Real — R3.5-complete, §22-signed-off** (Reza ran `smoke.sh`). Rebuilt as service #1 (graph-first): real graph CRUD plus recipe-driven ingestion (text / document / structured / code) into the unified graph (ADR-022), with a real Cypher write chain through `OrganisationScopedKGWriter`. The `GraphNodeService`-in-a-route §21 violation is gone.

## What it is now

R3.5 rebuilt this real, end-to-end, against real Neo4j + Postgres. The write side genuinely ingests: `routes/` (`graph_routes`, `ingest_routes`, `recipe_routes`, `ontology_routes`, `internal_routes`) → `services/` (real `graph_service`, `ingestion_service`, `structured_ingestion_service`, `code_ingestion_service`, recipe `engine`, `recipe_service`, `ontology_service`, `job_service`, plus `chunker`/`embedder`/`extractors`/`parser`/`primitives`) → repositories → substrate. The legacy port-sources (`knowledge-graph-builder`, `oraclous-core-service`) are deleted. The org/member/role/invitation domain **left this service** (the ADR-017 boundary fix) and lives in [auth-service](auth-service.md); the graph keeps only the ReBAC *edges*.

## Purpose

`knowledge-graph-service` is the substrate's **write side**: it turns raw inputs into graph nodes and relationships, plus schema management, ontology enforcement, and provenance writes. The read side is [knowledge-retriever-service](knowledge-retriever-service.md). Heavier graph analytics (community detection, centrality) are **not in this build** — a later concern.

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

## Responsibilities

* Recipe + primitive ingestion across text / PDF / DOCX / MD / CSV / JSON / code into the unified graph (ADR-022), with temporal write-side stamps
* Ontology enforcement (`ontology_service`, ontology endpoints) and internal schema extraction (`internal_routes`, `/internal/v1/schema`)
* ReBAC graph maintenance: workspace hierarchy, cross-workspace relationships, agent scopes, delegations, and the membership/subgraph-grant **edges** written on behalf of [auth-service](auth-service.md)
* Multi-tenant write wrappers enforcing `organisation_id` and `graph_id`
* Provenance writes
* Background job orchestration for long-running ingestion pipelines (`job_service`)
* **Deferred (not in this build):** graph analytics — community detection, centrality, graph-shape characterisation

## What does NOT live here

* **Retrieval queries** — [knowledge-retriever-service](knowledge-retriever-service.md)
* **Organisation / member / invitation management** — [auth-service](auth-service.md) (orgs left the graph service; the ADR-017 boundary fix)
* **Tool / capability execution** — [capability-registry-service](capability-registry-service.md)
* **Retrieval / chat** — [knowledge-retriever-service](knowledge-retriever-service.md) (read side)

## Security commitments

* `organization_id` filter mandatory on every write path
* Cypher injection prevention via parameterised queries (the `test_cypher_injection.py` suite is preserved)
* Per-graph indexes and `graph_id`-scoped writes; cross-tenant writes structurally impossible
* Decompression-bomb protection via a `MAX_DECOMPRESSED_BYTES` cap on uploaded archives

## Architecture conformance (ORAA-4 §21)

The `GraphNodeService`-in-a-route violation was fixed by the rebuild: package root `services/knowledge-graph-service/src/oraclous_knowledge_graph_service/` with `routes/` (parse → one service call → HTTP map only), all ingestion/recipe logic in `services/`, pure entities in `domain/` (`graph`, `job`, `ontology`, `structural`), the only Neo4j/Postgres/Redis access in `repositories/(+models.py)`, Pydantic-only `schema/`, `core/{config,dependencies,lifespan}.py`, `migrations/`. `structure_enforced: true`, `claimed_done: true` — the structure and no-stub checkers fail CI on any regression.

## Definition of Done (ORAA-4 §22)

Done only when all 8 gates pass — and "merged PR + green stub-tests" satisfies none of them. Required: structurally conformant; not hollow (`check_no_stubs` zero findings + `claimed_done` flipped in `service_status.yaml`); runs (`docker compose up` healthy, `GET /health` 200); real endpoints (integration ingest of each modality vs real Neo4j via testcontainers, no stub/501); end-to-end smoke (`tests/smoke/smoke.sh` ingesting a real file of each kind, run as the docker-required `r3_5_gate` job); Reza personally tests and signs off (`needs-human` held until accepted). Per §23: one service, ≤6 coarse vertical slices, each cutting all layers and ending in a passing smoke.

## Related

* ADR-022 — recipe / primitive / unified-graph ingestion model (the R3.5 spec)
* ADR-001 — Four-Layer Architecture
* ADR-006 — Organisation as Outermost Tenancy Unit
* [knowledge-retriever-service](knowledge-retriever-service.md) — the read side
* [auth-service](auth-service.md) — owns org/member/invitation management (the ADR-017 boundary fix)
* Section 3 — Substrate layer
