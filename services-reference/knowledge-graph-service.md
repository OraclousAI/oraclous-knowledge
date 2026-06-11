---
confluence_id: "753832"
title: "knowledge-graph-service"
---

# knowledge-graph-service

**Layer:** 1 (Substrate) · **Port:** 8003 · **Status:** **Real — R3.5-complete, §22-signed-off** (Reza ran `smoke.sh`). Rebuilt as service #1 (graph-first): real graph CRUD plus recipe-driven ingestion (text / document / structured / code) into the unified graph (ADR-022), with a real Cypher write chain through `OrganisationScopedKGWriter`. The `GraphNodeService`-in-a-route §21 violation is gone.

## What it is now

R3.5 rebuilt this real, end-to-end, against real Neo4j + Postgres. The write side genuinely ingests: `routes/` (`health_routes`, `graph_routes`, `ingest_routes`, `recipe_routes`, `ontology_routes`, `internal_routes`) → `services/` (real `graph_service`, `ingestion_service`, `structured_ingestion_service`, `code_ingestion_service`, recipe `engine`, `recipe_service`, `ontology_service`, `job_service`, plus `chunker`/`embedder`/`extractors`/`parser`/`primitives`) → repositories → substrate. The legacy port-sources (`knowledge-graph-builder`, `oraclous-core-service`) are deleted. The org/member/role/invitation domain **left this service** (the ADR-017 boundary fix) and lives in [auth-service](auth-service.md); the graph keeps only the ReBAC *edges*.

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

## Recipe rule shapes (format 0.2 — enriched by epic #269)

A recipe is data, not code (ADR-022): a `format 0.2` JSON document validated against `recipe.schema.json` and *interpreted* by the engine. Beyond the Slice-A baseline (deterministic node/edge `mappings` with nested-object reads and foreign-key edges), the **#269 recipe-enrichment epic** added five rule shapes that turn structured records into a richer, interconnected graph. All are deterministic-first and **fail-soft** (an LLM/embedder being unavailable skips only that pass, never the structured projection). The shapes, with the slice PR that landed each:

| Shape | Where in the recipe | What it does | Slice / PR |
| --- | --- | --- | --- |
| **`transform`** | `mappings[].identity.transform` (and `properties[].transform`) | A named deterministic value transform applied to a read value before it is used as identity/property. Registry: **`host`** (URL → bare hostname, `www.` stripped), **`lower`**, **`strip_www`**, **`canonical`** (entity-name → canonical key: casefold + hostname-stem + legal-suffix strip, so `Eurail B.V.` / `eurail.com` / `Eurail Group` → `eurail`). An unknown transform is a validation error. | #270 |
| **`from_each` + `edge_to_each`** | on a `project_to: node` rule | List fan-out: `from_each` names a **list-valued** field; each element becomes one node whose identity *is* the element value (MERGE-shared across records). `edge_to_each` pairs it with an edge `(record's primary node)-[type]->(each element node)`. | #270 |
| **`extractions`** | top-level `extractions[]` | **Hybrid free-text-on-a-field**: after the deterministic projection, the LLM entity extractor runs over a **prose field** of each record under an inline `ontology` (entity + relationship types, mode `strict`/`coerce`/`open`), mining named entities and MERGE-ing a `link` edge from the record's primary node to each. Entities dedup across records, so records interconnect by shared entities. Fail-soft when `KGS_EXTRACTOR=null`. | #271 |
| **`similarities`** | top-level `similarities[]` | **Content similarity**: embed a designated prose field per record, run a cosine kNN (`top_k`, `min_score`), and MERGE an `edge_type` (default `SIMILAR_TO`) edge carrying a **`score`** between records whose text is close — one edge per unordered pair. So evidence that *says* similar things connects even with no shared source/entity. | #274 |
| **`resolution`** | `extractions[].resolution` | **Resolve-on-write canonicalization** (entity resolution): `canonical: true` keys each extracted entity by its canonical key, so surface variants MERGE onto **one** node (carrying `name` = canonical key, `canonical_name` = display form, `aliases` = the original surface forms) rather than separate nodes. A conservative semantic pass then folds near-duplicate canonical names (cosine ≥ `merge_threshold`, default 0.92) and flags the ambiguous band `[candidate_threshold, merge_threshold)` (default 0.85–0.92) with a **`SAME_AS_CANDIDATE {score}`** review edge — never auto-merged. Fail-soft. | #275 |

A performance pass (#272) runs the extraction concurrently across chunks. The canonical authored example that exercises all five shapes is the evidence recipe in `services/recipes/templates.py::build_evidence_recipe` (the Postman collection ships a runnable copy). The graph these shapes write is described next.

## Graph structure (node labels, edge types, properties)

The #269 enrichment projects, beyond the unified `Source → Container → Entity` baseline (ADR-022 §3), the following recipe-driven shapes. Domain labels and edge types are **recipe-supplied** (validated safe-identifiers), not hard-coded; the set below is what the enriched evidence recipe writes and the de-facto schema the retriever/FE read:

* **Node labels:** `Publisher` (host-keyed from a source URL via `transform: host`), `Tag` (fanned from a list field), and the extraction ontology's entity labels — `Person`, `Organization`, `Product`, `Place` (alongside the baseline `Evidence`, `ClaimSource`, `Conflict`).
* **Edge types:**
  * `PUBLISHED_BY` — `ClaimSource-[:PUBLISHED_BY]->Publisher` (same-record identity; collapses every article URL on a domain to one Publisher).
  * `HAS_DIMENSION` — `Evidence-[:HAS_DIMENSION]->Tag` (one per fanned-out list element).
  * `MENTIONS` — `Evidence-[:MENTIONS]->`entity (the extraction `link` edge to each mined entity).
  * `OPERATES`, `LOCATED_IN` — relationship types from the inline extraction ontology, between mined entities (e.g. `Organization-[:OPERATES]->Product`).
  * `SIMILAR_TO {score}` — between similar records' nodes (content-similarity pass; carries a cosine `score`).
  * `SAME_AS_CANDIDATE {score}` — between two canonical entity nodes in the ambiguous resolution band, MERGEd for human review (carries a cosine `score`); **not** an assertion of identity.
* **Entity properties** (on a resolved entity node): `aliases` (the set of original surface forms seen), `canonical_name` (a chosen display form), with `name` carrying the canonical key.
* **Edge `score`:** a rounded cosine similarity, present on **`SIMILAR_TO`** and **`SAME_AS_CANDIDATE`** edges.

The cross-repo summary of these labels/edges/properties is mirrored in [Interface Contracts §GRAPH](../flows/interface-contracts.md#graph--enriched-graph-schema-269).

## Responsibilities

* Recipe + primitive ingestion across text / PDF / DOCX / MD / CSV / JSON / code into the unified graph (ADR-022), with temporal write-side stamps
* Ontology enforcement (`ontology_service`, ontology endpoints) and internal schema extraction (`internal_routes`, `GET /internal/v1/schema/{graph_id}`)
* Reserves ReBAC label namespaces (`__Rebac__`) against accidental ingestion overwrite; **actual ReBAC-edge writes (workspace hierarchy, cross-workspace relationships, agent scopes, delegations, membership/subgraph-grant edges) are not implemented in this build**
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
* Decompression-bomb protection on zip archives in code ingestion via a per-file size cap (`_MAX_FILE_BYTES`, 2 MB) and a file-count cap (`_MAX_FILES`, 5000) — `code_ingestion_service.py` (there is no aggregate total-decompressed cap today)

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
