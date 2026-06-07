---
confluence_id: "622776"
title: "knowledge-retriever-service"
---

# knowledge-retriever-service

**Layer:** 1 (Substrate) · **Port:** 8004 · **Status:** **Real — R3.5-complete, §22-signed-off.** Rebuilt as service #2 (read side): real org-scoped **semantic / full-text / hybrid / graph** retrieval over what the graph service ingested, returning a uniform `NodeResult` envelope. **Chat and a dedicated query-cache are not in this build** (deferred); temporal point-in-time reads ARE shipped (`GET /v1/graph/{graph_id}/temporal`).

## What it is now

R3.5 rebuilt the read side real, end-to-end, after [knowledge-graph-service](knowledge-graph-service.md) (its data source) was signed off. The retrieval surface genuinely queries: `routes/` (`search_routes`, `graph_routes`) → `services/` (real `retrieval_service` + `embedder`) → a read-side Neo4j connection. Smoke proves `/v1/search/{semantic,fulltext,hybrid}` and the graph endpoints (`/v1/graph/{id}/subgraph`, `/neighbors/{node_id}`, `/temporal`) against a graph populated by the rebuilt write side. The legacy `knowledge-graph-builder` retriever paths are deleted.

## Purpose

`knowledge-retriever-service` is the substrate's **read side**. It exposes modality-appropriate retrieval shapes that all return one uniform `NodeResult` envelope, so agents and harnesses consume results without reasoning about which modality powered the match.

## Responsibilities

* **Semantic** search (text, document, code) via vector indexes
* **Full-text** search via Lucene-style indexes
* **Hybrid** search (vector + full-text reranking)
* **Graph** traversal queries (Cypher, parameterised, org-scoped): `GET /v1/graph/{graph_id}/subgraph` (bounded `{nodes,edges}` visualisation slice), `GET /v1/graph/{graph_id}/neighbors/{node_id}` (1-hop neighbourhood)
* **Temporal** point-in-time reads — entities whose validity window covers `as_of` (`GET /v1/graph/{graph_id}/temporal`)
* **Deferred (not in this build):** **chat** (the conversational read surface); a dedicated query-cache service

## Result envelope

Every retrieval returns `NodeResult` with consistent fields: node identifier, modality, content, provenance (source, ingestion time, ingestion source), and retrieval-method metadata (which index was hit, score, what was reranked). A caller cannot tell a semantic match from a graph-traversal match by its shape.

## Dependencies

* **Upstream:** Neo4j (read connection, separate role from the graph service's write connection). Identity is resolved **locally** — the [application-gateway-service](application-gateway-service.md) trusted-gateway path (ADR-018: trust `X-Principal-*`/`X-Organisation-Id` + `X-Internal-Key`), a dev bearer, or a shared-secret JWT decode in `jwt` mode — not via an auth-service ReBAC call
* **Downstream consumers:** harness/agent flows (most retrieval volume), and — once it fronts this service — [application-gateway-service](application-gateway-service.md). Until then, consumers reach this service **directly by host IP:port** (legacy parity; legacy had no gateway).

## Security commitments

* Every retrieval is **organisation-scoped**: identity is resolved (gateway headers / dev bearer / JWT), a single `organisation_id` is bound per request via the fail-closed governance seam (`enforced_organisation_id`), and every Cypher read filters by `organisation_id` + `graph_id` as bound parameters
* `graph_id` is taken from the request and scoped to the bound org; there is no per-actor ReBAC allow-set, `_effective_graph_ids` resolution, query-cache, or `cross_workspace` declaration in this build (those remain forward design notes)

## Architecture conformance (ORAA-4 §21)

Rebuilt to the layered shape: package root `services/knowledge-retriever-service/src/oraclous_knowledge_retriever_service/` with `routes/` (parse → one service call → HTTP map), all retrieval logic in `services/`, the only Neo4j/Redis access in `repositories/(+models.py)`, Pydantic-only `schema/`, `core/{config,dependencies,lifespan}.py`. No logic in handlers; no non-`BaseModel` classes or DB drivers in `routes/`.

## Definition of Done (ORAA-4 §22) — MET

All 8 gates passed: structurally conformant; not hollow (`check_no_stubs` zero findings, `claimed_done: true`); runs (`docker compose up` healthy, `GET /health` 200); real endpoints (integration: each retrieval mode vs a real graph populated by the rebuilt graph service, via testcontainers, no stub/501); end-to-end smoke (`tests/smoke/smoke.sh` ingest-then-retrieve across modes, `r3_5_gate` job); Reza signed off.

## Related

* ADR-022 — recipe / primitive / unified-graph model (defines what is retrieved)
* ADR-001 — Four-Layer Architecture
* [knowledge-graph-service](knowledge-graph-service.md) — the write side / data source (built first)
* Section 3 — Substrate layer (multi-modal commitments)
