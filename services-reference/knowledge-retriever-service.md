---
confluence_id: "622776"
title: "knowledge-retriever-service"
---

# knowledge-retriever-service

**Layer:** 1 (Substrate) · **Port:** 8006 · **Status:** **Hollow today — R3.5 step 2 rebuilds it real.** Shipped as a stub (retriever / fulltext / similarity / query-cache services exist as shells; search routes return stub or `501`). R3.5 builds real semantic / full-text / hybrid / graph / temporal retrieval **plus chat**, end-to-end, after the graph service is signed off.

## Honest current reality

R3 marked this "done" but the retrieval surface is **hollow**: `retriever_service.py`, `retriever_factory.py`, `similarity_service.py`, `fulltext_index_service.py`, `query_cache_service.py`, and the `routers/search.py` endpoints are shells that don't perform real retrieval. The genuine retrieval logic still lives undeleted in the legacy `knowledge-graph-builder` retriever paths. This page describes the **R3.5 target**.

R3.5 rebuilds the retriever as **step 2**, after [knowledge-graph-service](knowledge-graph-service.md) (its data source) is rebuilt and Reza-signed-off. It is built REAL and signed off before the dependent [identity-org-service](identity-org-service.md) starts.

## Purpose (R3.5 target)

`knowledge-retriever-service` is the substrate's **read side**. It exposes modality-appropriate retrieval shapes that all return one uniform `NodeResult` envelope, so agents and harnesses consume results without reasoning about which modality powered the match. It also serves **chat** retrieval.

## Responsibilities (R3.5 target)

* **Semantic** search (text, document, code) via vector indexes
* **Full-text** search via Lucene-style indexes
* **Hybrid** search (vector + full-text reranking)
* **Graph** traversal queries (Cypher, parameterised, ReBAC-bounded)
* **Temporal** slice queries (bitemporal data, point-in-time reads)
* **Chat** — the conversational read surface over the retrieved graph
* Query cache with `organization_id:graph_id:`-prefixed keys

## Result envelope

Every retrieval returns `NodeResult` with consistent fields: node identifier, modality, content, provenance (source, ingestion time, ingestion source), and retrieval-method metadata (which index was hit, score, what was reranked). A caller cannot tell a semantic match from a graph-traversal match by its shape.

## Dependencies

* **Upstream:** Neo4j (read connection, separate role from the graph service's write connection), Redis (query cache), [auth-service](auth-service.md) + [identity-org-service](identity-org-service.md) (ReBAC checks on retrieval — machine and human principals respectively)
* **Downstream consumers:** harness/agent flows (most retrieval volume), chat clients, and — once it exists — [application-gateway-service](application-gateway-service.md). Until the gateway is built, consumers reach this service **directly by host IP:port** (legacy parity; legacy had no gateway).

## Security commitments

* Every retrieval is ReBAC-gated; an actor sees only what their effective scope allows
* `_effective_graph_ids` resolution per turn; every retrieval scopes to that set
* Cache keys include `organization_id` and `graph_id` prefixes; cross-tenant cache hits are structurally impossible
* Cross-workspace retrieval requires explicit `cross_workspace` declarations (Section 6.5 Threat 9.1)

## Architecture conformance (ORAA-4 §21)

Rebuilt to the layered shape: package root `services/knowledge-retriever-service/src/oraclous_knowledge_retriever_service/` with `routes/` (parse → one service call → HTTP map), all retrieval + chat logic in `services/`, the only Neo4j/Redis access in `repositories/(+models.py)`, Pydantic-only `schema/`, `core/{config,dependencies,lifespan}.py`. No logic in handlers; no non-`BaseModel` classes or DB drivers in `routes/`.

## Definition of Done (ORAA-4 §22)

Done only when all 8 gates pass: structurally conformant; not hollow (`check_no_stubs` zero findings + `claimed_done` flipped in `service_status.yaml`); runs (`docker compose up` healthy, `GET /health` 200); real endpoints (integration: each retrieval mode + chat vs a real graph populated by the rebuilt graph service, via testcontainers, no stub/501); end-to-end smoke (`tests/smoke/smoke.sh` ingest-then-retrieve across modes, run as the docker-required `r3_5_gate` job); Reza personally tests and signs off (`needs-human` held until accepted). Per §23: one service, ≤6 coarse vertical slices.

## Related

* ADR-022 — recipe / primitive / unified-graph model (defines what is retrieved)
* ADR-001 — Four-Layer Architecture
* [knowledge-graph-service](knowledge-graph-service.md) — the write side / data source (R3.5 step 1, built first)
* Section 3 — Substrate layer (multi-modal commitments)
