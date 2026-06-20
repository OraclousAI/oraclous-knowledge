# ADR-026 — Federated Cross-Graph Query: an Aggregator over Already-Accessible Graphs

## Status

| | |
| --- | --- |
| Status | Accepted |
| Date | 2026-06-12 |
| Deciders | solution-architect (drafted), Reza (directed the capability: "query all the workspaces he got access to from a single place, as complete as possible, with more graph retrieval options") |
| Driving epic | [#312](https://github.com/OraclousAI/oraclous-backend/issues/312) · issue [#330](https://github.com/OraclousAI/oraclous-backend/issues/330) |
| Builds on | [ADR-018](adr-018-edge-authentication-trusted-gateway.md) (org-scoped trust) · [ADR-022](adr-022-recipe-primitive-unified-graph-ingestion.md) (graph substrate) · the #279 HITL resolution flow |
| Re-architects | legacy `knowledge-graph-builder/app/services/federation_service.py` (+ `entity_resolver.py`, `tasks/federation_tasks.py`) |

## Context

A higher-level agent (or user) needs to ask one question across **every workspace/graph it can access**, not one graph at a time. The legacy had a federation surface, but it was a dead end-to-end: the vector path never injected a real query vector (a stub), two of four resolver signals were hardcoded 0.0, and no frontend component ever called it. So this is a **build to the legacy's intent**, not a port — and the intent's two architectural questions must be decided once: *what may federation reach, and where does it live.*

All graphs live in **one shared Neo4j**, partitioned by `graph_id` + `organisation_id` stamped on every node — so federation is a fan-out query problem, not a cross-database one.

## Decision

1. **Federation grants NO new access — it is an aggregator over already-accessible graphs.** The federated set is exactly the graphs the caller can already read individually under the current org-scoped floor (ADR-018); per-graph access is enforced with the *same* gate the single-graph read endpoints use. An explicit `graph_ids` subset is validated ∩ accessible and **fail-closed** (any inaccessible/unknown id → reject, no partial results). No new authz model is introduced; when ReBAC enforcement lands (R7-SEC+), federation inherits it for free because it composes the single-graph gate.

   > **Amended by [ADR-036](adr-036-cross-org-foreign-row-read-under-rebac-grant.md) (2026-06-20).** The "no new access" floor is the *default*, not absolute: a fail-closed, **owner-issued ReBAC `read` grant** now authorises reading the granted graph's **owner-org rows** in federation — the exact R7-SEC+ ReBAC exception this clause and Alternative 3 reserved. #446/#459 landed the admission *gate*; ADR-036 completes the *row* read. No grant ⇒ no new access, unchanged.

2. **No `federatable` opt-in flag.** The legacy flag was friction with no consumer. Default = all accessible graphs; the subset param covers narrowing. (A per-graph *exclude* can be added later if a real need appears.)

3. **Reads live in the knowledge-retriever-service** (the read layer): federated **entity search**, **semantic/vector**, **fulltext/hybrid**, and a **federated subgraph/neighborhood fetch** — per-graph fan-out (the legacy `UNION ALL`-per-graph shape lifts), every result labeled `source_graph_id`/`source_graph_name`, bounded by per-graph and total caps and a max graph count. The vector path is **real** (embed the query with the existing 512-dim embedder; org+graph-scoped brute-force cosine per the established KRS pattern).

4. **Agents get it as a first-party tool** (`core/federated-search` in the capability-registry, mirroring `find_similar`/the retriever connector — ADR-018 trust, no credential), because the requesting party is as often a higher-level agent as a human.

5. **Cross-graph SAME_AS folds into the existing HITL resolution pipeline** (#279: `SAME_AS_CANDIDATE` → approve/reject → audited): candidates are generated across graph pairs (embedding similarity + canonical-key match), carry both graph ids, and use the same verdict endpoints/audit table. The legacy 1,038-line `EntityResolver` is **not** ported.

6. **Query-cache integration is deferred.** The #308 cache key folds ONE graph's generation counter; a federated entry would need every constituent graph's generation folded in. Skip caching federated reads v1 (correctness over speed); noted as a follow-up.

## Alternatives considered

* **Port the legacy surface as-is.** Rejected — its vector path was a stub, its authz read legacy ReBAC shadow nodes that no longer exist, and its resolver duplicates the #279 pipeline.
* **A `federatable` per-graph opt-in (legacy).** Rejected — friction with no demonstrated need; the no-new-access principle makes opt-in redundant.
* **A federation-specific access model (groups/shares).** Rejected for now — cross-org/sharing semantics belong to the R7-SEC+ ReBAC work; building them inside federation would fork the authz model.

## Consequences

* KRS gains federated read routes + fan-out repositories; the gateway proxies them; capability-registry gains `core/federated-search`.
* The **no-new-access invariant is testable**: a graph outside the caller's access never appears in any federated result (cross-org isolation tests are mandatory).
* Fan-out cost is bounded by caps, and federated reads are uncached v1.
* KGS's resolution vertical accepts cross-graph candidate pairs (same HITL endpoints + audit).

## See also

* ADR-018 (org-scoped trust) · the #279 resolution/HITL flow · the #308 cache (generation counters)
* Legacy: `federation_service.py`, `endpoints/federation.py`, `tasks/federation_tasks.py`, `components/entity_resolver.py`
* Issues [#330](https://github.com/OraclousAI/oraclous-backend/issues/330) · [#312](https://github.com/OraclousAI/oraclous-backend/issues/312)
