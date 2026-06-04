---
confluence_id: "688329"
title: "Section 8 — Consolidation and Migration Plan"
---

# Section 8 — Consolidation and Migration Plan

**Related structured artifacts:** the phases below reference implementation contracts that live in sibling pages. Implementers consulting this plan should resolve those references against the artifacts, not against this section's prose.

* **Phase 0.5** (organisation tenancy) establishes the foundation that the policy sets in [Structured Governance Taxonomy](https://oraclous.atlassian.net/wiki/spaces/OP/pages/688439) bind to via `owner_organization`. The relevant ADRs are [ADR-006](https://oraclous.atlassian.net/wiki/spaces/OP/pages/393403) (organisation as outermost tenancy unit) and [ADR-008](https://oraclous.atlassian.net/wiki/spaces/OP/pages/753792) (cloud-hosted equivalence + operator separation).
* **Phase 2** (capability registry consolidation) emits OHM-shaped descriptors. The descriptor schema, canonical serialisation, and reference resolution semantics are in [OHM v1.0 Standalone Specification](https://oraclous.atlassian.net/wiki/spaces/OP/pages/393501); the canonical-hub decision is [ADR-002](https://oraclous.atlassian.net/wiki/spaces/OP/pages/557058).
* **Phase 7** (compiler harness and seed manifests) emits OHM documents for the default compiler, default consciousness skill, default policy template. The default policy template binds to entries from the Governance Taxonomy; seed manifests must validate against the OHM spec.
* **Phase 8** (security hardening pass) implements the mitigations from [Structured Threat Catalogue](https://oraclous.atlassian.net/wiki/spaces/OP/pages/983129). Each Phase 8 deliverable maps to one or more Tn-Mn mitigation IDs; the required tests are named in the catalogue's `required_tests` blocks.

This section is authoritative for the migration sequence and service decomposition; the artifacts are authoritative for what each phase must produce or satisfy.

> **R3.5 status note (2026-06-04) — this migration did NOT actually happen; R3.5 executes it for real.** The phased plan below (Phase 0 through Phase 9, "lift and extend, never rewrite") is the intended decomposition. The audit truth is that the R2/R3 service migration **never landed**: `capability-registry-service`, `knowledge-graph-service`, and `knowledge-retriever-service` shipped as **hollow shells** — stub endpoints, `raise NotImplementedError`, a `GraphNodeService` stub class defined inside a route file — and the real logic this section calls out for lift (the tool registry, `AgentExecutor`, the retriever, ingestion, etc.) **still lives in `oraclous-core-service`** (~6,300 LOC, undeleted and dead). The lift-not-rewrite intent held, but the lift was not performed. **R3.5 executes the migration for real, service by service**, each one rebuilt end-to-end against real substrate and personally signed off by Reza before the next dependent service starts, in graph-first order: (1) knowledge-graph-service → (2) knowledge-retriever-service → (3) a new identity/org service (users + email + OAuth + orgs/members/roles/invites; orgs leave the graph service) → (4) credential-broker-service → (5) capability-registry + tools + connectors (ported from `oraclous-core-service`). The migration ends in the **salvage-then-delete of `oraclous-core-service`** — it stays (`port_source: true`, `deletable: false`) until its logic is ported and tested, and its deletion is destructive and **human-gated**. The per-service Definition of Done and the salvage-then-delete protocol are canonical in **ORAA-4 operating-contract (§21–§23 + the hollowness-audit / salvage-then-delete clauses)**; when this section and ORAA-4 diverge, ORAA-4 wins. The original phasing below is left intact as the record of the intended shape.

This section answers a single question: **how do we get from the current Oraclous codebase to the target architecture described in Sections 1-7, without breaking production features and without accumulating architectural debt?**

It is the most concrete section in the document. It names specific services, specific code that gets lifted or collapsed, and proposes a phased migration that preserves working features through the transition. It applies the architectural commitments from previous sections to the codebase reality.

The section is organised around four questions:

1. **Where is the code today?** An honest assessment of the current shape.
2. **Where should it be?** The target shape, mapped to the four-layer architecture.
3. **How do we get there?** The migration sequence, phased to minimise disruption.
4. **What do we deliberately not move?** Code paths that stay where they are by choice.

The guiding principles for the plan are software engineering best practices: **separation of concerns** (services own one thing each), **cohesion** (related code lives together), **clear boundaries** (cross-service contracts are explicit), **incremental migration** (every step ships independently and reversibly), and **security continuity** (no working defence is weakened during the migration).

---

## Current state of the codebase

The current Oraclous codebase consists of four backend services. The honest assessment of each:

### `auth-service`

**Purpose:** User authentication, OAuth flows, JWT issuance.

**State:** Production-grade. Well-scoped, single responsibility, clean API. Handles members, service accounts, and the principal-type distinction the rest of the platform relies on.

**Verdict:** Stays largely as-is. Will need extensions for agent identity (Section 8.2) and delegated identity issuance (Section 6.5 Threat 4.1), but the core service is correctly factored.

### `credential-broker-service`

**Purpose:** Credential storage, OAuth token resolution, scope-based access to external providers.

**State:** Production-grade. Encrypted credential storage, OAuth refresh flows, capability descriptors for data source access. Clean separation from auth-service. Used by `oraclous-core-service` for tool execution and by `knowledge-graph-builder` for LLM API key resolution.

**Verdict:** Stays largely as-is. Will be extended to support delegated identity (agents acting on behalf of members under specific scopes) and to broker credentials for internal cross-workspace traversal.

### `oraclous-core-service`

**Purpose:** Originally intended as the orchestrator — tool registration, workflow management, instance manager, execution service.

**State:** **Mixed.** Has production-grade pieces (tool registry, credential client, tool execution service, validation service) alongside placeholder pieces (workflow service is a stub, pipeline generator is a stub, no actual workflow execution engine). The tool registry is real but disconnected from the agent runtime that lives elsewhere.

**Verdict:** This is the service that needs the most restructuring. The tool registry and execution service are foundations that need to evolve into the Capability Registry (Layer 2). The empty workflow execution engine needs to be retired in favour of the harness runtime (Layer 3). Some pieces stay, some lift, some get deleted.

### `knowledge-graph-builder`

**Purpose:** Originally intended as the knowledge graph layer — ingestion, retrieval, schema management.

**State:** **Sprawling.** The most production-grade service in the codebase, but it has accreted concerns that don't belong: the `AgentExecutor`, the `:Agent` Neo4j nodes, the chat persistence layer, integration keys for published agents, MCP server work (now retired), the agent toolkit, the LLM client factory. It's the largest service by code volume and contains the platform's best agent runtime, but the runtime is buried inside a service that was meant to build knowledge graphs.

**Verdict:** This service needs to be **decomposed**. The knowledge graph functionality stays (renamed and scoped). The agent runtime lifts out into a new service (the Harness Runtime, Layer 3). The retriever splits out (into a Knowledge Retriever service). The published agents and chat persistence become Application Gateway concerns. The MCP server work stays retired — its lessons inform the new design, but the code is gone.

### Current architecture diagram

```
┌─────────────────────────────────────────────────────────┐
│ auth-service (port 8000)                                │
│ • User authentication, JWT, OAuth                       │
│ • Member, service-account principal types               │
│ STATUS: Production-grade                                │
└─────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────┐
│ credential-broker-service (port 8002)                   │
│ • OAuth token storage and refresh                       │
│ • Capability descriptors for external providers         │
│ STATUS: Production-grade                                │
└─────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────┐
│ oraclous-core-service (port 8001)                       │
│ • Tool registry (real, but disconnected)                │
│ • Tool execution service (sync + async + jobs)          │
│ • Instance manager (per-workflow tool configuration)    │
│ • Validation service                                    │
│ • Workflow models + schemas (DB layer real, runtime stub)│
│ • Pipeline generator (stub)                             │
│ STATUS: Mixed — half production, half placeholder       │
└─────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────┐
│ knowledge-graph-builder (port 8003)                     │
│ • Ingestion (text, documents, code, structured)         │
│ • Retrieval (vector, hybrid, graph, text-to-cypher)     │
│ • Schema management                                     │
│ • Analytics (community detection, centrality)           │
│ • Chat persistence (Postgres + RLS)                     │
│ • Chat engine (synthetic agent over chat config)        │
│ • AgentExecutor (multi-mode tool-use loop)              │
│ • Agent CRUD (Neo4j-persisted :Agent nodes)             │
│ • Agent toolkit (graph-bound tools)                     │
│ • Published agents + integration keys                   │
│ • LLM client factory + LLM config service               │
│ • Multi-tenant components and isolation                 │
│ • Provenance collector                                  │
│ • Federation (cross-graph LINKED_TO traversal)          │
│ STATUS: Sprawling — production-grade content, wrong     │
│         service boundaries                              │
└─────────────────────────────────────────────────────────┘
```

This is the starting point. The target is below.

---

## Target architecture mapped to services

The four-layer architecture from Section 3 maps to a target service set. Some services from today survive with adjusted scope; some new services emerge from decomposition; some scattered logic gets pulled together.

### Target service set

```
┌─────────────────────────────────────────────────────────┐
│ LAYER 1: SUBSTRATE                                      │
│                                                         │
│ auth-service (port 8000)                                │
│ • User + agent identity                                 │
│ • Delegated identity issuance                           │
│                                                         │
│ credential-broker-service (port 8002)                   │
│ • Credentials + scoped delegation                       │
│ • Internal credential brokerage                         │
│                                                         │
│ knowledge-graph-service (port 8003)  [renamed]         │
│ • Build (ingestion)                                     │
│ • ReBAC graph maintenance                               │
│ • Provenance + audit storage                            │
│ • Multi-modal storage commitments                       │
│                                                         │
│ knowledge-retriever-service (port 8006)  [NEW]         │
│ • Read-side queries (vector, hybrid, graph, temporal)   │
│ • Modality-uniform NodeResult envelope                  │
│ • ReBAC-gated retrieval                                 │
└─────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────┐
│ LAYER 2: CAPABILITY REGISTRY                            │
│                                                         │
│ capability-registry-service (port 8001)  [evolved      │
│  from oraclous-core-service]                            │
│ • Unified capability descriptor model                   │
│ • Tools, skills, agents, harnesses, human roles         │
│ • Versioning (content hash + semver tags)               │
│ • Adapter contracts (inbound + outbound)                │
└─────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────┐
│ LAYER 3: HARNESS RUNTIME + EXECUTION ENGINE             │
│                                                         │
│ harness-runtime-service (port 8004)  [NEW, lifted      │
│  from knowledge-graph-builder]                          │
│ • Harness execution                                     │
│ • Actor dispatch (agents + humans)                      │
│ • Multi-actor coordination                              │
│ • Policy envelope enforcement                           │
│ • Round-table primitive                                 │
│ • Provenance write-through                              │
│                                                         │
│ execution-engine-service (port 8005)  [NEW]            │
│ • Durable execution (long-running, checkpointed)        │
│ • Schedule firing                                       │
│ • Job tracking                                          │
│ • Task board state management                           │
└─────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────┐
│ LAYER 4: APPLICATION GATEWAY                            │
│                                                         │
│ application-gateway-service (port 8007)  [NEW, lifted  │
│  from knowledge-graph-builder + oraclous-core-service]  │
│ • Public APIs                                           │
│ • Published agents + integration keys                   │
│ • MCP server (inbound)                                  │
│ • MCP client (outbound)                                 │
│ • Webhook receivers                                     │
│ • Embeddable widgets                                    │
│ • Member-facing UIs                                     │
└─────────────────────────────────────────────────────────┘
```

### Service-by-service decisions

| Current Service | Target Service(s) | Disposition |
| --- | --- | --- |
| `auth-service` | `auth-service` | **Keep**, extend for agent identity |
| `credential-broker-service` | `credential-broker-service` | **Keep**, extend for delegated identity |
| `oraclous-core-service` | `capability-registry-service` (mostly) + parts to gateway | **Restructure**: tool registry → capability registry, execution → harness runtime, workflow stubs → retire |
| `knowledge-graph-builder` | `knowledge-graph-service` (ingestion + storage) + `knowledge-retriever-service` (reads) + `harness-runtime-service` (agent runtime) + `application-gateway-service` (public surface) | **Decompose**: this is the biggest single migration |

### Why this shape

A few load-bearing decisions worth naming:

**The knowledge graph builder splits in two.** Build and retrieve are different responsibilities with different access patterns, scaling profiles, and security concerns. Build is write-heavy, latency-tolerant, runs in batches. Retrieve is read-heavy, latency-critical, runs synchronously. They share substrate but should be separate services. This is item 1 + 2 from your gap analysis made concrete.

**The harness runtime is a new service, lifted from** `knowledge-graph-builder`. The `AgentExecutor` is the most production-grade agent runtime in the codebase, but it lives in the wrong service. Lifting it into its own service (with the toolkit, LLM client factory, LLM config service, provenance collector) frees the knowledge graph service to focus on graphs and lets the runtime grow into the Harness Runtime that hosts the compiler, consciousness agents, and all customer harnesses.

**The execution engine is its own service.** Long-running jobs, schedules, and checkpoints have different operational characteristics than synchronous request handling. Separating them prevents schedule firing from being constrained by API request limits, and lets the engine scale independently.

**The application gateway is new and pulls together scattered public surfaces.** Today, published agents live in `knowledge-graph-builder`. The MCP server work (retired) was scattered. Chat APIs are in the KG builder. None of these are KG concerns. Pulling them into a dedicated gateway service consolidates the external surface area into one place with one consistent security model.

**The capability registry is the evolution, not the replacement, of** `oraclous-core-service`. The tool registry, instance manager, validation service, and credential client are the right foundations for a unified capability registry. The workflow stubs, the empty pipeline generator, the placeholder execution path — those get retired. What stays gets generalised from "tools" to "capabilities" (tools + skills + agents + harnesses + human roles).

---

## What lifts, what stays, what collapses, what retires

For each major code area in the current codebase, the disposition:

### Lift (moves to a new service, mostly intact)

`AgentExecutor` and related (`knowledge-graph-builder/app/services/agent_executor.py`) → harness-runtime-service. The whole multi-mode tool-use loop, the streaming variant, the provenance collector, the LLM client factory, the LLM config service, the tool-use protocol types. This is the largest single lift.

**Agent toolkit (**`agent_tools.py`, `agent_tool_schemas.py`) → harness-runtime-service initially, then capability-registry-service over time. The toolkit is currently graph-bound; as it migrates, the graph tools become one _category_ of capability among many. The schemas registry becomes the registry's structured-schema source.

**Agent CRUD (**`agent_service.py`, agent endpoints) → harness-runtime-service. The `:Agent` Neo4j nodes themselves stay in the knowledge graph substrate (they are graph-shaped artifacts), but the _service_ that creates and manages them lives with the runtime. The substrate provides the persistence; the runtime owns the lifecycle.

**Chat persistence (**`chat_history_service.py`, chat endpoints, RLS policies) → application-gateway-service. Chat is a public-facing surface, not a graph concern. The Postgres-with-RLS implementation moves as-is; it is production-grade and the RLS pattern is exactly what the gateway needs for member-scoped data.

**Chat engine (**`chat_engine.py`) → harness-runtime-service. The synthetic-agent pattern (build an in-memory agent config and dispatch it through the executor) becomes the runtime's standard pattern for chat-shaped interactions.

**Published agents + integration keys (**`integration_key_service.py`, public endpoints) → application-gateway-service. This is core gateway functionality: rate limits, integration keys, CORS scoping, slug-based routing. Already well-factored, just moves.

**Provenance collector (**`provenance.py`) → harness-runtime-service for in-flight collection, substrate for persistent storage. The collector follows the runtime; the storage follows the substrate.

**Tool registry (**`oraclous-core-service/app/services/tool_registry.py` and `tool_registry.py` in `app/tools/`) → capability-registry-service. The two registries (DB-backed and in-memory) consolidate into one. The DB schema stays; the in-memory pattern is reworked to be the runtime cache, not a separate source of truth.

**Tool execution service (**`tool_execution_service.py`) → execution-engine-service. Job tracking, sync/async execution, progress streaming. Production-grade, just lifts.

### Stay (kept where they are, possibly extended)

`auth-service` in its entirety. Extended for agent identity issuance and delegated identity tokens, but the service stays.

`credential-broker-service` in its entirety. Extended for internal cross-workspace credential brokerage and for delegated identity scope verification.

**Knowledge graph ingestion (**`pipeline_service.py`, `background_jobs.py`, ingestion endpoints) stays in `knowledge-graph-service` (the renamed builder). This is the substrate's write side and belongs there.

**Multi-tenant components (**`multi_tenant_components.py`) stays in `knowledge-graph-service`. These are graph-write enforcement primitives.

**Schema management (**`schema_manager.py`, schema endpoints) stays in `knowledge-graph-service`. Schema is a build-side concern; retrieval consumes schemas but doesn't define them.

**Code parser (**`code_parser_service.py`) stays in `knowledge-graph-service`. Code ingestion is multi-modal ingestion.

**Federation (LINKED_TO traversal,** `task-205` work) stays in `knowledge-retriever-service` (the new read service). It is fundamentally a retrieval concern — _cross-workspace reads_ — not an ingestion concern.

**Analytics (**`analytics_service.py`, community detection, centrality) stays in `knowledge-graph-service` (the write side runs detection) with read APIs exposed by `knowledge-retriever-service`. This is one of the cleaner separations.

### Collapse (multiple things become one)

**The two tool registries collapse into one.** The in-memory `tool_registry.py` (registers Python classes) and the DB-backed `ToolRegistryService` (manages persisted `ToolDefinitionDB` rows) become a single Capability Registry service with one descriptor model, one storage backend, and one resolution path. The dual-registry pattern goes away.

**The** `agent_tool_schemas.py` registry collapses into the Capability Registry. Today the agent toolkit has its own schema registry separate from the tool registry. After consolidation, every capability (graph tool, external tool, MCP-imported tool, skill, agent, human role) has one descriptor in one place.

**The chat persistence concept and the harness-execution concept partially collapse.** Today, "chat" and "agent execution" are two systems that share infrastructure. After consolidation, a chat is a particular shape of harness execution (a single-actor conversational harness with a chat-style task board). The chat persistence schema stays as-is initially, but it can converge with harness execution state over time.

**The workflow concept retires entirely (see below) and its replacement is the harness.** This is a conceptual collapse rather than a code collapse.

### Retire (deleted, with reasons)

**The empty workflow execution engine (**`workflow_service.py`, `pipeline_generator.py`). These are stubs. The workflow schema and DB models are real but were built for a workflow runtime that was never implemented. The harness model replaces the workflow concept; the schema can be reused as the basis for harness storage (with adaptation) or retired entirely depending on migration sequencing. **Recommendation: retire and start fresh with OHM-shaped storage for harnesses.** The current workflow schema doesn't map cleanly to OHM (no orchestration prose, no roster of actors with mixed types, no task board structure) and forcing the fit creates more debt than starting clean.

**The MCP server work (**`docs/RETIRED-mcp-substrate.md` already documents the retirement). Stays retired. Lessons from the retirement document (closed bespoke substrate problems) directly inform the new MCP server design in the Application Gateway — but the code stays gone. The new MCP server is a Gateway concern, designed differently.

**The instance manager's role as a workflow node configurator.** The instance manager is real and useful, but its current purpose (per-workflow tool configuration) is bound to the workflow concept. The Capability Registry replaces the per-workflow configuration pattern with a per-harness capability allocation pattern. The instance manager's code can be salvaged into the registry's invocation handle logic, but the _concept_ of an instance retires.

**Various stub services and copilot-instruction docs (**`oraclous-core-service/github/copilot-instruction.md`) that propose features (LangGraph integration, websocket workflow updates, optimisation passes) for the workflow runtime that won't be built. Documentation cleanup; no code impact.

---

## The graph retriever decision

You flagged this explicitly as something to decide in Section 8 after multi-modal considerations are factored in. Here is the decision and the reasoning.

### Decision

**Extract the retriever into its own service** (`knowledge-retriever-service`), leaving `knowledge-graph-service` (the renamed builder) as ingest-only.

### Reasoning

Three factors point in the same direction:

**Different access patterns.** Build is write-heavy, batch-friendly, and tolerates latency. Retrieve is read-heavy, latency-sensitive, and runs synchronously alongside agent reasoning. Combining them means scaling both for the worse case of either.

**Different multi-modal evolution paths.** Adding a new modality on the build side is a parser + ingestion pipeline. Adding it on the read side is a new retrieval shape + index integration. These evolve independently. Splitting them lets each evolve at its own pace.

**Different governance and audit needs.** Reads happen far more frequently than writes. The read service's audit volume will dwarf the build service's. Splitting them lets each have appropriately scoped logging and audit retention without one service drowning in the other's volume.

The alternative (single combined service with internal build/read modules) is simpler operationally but loses each of these benefits. For a self-hosted open-source platform where operators may want to scale, audit, and extend each side independently, the split is worth the operational cost.

### Multi-modal considerations

As called out in the multi-modal substrate commitments (Section 3), every modality is stored as nodes in the knowledge graph with modality-appropriate indexes. The retriever exposes modality-appropriate retrieval shapes but they all return the same `NodeResult` envelope.

This means: **the retriever service has multiple retrieval endpoints (semantic search, full-text search, hybrid search, graph traversal, temporal slice, perceptual match) but one result envelope.** Agents and harnesses don't reason about which modality they're consuming; the retriever handles it.

For currently-supported modalities, the retriever exposes:

* Semantic search (text, document, code)
* Full-text search (text, document, code)
* Hybrid search (text-heavy modalities)
* Graph traversal (relationships)
* Temporal slice (bitemporal data)

For future modalities, the retriever extends:

* Perceptual match (images, video frames)
* Acoustic match (audio)
* Geometric query (3D, spatial)

Adding a future modality is a substrate-internal change. The retriever extension is a new endpoint and a new index integration; the rest of the platform doesn't change.

### Migration path for the retriever

The retriever code already exists in `knowledge-graph-builder` — it just lives in a service that also does ingestion. The migration is **extract, not rebuild**:

1. Identify all retrieval code in `knowledge-graph-builder`: `retriever_service.py`, `retriever_factory.py`, the retriever-specific multi-tenant components, the full-text index service, the query cache, the chat engine's retrieval paths.
2. Move these into a new `knowledge-retriever-service` with its own deployment unit.
3. The new service shares the Neo4j substrate (same database) but runs as a separate process with its own scaling profile.
4. The old `knowledge-graph-builder` (now `knowledge-graph-service`) drops these modules; its imports update; its tests for retrieval move to the new service.

This is mechanically straightforward because the code already exists and is well-factored. The hard part is the coordination — ensuring no in-flight references break during the transition.

---

## Migration phasing

The migration runs in phases, each shipping independently and each leaving the platform in a working state. No phase requires all subsequent phases to be useful; each ends with production parity or better.

### Phase 0 — Documentation and stabilisation (Weeks 1-2)

Before any code moves: lock in the architecture document, lock in OHM v1 spec, lock in the capability descriptor schema, lock in the ReBAC extensions needed for agent identity.

**Deliverables:**

* This document (v1.0 final, after Section 9)
* OHM v1 specification document (extracted from Section 4 as a standalone artifact)
* ADRs for the major architectural decisions (the four-layer split, OHM as canonical format, runtime-as-platform/actors-as-harnesses, federation by ReBAC)
* Capability descriptor schema (extracted from Section 4 as a standalone artifact)

**Why this matters:** code changes without locked-down architecture cause drift. The document is the contract every phase below conforms to.

### Phase 0.5 — Organisation tenancy and metering substrate (Weeks 3-4, parallel with Phase 1)

Before code reorganisation begins, the substrate gains two foundational additions: organisation-level tenancy enforcement and metering. These changes ripple through every subsequent phase, so they happen early.

**Deliverables:**

* `organization_id` added to every storage primitive (Neo4j nodes/relationships, Postgres tables, Redis keys, cache entries)
* Every query and write path extended to include `organization_id` as a mandatory filter
* Multi-tenant component wrappers extended to enforce organisation scoping
* Multi-tenant isolation test suite extended with organisation boundary tests
* Metering subsystem implemented in the substrate (tokens, invocations, storage, time tracking)
* Metering write hooks added at the runtime, capability registry, and substrate
* Usage reporting API in the substrate exposing organisation-scoped metering data
* For existing deployments: migration script to add an `organization_id` to all existing data (single default organisation per existing deployment)

**Why this matters:** organisation tenancy is the cloud-mode prerequisite. Metering is the cloud-mode billing prerequisite. Both need to exist before service reorganisation creates new attack surfaces — adding tenancy retroactively across many services is much harder than adding it once at the data layer.

**Risk and mitigation:** existing deployments are single-organisation; the migration is mechanical. The risk is missing a query path that should have organisation scoping. Mitigation: the multi-tenant test suite extension is the gate — no Phase 0.5 deliverable ships without all isolation tests passing for organisation boundaries.

### Phase 1 — Auth and credential extensions (Weeks 5-6)

Extend the existing auth-service and credential-broker-service to support the new identity model. These are the smallest, most contained changes and unblock everything else.

**Deliverables:**

* Agent identity issuance in `auth-service` (agents as principals alongside users and service accounts)
* Delegated identity tokens in `credential-broker-service` (member-to-agent scope delegation)
* ReBAC graph extensions for delegated relationships
* Migration scripts for existing data (agents created during the migration get post-hoc identities)

**Why this matters:** every subsequent phase depends on agents having their own identities. Doing this first prevents downstream rework.

### Phase 2 — Capability registry consolidation (Weeks 7-10)

Take `oraclous-core-service` and evolve it into the Capability Registry. Consolidate the two tool registries. Generalise from tools to capabilities. Introduce OHM-shaped descriptors.

**Deliverables:**

* `capability-registry-service` (renamed from `oraclous-core-service`)
* Unified capability descriptor schema with kind discrimination (tool, skill, agent, harness, human_role)
* Single resolution path replacing the dual-registry pattern
* Versioning with content hashes
* The first inbound adapter: MCP tool importer
* Retirement of the workflow stubs and pipeline generator (with documentation noting what they were and why they were retired)

**Why this matters:** the registry is the substrate's discovery surface for everything composable. Until it exists in target shape, the harness runtime can't compose against it.

**Risk and mitigation:** existing tools registered today (Google Drive Reader, Notion Reader, PostgreSQL Reader, MySQL Reader) are real production capabilities used by customers. They must keep working through the migration. Each tool gets a generated OHM descriptor; their existing executor classes remain (the descriptor wraps them). Customer-facing API contracts are preserved.

### Phase 3 — Knowledge graph decomposition (Weeks 11-16)

Split `knowledge-graph-builder` into `knowledge-graph-service` (build) and `knowledge-retriever-service` (read).

**Deliverables:**

* `knowledge-retriever-service` extracted as its own service with its own deployment
* Retrieval modules moved (retriever_service.py, retriever_factory.py, multi-tenant retrieval components, full-text index service, query cache, retrieval-side federation)
* `knowledge-graph-service` (renamed from builder) retains ingestion, schema management, analytics
* Cross-service API contracts defined and tested
* Multi-tenant isolation tests run against both services

**Why this matters:** this is the most disruptive single phase. It touches the largest service in the codebase. Doing it cleanly here prevents the harness runtime from having to bridge a still-monolithic graph service.

**Risk and mitigation:** ingestion and retrieval depend on the same data. Both services connect to the same Neo4j database with appropriate roles. Migration is mechanical; tests for retrieval move to the new service. Customer-facing chat endpoints route through the retriever (initially the application gateway proxies; in Phase 5 the gateway calls directly).

### Phase 4 — Harness runtime extraction (Weeks 17-20)

Lift `AgentExecutor` and related code out of `knowledge-graph-builder` (now `knowledge-graph-service`) into a new `harness-runtime-service`. Generalise the executor past single-graph use.

**Deliverables:**

* `harness-runtime-service` as its own deployment
* AgentExecutor, agent toolkit, LLM client factory, LLM config service, provenance collector — all migrated
* Agent CRUD APIs moved (the `:Agent` nodes remain in the graph substrate but the lifecycle service lives with the runtime)
* The new runtime calls into the Capability Registry for capability resolution (instead of the toolkit's in-memory schema registry)
* The new runtime calls into the Knowledge Retriever for graph reads (instead of direct Neo4j queries from the toolkit)
* Multi-actor coordination primitives (initially: hand-off between agents, with HITL and round-tables coming in Phase 5)

**Why this matters:** this is the central nervous system of the new platform. Until the harness runtime exists in target shape, harnesses cannot be defined or run.

**Risk and mitigation:** the existing `AgentExecutor` powers chat (synthetic agent pattern). Chat must keep working through the migration. The chat engine moves with the runtime; chat APIs continue working with the new service backing them. From the customer's perspective, no visible change.

### Phase 5 — Execution engine and runtime completion (Weeks 21-24)

Extract the durable execution side (`tool_execution_service.py`, job tracking, async progress) from `oraclous-core-service` (now `capability-registry-service`) into a new `execution-engine-service`. Complete the harness runtime with HITL, round-tables, schedules, and task boards.

**Deliverables:**

* `execution-engine-service` as its own deployment
* Tool execution service code migrated (sync + async + jobs)
* Task board data model implemented in the substrate
* HITL primitive (task assignment + notification dispatch + resumption)
* Round-table primitive (lifecycle, invitation, contribution, decision capture)
* Schedule firing with the execution engine
* Multi-actor coordination via task boards
* Cross-workspace federation traversal in the runtime

**Why this matters:** this completes the runtime to the point where it can host the default compiler. Without HITL and round-tables and schedules, the compiler harness cannot be built.

### Phase 6 — Application Gateway extraction (Weeks 25-28)

Lift the public-facing surface (chat APIs, published agents, integration keys, embeddable widgets, the new MCP server, member-facing UIs) into a new `application-gateway-service`.

**Deliverables:**

* `application-gateway-service` as its own deployment
* Chat APIs migrated (the persistence layer goes here; the execution backing remains the harness runtime)
* Published agents and integration keys migrated
* New MCP server implementation (drawing lessons from the retired MCP work but written fresh per Section 7)
* New MCP client integration (importing external MCP tools into the registry)
* Webhook receivers
* Task board UI APIs

**Why this matters:** the gateway is the platform's contract with the outside world. Until it exists in target shape, the platform's portability story can't be demonstrated.

### Phase 7 — Compiler harness and seed manifests (Weeks 29-32)

Build the default compiler harness. Define seed manifests for new workspaces. Implement the bootstrap update flow.

**Deliverables:**

* Default compiler harness in OHM, deployed as the seed compiler for new workspaces
* Default consciousness skill in OHM
* Default capability inventory definition
* Default task board definition
* Default policy template
* Reference catalog mechanism
* Bootstrap update notification flow
* Diff-and-accept UI for platform-published updates

**Why this matters:** this is the platform's "first turn." Before Phase 7, workspaces have a runtime but no compiler. After Phase 7, a workspace admin can describe a goal in prose and get a working harness back. The product loop closes.

### Phase 8 — Security hardening pass (Weeks 33-36)

Implement the Phase 2 (hardening) and Phase 3 (advanced) mitigations from Section 6.5's phased mitigation plan that weren't already covered by the migration.

**Deliverables:**

* Indirect prompt injection sanitization extensions
* Output redaction extensions (custom patterns)
* Cross-workspace traversal audit reports
* Service account principal type hardening
* Cache key isolation audits
* Consciousness drift detection (initial implementation)
* Federation laundering audit reports
* Adapter output validation
* Schedule storm protection

**Why this matters:** the security commitments in Section 6.5 are documented from day one but implemented across phases. Phase 8 brings them to parity with the architecture.

### Phase 9 — Ongoing (continuous)

Iterative improvement, customer feedback, additional adapters, additional modalities, additional default capabilities. The platform exists at v1; everything afterward is continuous evolution against the architecture, not against the migration plan.

### Parallel track: Cloud-mode compliance work

Cloud-hosted deployment requires compliance certifications that the engineering phases above produce _evidence_ for but do not themselves achieve. The compliance work runs in parallel with engineering and has its own timeline driven by external auditors, not by the engineering phases.

**Compliance commitments for cloud mode (v1):**

* **ISO 27001** — information security management system certification
* **SOC 2 Type II** — operational effectiveness of security controls over a 6-12 month observation period

**What the compliance work involves:**

* Documenting the security controls described in Section 6.5 as formal policies
* Implementing the operational controls (access management, change management, incident response, business continuity) that the engineering work doesn't directly produce
* Selecting a certified audit firm and beginning the audit engagement
* Producing evidence of control effectiveness through the audit window
* Customer-facing attestation reports

**Sequencing:** the compliance work starts during Phase 0.5 (when organisation tenancy is established) and proceeds in parallel with all engineering phases. The first certifications are expected after Phase 8 completes (engineering parity with the architecture), with the SOC 2 Type II audit window extending past Phase 8 by the auditor's required observation period.

**Self-hosted customers do not require this work** — they operate their own deployment and their own compliance posture. Cloud customers receive the certifications as evidence of Oraclous-the-company's operational commitments.

---

## Migration principles

A few principles thread through all phases:

### Production features keep working

Every customer-facing capability that works today must work through the migration. Chat (already production-grade), agent CRUD, ingestion, retrieval, published agents, integration keys, multi-tenant isolation — none of these can break.

This is achieved by: **lift and extend, never rewrite**. Code that moves is the same code, in a new home. New behaviour is added; old behaviour is preserved. The OHM descriptors wrap existing implementations rather than replacing them.

### Security continuity

The existing security defences (multi-tenant isolation tests, Cypher injection prevention, ID enumeration defence, RLS policies on chat, decompression bomb protection, secrets baseline) move with their code. Each migration phase includes a security test pass that re-runs the existing adversarial tests against the new service layout.

If a security defence cannot be preserved through a migration phase, the phase is paused until the defence is reimplemented. This is non-negotiable.

### Tests move with code

Every service that ships with tests today (and all of them do) keeps those tests through migration. When code moves from service A to service B, its tests move too. New tests are added for new behaviour, but no existing test is dropped without explicit justification.

### Each phase ships independently

Phases are sequenced for dependency order, but each ends with the platform in a working state. If Phase 4 ships and Phase 5 is delayed, the platform still works — it just doesn't yet have HITL and round-tables. This makes the plan resilient to real-world disruption.

### Decisions are reversible until committed

The plan above is a target. As phases run, real-world feedback will identify mistakes — boundaries that need adjusting, modules that belong somewhere else, decisions that need revisiting. The architecture document is the contract, but it is a living contract. Each phase ends with a retrospective and the document gets updates where needed.

### Architectural debt is named, not accumulated

When a phase's reality differs from the document's plan, the difference is named explicitly. Either the code is brought to match the doc, or the doc is updated to reflect the new direction. Silent drift is the failure mode the document exists to prevent.

---

## What does NOT move

To make the plan honest, here is what stays where it is, by deliberate choice:

**The Neo4j database itself stays at the foundation.** The substrate is Neo4j + Postgres + Redis; no migration changes this. Schemas evolve; the database technology does not.

**The credential broker's encryption model stays.** It is production-grade; no reason to touch it.

**The chat persistence model (Postgres with RLS) stays as the storage model for member-scoped conversational data.** It moves services (from KG builder to gateway) but the schema and security model stay.

**Multi-tenant isolation enforcement (**`graph_id` on every query, parameterised Cypher, RLS) stays as the universal pattern. Every migration preserves it.

**The auth-service's principal-type model (user, service account, agent) stays.** It is the right shape; we extend it for delegated identity, but we don't replace it.

**Existing customer-registered tools stay registered.** No migration deletes customer data or breaks customer integrations.

---

## Risks and mitigations

The honest risk register:

### Risk 1: Migration takes longer than planned

**Mitigation:** Each phase is independently shippable. If Phase N takes twice the estimate, the platform is still in a working state at the end of Phase N-1. The architecture is designed to tolerate slow migration; it does not require completion in any specific timeframe.

### Risk 2: A migration phase breaks production

**Mitigation:** Lift-and-extend pattern preserves existing behaviour by default. Every phase ships with a regression test pass against existing customer-facing APIs. If a regression is detected, the phase is rolled back; the architecture's clean service boundaries make rollback mechanically possible.

### Risk 3: The compiler harness (Phase 7) is harder than estimated

**Mitigation:** The compiler is the most novel thing in the platform. It is also the only piece that can be iteratively improved without architecture changes — because it is itself a harness. A "v1 compiler" that does limited topology generation is acceptable; iteration follows. The platform ships before the compiler is excellent.

### Risk 4: Multi-modal expansion happens before the architecture is ready

**Mitigation:** The multi-modal commitment is explicit (Section 3): additive, substrate-internal, no architecture change. If a customer needs image ingestion before Phase 9, it can be added to the build side and the retriever side without touching the layers above.

### Risk 5: The OHM format proves inadequate

**Mitigation:** OHM is the canonical hub; if it proves inadequate, OHM v2 is published. The format is versioned (`ohm: 1`). Adapters can target multiple versions. The risk is real but bounded: the format is small enough that revisions are tractable.

### Risk 6: Customer adoption requires changes to the document

**Mitigation:** This is the expected outcome. The document is the v1 architecture; customer feedback drives v2. Sections 5-7 in particular are the most likely to need iteration based on real-world usage. The recursion principle and the platform-as-code/actors-as-harnesses commitment are the foundational claims; everything else is revisable.

---

## The bottom line

The current Oraclous codebase has production-grade ingredients that need to be reorganised, not rewritten. The biggest single migration is decomposing `knowledge-graph-builder`. The biggest conceptual shift is retiring the workflow concept in favour of the harness model. The biggest piece of new work is the compiler harness — but as a harness, not a platform component.

The plan above is sequenced to preserve production through every phase, to honor security continuity, and to leave the platform in a working state at each phase boundary. It is a plan a small team can execute; it does not require simultaneous coordination across all services.

The platform that emerges at the end of Phase 7 is what the architecture in Sections 1-7 describes. Phase 8 hardens it; Phase 9 evolves it.

This section is the contract between the architecture and the engineering work. When implementation questions arise during a phase, the answer should be derivable from this document. Where it is not, the document needs updating before implementation proceeds.
