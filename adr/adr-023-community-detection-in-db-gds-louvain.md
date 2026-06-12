# ADR-023 — Community Detection via In-DB Neo4j GDS Louvain (Community Edition)

## Status

| | |
| --- | --- |
| Status | Accepted |
| Date | 2026-06-12 |
| Deciders | solution-architect (drafted), Reza (signed off) |
| Driving epic | [#294](https://github.com/OraclousAI/oraclous-backend/issues/294) — Legacy-restorations · issue [#303](https://github.com/OraclousAI/oraclous-backend/issues/303) |
| Re-architects | legacy in-memory `leidenalg` community detection (`knowledge-graph-builder/app/{tasks/community_tasks.py,services/community_summarizer.py,services/analytics_service.py}`) |
| Builds on | [ADR-022](adr-022-recipe-primitive-unified-graph-ingestion.md) (ingestion) · [ADR-016](adr-016-canonical-service-architecture-and-hardened-definition-of-done.md) §21 (service architecture) · [ADR-018](adr-018-edge-authentication-trusted-gateway.md) (multi-tenant scope) |

## Context

R3.5 rebuilt the knowledge-graph-service without the legacy's community-detection + analytics surface. The legacy detected communities with an **in-memory Python `leidenalg`** run at five resolutions `[0.5, 1.0, 2.0, 3.0, 4.0]` → a multi-level `:__Community__` hierarchy + `IN_COMMUNITY` edges, then LLM-summarised each community (`summary` / `summary_keywords` / `summary_excerpt` + provenance) and exposed `/communities` + `/analytics` endpoints.

Two facts about the **current deployed substrate** force the decision:

* The deployed Neo4j is **`neo4j:5.23-community`** and **already loads the GDS plugin** (`deploy/docker-compose.yml`: `NEO4J_PLUGINS: ["apoc","graph-data-science"]`, `gds.*` unrestricted). So in-database graph algorithms are available with no infra change.
* **GDS Louvain ships in Community Edition; GDS Leiden is Enterprise-only.** The legacy algorithm (Leiden, via the python lib) cannot run in-DB on the current image without an Enterprise upgrade + license.

The legacy also ran the algorithm *outside* the database (python), paying a full graph round-trip. Re-architecting onto in-DB GDS removes both the python graph library and the round-trip — the platform-native path.

## Decision

1. **In-DB GDS Louvain — not Leiden, not python `leidenalg`.** Community detection runs as Cypher `CALL gds.louvain.*` inside Neo4j. Louvain is chosen because it ships in **GDS Community** (zero license cost, no image change) and yields equivalent multi-resolution community structure for graph-comprehension. Leiden would force `neo4j:5.23-enterprise` + a license; deferred to a future ADR if community quality ever demands it. **The algorithm is swappable behind the repository** (see §5).

2. **Multi-resolution hierarchy preserved.** Louvain is run to produce the same five-level hierarchy (`includeIntermediateCommunities` and/or the `resolution`/`gamma` parameter, else N runs). Output is written as `:__Community__ {community_id, level, entity_count, status}` (community_id = deterministic SHA-256 of sorted member ids, matching the legacy 16-char scheme) + `IN_COMMUNITY` edges `__Entity__ → __Community__`.

3. **Writes go through the existing injected-scope writer.** Every community node/edge is stamped `organisation_id` / `graph_id` / `transaction_time` server-side via the `OrganisationScopedKGWriter` / `MultiTenantKGWriter` path — **the caller cannot override the injected scope.** This preserves the multi-tenant + bitemporal invariants the rest of the graph already obeys.

4. **In-DB projection is org+graph-scoped and short-lived.** Project only the `organisation_id`+`graph_id`-scoped `__Entity__` subgraph, run, and `gds.graph.drop` the in-memory projection in a `finally`. Detection, list, get and status are all org+graph scoped — one org cannot see or trigger another's communities.

5. **LLM summarisation retained.** Per-community `summary` / `summary_keywords` / `summary_excerpt` + provenance (`summary_model` / `summary_at`) via the same OpenAI-compatible client the KGS already uses for extraction, concurrency-limited (`asyncio.Semaphore`, per the #272 fix), behind its own endpoint.

6. **Endpoints mirror the legacy shapes**, §21-layered (`routes → services → domain → repositories`, repositories the only Neo4j/GDS access): `GET /communities/kinds`, `GET /graphs/{id}/communities?level=&kind=`, `POST /graphs/{id}/communities/detect` (→ 202 async via the existing Celery job pattern, or sync when small), `GET …/{community_id}`, `GET …/status`, `POST …/summarize`, and `GET /graphs/{id}/analytics`.

## Alternatives considered

* **A. Leiden on Neo4j Enterprise.** Rejected for now — adds a license cost + a higher Enterprise memory footprint + an infra change, for a community-quality gain that our use (graph comprehension, summarisation seeds) does not require. The repository abstraction keeps this a one-line swap if it is ever justified.
* **B. Keep the in-memory python `leidenalg`.** Rejected — re-introduces a python graph library and a full graph round-trip out of the database. In-DB GDS is the platform-native path and is already installed.
* **C. Defer community detection entirely.** Rejected — it is a high-value graph-comprehension capability and is clean to build with Louvain on the current Community image (no prerequisite, no schema migration).

## Consequences

* KGS gains `repositories/community_repository.py` (the only GDS access), `services/analytics_service.py`, a community summariser, and `routes/community_routes.py`.
* The **GDS plugin becomes load-bearing** (already present). A GDS-unavailable condition returns a typed error, never a swallowed 500.
* **No schema migration** — communities are ordinary Neo4j nodes/edges under the existing tenancy stamps.
* The Louvain→Leiden choice is now an isolated, reversible decision behind `community_repository`, contingent only on an Enterprise adoption decision.

## See also

* [ADR-022](adr-022-recipe-primitive-unified-graph-ingestion.md) — ingestion model the communities sit on top of
* §21 canonical service architecture · ADR-016 · ADR-018 (multi-tenant scope)
* Legacy source: `legacy-reference/old-backend/knowledge-graph-builder/app/{tasks/community_tasks.py, services/community_summarizer.py, services/analytics_service.py, api/v1/endpoints/communities.py}`
* Issues [#303](https://github.com/OraclousAI/oraclous-backend/issues/303) · [#294](https://github.com/OraclousAI/oraclous-backend/issues/294)
