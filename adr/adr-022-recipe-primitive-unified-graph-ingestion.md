---
confluence_id: TBD
title: "ADR-022 — Concern-Driven Ingestion: Recipes, Primitives, and the Unified Source→Structure→Entity Graph Model"
---

# ADR-022 — Concern-Driven Ingestion: Recipes, Primitives, and the Unified Source→Structure→Entity Graph Model

## Status

| Field | Value |
|---|---|
| Status | Accepted (ported from legacy `develop@84152635`; binding for R3.5 knowledge-graph-service) |
| Date | 2026-06-04 (port); original SA review 2026-05-19 (legacy STORY-034 / TASK-220/221/237) |
| Approved by | tech-lead (Reza Jahankohan) |
| Driving artifact | R3.5 release; ORAA-4 §23 (spec pinned to legacy `develop@84152635`) |
| Binding implementation (the spec) | legacy `knowledge-graph-builder/{docs/unified-graph-model.md, docs/recipe-spec.md, app/recipes/*, app/cypher/migrations/2026-05-19_unified_graph_model.cypher}` at `develop@84152635de05c105765cfe6b631bb5ba81f2f4aa` — read via `git show develop:<path>`, never write `legacy-reference` |

## Context

The legacy knowledge graph had **four divergent ingestion paths** (`/ingest`, `/ingest/document`, `/ingest-records`, `/ingest-incremental`), each with its own provenance stamping and node shapes: files became `:Document` nodes, databases became `:Connector` nodes whose tables were never modeled, and "a new data concern" meant writing new platform code. This is exactly the kind of per-shape sprawl that produced the hollow, inconsistent services R3.5 exists to fix.

The legacy `develop` branch resolved this (STORY-034) into a single concern-driven model. Because **ORAA-4 §23 pins the R3.5 spec to `develop@84152635`**, this model — not the older four-path one — is the binding specification for the R3.5 `knowledge-graph-service`. This ADR records the decision so the new service is built to it, not re-derived or assumed.

## Decision

### 1. Ingestion is concern-driven via agent-authored **recipes** (data, not code)

A **recipe** is a declarative JSON document — validated by a JSON Schema, **interpreted** by a recipe execution engine, **never executed as code**. It specifies how a given *data shape*, under a given *concern*, projects into graph nodes and edges.

- A recipe is **authored once, at design time**, by the `data-specialist` agent reasoning over a *sample* of a source plus a natural-language concern. Lifecycle: `draft → human review → promote (status="promoted", version bumped) → execute`. Only a promoted recipe runs in production; drafts are reviewable artifacts.
- A recipe **executes mechanically, at run time**, over the full dataset — **no LLM, no agent, deterministic and idempotent**. (The one free-text exception: a recipe rule of the "free-text extraction" type invokes the LLM extractor for unstructured prose; per the SA review's "position B".)
- **A new concern is a new recipe; no platform code is written per concern.**

### 2. **Primitives** — deterministic, per-data-type decomposition

Before a recipe runs, the raw source is decomposed by a **primitive**: a deterministic, dependency-light decomposer per data type (`document`, `csv`, `json`, `markdown`, `code`, `relational`) implementing a `Primitive` Protocol that yields a `StructuralRepresentation` — a flat list of `StructuralUnit`s. Primitives are pure and key-free (no LLM, no embeddings). This is what makes CSV / JSON / code / relational ingestion **fully testable with no external API key** (see the R3.5 knowledge-graph-service smoke).

### 3. The unified **Source → Container → Entity** graph model

Every data source — database, spreadsheet, document folder, code repo — turns into **one consistent kind of graph**. Three node families:

| Family | Labels | What it is |
|---|---|---|
| **Source** | `:Source:__KGBuilder__` | one per ingested data source |
| **Container** | `:Table`, `:Sheet`, `:File`, `:Chunk` (each `:__KGBuilder__`) | a grouping *inside* a source; a **fixed, platform-owned set** — recipes never invent these |
| **Entity** | `:__Entity__` + one recipe-supplied domain label (`:Employee`, `:Operator`, …) | a real thing; the domain type is a real Neo4j label, never a property |

**The core rule — one node per real thing.** A container gets its own node; the data *inside* a container does **not** get a second "structure" node if it is itself a real thing. A database row *is* the employee (`:Employee:__Entity__`, pointing back to its `:Table`) — there is no separate "row node". A code function *is* `:Function:__Entity__`, not a symbol-node-plus-entity-node. **Two nodes only when container and contents are genuinely different things** — e.g. a `:Chunk` of text vs. the entities *mentioned in* it. This avoids doubling node counts for the commonest data shapes.

- **Identity is decoupled from storage primary keys**: deterministic identity hashing (`fingerprint`), so re-ingest MERGEs idempotently.
- **Domain labels** are recipe-supplied and validated (safe-identifier + ADR-015 reserved-namespace; the container label set is fixed so recipes cannot collide with it).
- **Org-scoping (ADR-006/ADR-012):** every node/edge carries `organisation_id` (and `graph_id`), written through the substrate access seam — never trusting an inbound request field.

### 4. Recipe run is an async submit+status job (TASK-237)

`POST /graphs/{graph_id}/recipes/{recipe_id}/run` is an **async submit+status pair**: it creates a first-class `IngestionJob` row (`source_type="recipe"`), enqueues a Celery task, returns the job id, and the run is polled via the standard `GET /graphs/{id}/jobs/{job_id}`.

## Consequences

- The R3.5 `knowledge-graph-service` implements **one** ingestion pipeline (primitive → recipe engine → unified graph), not four — and the deterministic data types (CSV/JSON/code/relational) need no LLM, so they are smoke-testable key-free.
- A new data concern is an agent-authored recipe + human review, not a platform code change.
- The `data-specialist` agent (recipe authoring over a sample) is a required role for live ingestion; the engine itself is mechanical.
- **No backward compatibility** with the older four-path model — it is superseded; this is *the* model.
- Read-side (retrieval, point-in-time queries) lives in `knowledge-retriever-service`, not here.

## References

- [ADR-001 — Four-Layer Architecture](./adr-001-four-layer-architecture.md) · [ADR-016 — Canonical Service Architecture + Hardened DoD](./adr-016-canonical-service-architecture-and-hardened-definition-of-done.md)
- Binding spec: legacy `develop@84152635` `knowledge-graph-builder/docs/{unified-graph-model.md, recipe-spec.md}` and `app/recipes/*`.
- [R3.5 release](../releases/r3.5-make-every-service-real.md) · [knowledge-graph-service reference](../services-reference/knowledge-graph-service.md)
