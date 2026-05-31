---
confluence_id: "65967"
title: "Section 3 — Layered Architecture"
---

# Section 3 — Layered Architecture

**Related structured artifacts:** the four-layer split that this section formalises is the founding architectural decision recorded in [ADR-001 — Four-Layer Architecture](https://oraclous.atlassian.net/wiki/spaces/OP/pages/753752). The Substrate stores manifests in the format defined by [OHM v1.0 Standalone Specification](https://oraclous.atlassian.net/wiki/spaces/OP/pages/393501); the Substrate and Runtime together enforce the policy sets defined in [Structured Governance Taxonomy](https://oraclous.atlassian.net/wiki/spaces/OP/pages/688439); the organisation-isolation guarantees described under Layer 1 defend against threats T1 (data exfiltration), T6 (operator-separation breach), and T10.x (cloud-mode attacks) in [Structured Threat Catalogue](https://oraclous.atlassian.net/wiki/spaces/OP/pages/983129).

This section is authoritative for what each layer owns; the artifacts are authoritative for the implementation contracts each layer must satisfy.

This section details each of the four platform layers: what it owns, what primitives it exposes, what it depends on, what is explicitly _not_ its job, and where customers can extend or replace parts of it.

Before the layers themselves, two foundational design principles need to be made explicit. These principles are referenced throughout the rest of the document and govern every architectural decision downstream.

## Foundational principles

### Principle 1: Platform-as-code, actors-as-harnesses

The platform is divided cleanly between **machinery** (code) and **behaviour** (harnesses). Code is the part that:

* Enforces governance (ReBAC, credentials, policies)
* Executes deterministically (runtime loop, tool dispatch, schedule firing)
* Persists state (substrate, registry, task boards, provenance)
* Exposes primitives (API, MCP, manifest format)

Harnesses are the part that:

* Reasons (planning, routing, evaluation)
* Acts on goals (compiling, executing work, recording observations)
* Adapts to context (per-workspace, per-customer, per-domain)
* Can be replaced or customised without changing platform code

This division has a concrete consequence: **anything that requires intelligence is a harness, not a platform layer.** The compiler, consciousness agents, self-modification agents, the harness review system, end-user applications — none of these are platform code. All of them are harnesses running on the same runtime any customer harness uses.

The platform exposes primitives. Harnesses compose them.

### Principle 2: Defaults plus customisation, all the way down

Every customer-facing piece of platform behaviour follows the same pattern:

* The platform ships a **default** that works out of the box
* The default is itself composed from the same primitives customers have access to
* Customers can **replace, customise, or augment** any default through those same primitives

This is not just a product principle — it is an **architectural constraint**. There can be no "platform magic" that customers cannot reach. The default compiler is a harness customers can inspect, fork, and modify. The default consciousness pattern is a skill customers can swap. The default cross-workspace federation is a configuration customers can change.

This principle is what makes the platform a _substrate_ rather than a _product_. Customers do not consume Oraclous's opinions; they inherit Oraclous's defaults and choose which to keep.

---

## Layer 1: Substrate

The Substrate is the **trust root** of the platform. It owns all state that requires governance.

### What the Substrate owns

* **Organisations** — the outermost tenancy unit, the boundary that separates customers from each other
* **Workspaces** — the primary working unit nested inside organisations, hierarchical, with isolation enforced by ReBAC
* **Identity** — humans (members) and agents, both first-class, with their own credentials
* **ReBAC graph** — relationships between members, agents, workspaces, and resources; the source of truth for access decisions
* **Knowledge graphs** — per-workspace data, with `organization_id` AND `graph_id` scoping enforced on every query
* **Credentials** — OAuth tokens, API keys, secrets (including LLM provider credentials), with scoped delegation between members and agents
* **LLM provider configurations** — organisation, workspace, and agent-level provider/model selections with three-level resolution
* **Audit and provenance** — every action recorded with who, on whose behalf, against what, under what scope, with what result
* **Metering** — substrate-level tracking of resource consumption (tokens, invocations, storage, time) per organisation and workspace
* **Task boards** — persistent operational state, shared between humans and agents
* **Harness manifests** — committed versions, with full history
* **Consciousness records** — agents' experiential memory, scoped per agent or per team

### What the Substrate exposes

* **Access decision API** — "can this actor do this action against this resource?" — used by every other layer
* **Credential resolution API** — "give me a token for this actor to access this provider, with these scopes"
* **Workspace traversal API** — "as this actor, give me the effective set of workspaces I can read or act in"
* **Provenance write API** — every other layer writes audit entries here, never anywhere else
* **Storage APIs** — for knowledge graphs, task boards, manifests, consciousness records

### What the Substrate does NOT do

* It does not execute harnesses
* It does not dispatch tools or run agents
* It does not interpret prose or plan topologies
* It does not enforce _application-level_ policies (only platform-level access)
* It does not know what a _harness_ is in operational terms — only as a stored artifact

### What the Substrate depends on

Nothing else in the platform. The Substrate is the bottom of the stack. It depends on infrastructure (Neo4j, Postgres, secret stores) but not on other Oraclous layers.

### Customisation surface

The Substrate is the _least_ customisable layer by design — it is the trust root and must be predictable. Customers can extend it in these specific ways:

* Add custom **knowledge graph schemas** per workspace
* Define custom **ReBAC relationships** beyond the defaults
* Configure **policy templates** that other layers reference
* Plug in alternative **identity providers** for member authentication

Customers cannot replace the Substrate. It is the one layer that is genuinely fixed.

### Organisation-level isolation

The Substrate enforces organisation isolation as the **outermost boundary** in both self-hosted and cloud-hosted deployment modes. The architectural pattern:

* Every storage primitive (Neo4j nodes, Postgres rows, Redis keys, cache entries, search indexes) carries an `organization_id` alongside any inner scope
* Every query — read, write, traversal, search — includes `organization_id` as a non-negotiable filter
* Cross-organisation traversal is **structurally impossible**: no API exposes it, no Cypher pattern permits it, no internal service bypasses it
* Multi-tenant components (already present in the codebase as `MultiTenantVectorRetriever`, `MultiTenantHybridRetriever`, `MultiTenantVectorCypherRetriever`) extend to include organisation scoping at the outermost layer

In self-hosted mode, most deployments have a single organisation. In cloud-hosted mode, the same Neo4j cluster, Postgres database, and Redis instance hosts many organisations, each fully isolated. The code is the same; only the operational deployment differs.

This isolation is **the substrate's most important guarantee** in cloud mode. It is what makes cloud deployment compatible with ISO 27001 and SOC 2 Type II compliance. The isolation tests in the existing codebase (`test_multi_tenant_isolation.py`) extend to cover the organisation boundary; nothing about the substrate's data model changes architecturally.

### Multi-modal substrate commitments

The Substrate stores and retrieves multiple data modalities. The current scope is the inherited foundation; future modalities will be added without architectural rework.

**Currently supported modalities:**

* **Text** — natural language documents, plain text, transcripts. Stored as Chunk nodes with vector embeddings; retrievable via semantic, full-text, and hybrid search.
* **Documents** — PDFs, DOCX, structured files. Ingested through parsers that extract text and document structure; the text becomes searchable while document structure (sections, tables, references) is preserved in the graph.
* **Structured data** — relational data, CSV, JSON. Ingested with schema preservation; queryable via Cypher patterns that mirror the original structure.
* **Code** — source code from repositories. Stored with semantic chunking, language-aware tokenisation, and graph relationships representing imports, calls, and inheritance.
* **Temporal data** — time-series records, event logs, bitemporal data (valid time + transaction time). Stored with explicit `valid_from`, `valid_to`, and `transaction_time` properties; queryable through temporal filters.

**Modalities that are additive, not yet implemented:**

* **Images** — perceptual embeddings for visual similarity, OCR-extracted text for hybrid search
* **Audio** — transcription pipeline producing text chunks, plus acoustic embeddings for non-textual matching
* **Video** — frame-based perceptual embeddings, transcription, scene segmentation
* **Design files** — Figma, Sketch, CAD — structural extraction with semantic annotations
* **3D and spatial data** — point clouds, meshes, scene graphs with geometric indexing

**Architectural commitment:** every modality is stored as **nodes in the knowledge graph** with **modality-appropriate indexes** (vector, full-text, geometric, temporal) and **uniform ReBAC enforcement**. The Retriever exposes modality-appropriate retrieval shapes (`semantic_search`, `temporal_slice`, `perceptual_match`) but they all return the same `NodeResult` envelope. The Capability Registry treats all modalities uniformly — a capability that consumes "documents" doesn't need to know whether the underlying source was a PDF or a transcript.

This commitment means **adding a new modality is a substrate-internal change**, not an architecture change. It requires a new parser, a new index type, a new retrieval shape — but the four layers, the OHM format, and the governance model remain unchanged. New modalities ride on the existing rails.

The Retriever (covered briefly in Layer 1 below and in more detail in Section 8) is the layer where modality-appropriate retrieval converges into a uniform result type. This is what makes the multi-modal commitment honest: actors don't reason about modality at the harness level; the substrate handles it.

---

## Layer 2: Capability Registry

The Capability Registry is the **single source of truth for what can be invoked** in a workspace. It is the layer that collapses today's scattered tool registries into one coherent inventory.

### What the Registry owns

* **Capability descriptors** for all five kinds: tools, skills, agents, harnesses, human roles
* **Per-capability schemas** — structured input/output contracts for runtime use
* **Per-capability natural-language descriptions** — what each capability is good for, written for LLM consumers (especially the compiler)
* **Credential requirements** per capability — what scopes are needed to invoke it
* **Workspace scoping** — which capabilities are visible to which workspaces
* **Versioning** — capabilities evolve; the registry tracks versions and compatibility

### What the Registry exposes

* **Capability discovery API** — "what capabilities are available to this actor in this workspace?" — ReBAC-bounded by Substrate
* **Capability resolution API** — "give me the executable handle for capability X, version Y"
* **Capability registration API** — register a new tool, skill, agent, harness, or human role
* **Adapter API** — import/export capabilities to/from external formats (Claude Code skills, MCP tools, Codex definitions)

### What the Registry does NOT do

* It does not execute capabilities — that is the Runtime's job
* It does not decide who can use what — that is the Substrate's ReBAC job
* It does not store harness _runtime state_ — only the capability's descriptor

### What the Registry depends on

* The Substrate, for access control and workspace scoping

### The unified capability model

Every capability — regardless of kind — has the same descriptor shape:

* A **kind** (tool, skill, agent, harness, human_role)
* A **structured schema** for runtime invocation
* A **natural-language description** for compiler reasoning
* A **credential requirement** list
* A **workspace scope** specification
* An **invocation handle** that resolves to the appropriate runtime mechanism

This uniformity is what makes harnesses portable: when the compiler plans a topology, it does not need to know whether _"draft the email"_ will be done by a tool, a skill-loaded agent, a human role, or a sub-harness. The decision is a routing concern, not a planning concern.

### Customisation surface

This layer is highly customisable. Customers can:

* Register new capabilities of any kind
* Write custom adapters for external capability sources
* Override default capability descriptions to fit their domain language
* Scope capabilities to specific workspaces or workspace branches
* Version capabilities and manage migration policies

---

## Layer 3: Harness Runtime + Execution Engine

The Runtime is the **executor** of the platform. It is what turns manifests into running work.

This layer must be powerful enough to host the default compiler, consciousness agents, and self-modification agents as harnesses from day one. It cannot ship as a thin runtime with platform-specific code paths for those components.

### What the Runtime owns

* **Harness execution** — loading a manifest and driving its orchestration
* **Actor dispatch** — routing each step to the right actor (tool, agent, human, sub-harness)
* **Multi-actor coordination** — hand-offs, escalations, dependencies
* **Conversation and working memory** — within a single execution context
* **Policy envelope enforcement** — budget caps, HITL gates, output redaction, scope limits
* **Workspace traversal** — moving across workspaces under delegated identity (federation pattern as default)
* **Tool-use loop** — the model → tool → model iteration for agents

The Execution Engine sits underneath, owning:

* **Schedules and triggers** — cron, events, webhooks, manual
* **Long-running jobs** — work that outlives a single request
* **Checkpoints and resumability** — state persisted across pauses and restarts
* **Retries and failure handling** — with policy-bounded retry counts
* **Task board state** — pushing tasks to humans, receiving completions
* **Sub-harness invocation** — when an agent's harness includes another harness as a capability

### What the Runtime exposes

* **Harness execution API** — start, pause, resume, cancel a harness run
* **Capability dispatch API** — invoke a single capability with input, get a result (used by harnesses internally and by external callers)
* **Task board API** — read tasks, assign, claim, complete, escalate
* **Streaming API** — Server-Sent Events for in-progress harness output (chat-like or operational)
* **Provenance write-through** — every execution decision lands in the Substrate's audit trail

### What the Runtime does NOT do

* It does not compile manifests — that is a harness running on the Runtime
* It does not record consciousness — that is also a harness or skill
* It does not propose harness mutations — also a harness
* It does not author harnesses — humans and the compiler do
* It does not store committed harnesses — the Substrate does

### What the Runtime depends on

* The Substrate, for access decisions, credential resolution, provenance, and task board persistence
* The Capability Registry, for resolving what to invoke

### The two operational modes

The Runtime operates in two modes that share most of their machinery but differ in lifecycle:

**Synchronous mode** — a harness runs inside a single request. A chat turn, a quick task. The harness completes (or aborts) before the request returns. Uses the Runtime directly.

**Durable mode** — a harness runs across many wake-ups. Scheduled agents, long-running jobs, work that waits on human task completion. Uses the Execution Engine for state persistence between activations.

The same harness can run in either mode depending on how it is triggered. The Runtime decides based on the trigger and the harness's declared characteristics.

### Customisation surface

The Runtime itself is platform code and is not directly customisable. Customers customise _behaviour on the Runtime_ by writing harnesses. Specifically:

* All orchestration logic lives in harnesses, not in the Runtime
* All planning logic lives in harnesses
* All learning and adaptation logic lives in harnesses (consciousness)
* All harness modification logic lives in harnesses (self-modification)

The Runtime exposes the primitives; harnesses compose them.

---

## Layer 4: Application Gateway

The Application Gateway is the **public-facing surface** of the platform. It mediates everything between the outside world and the platform's internals.

### What the Gateway owns

* **External APIs** — REST, MCP, WebSocket — for harnesses to be invoked from outside
* **Published agents and harnesses** — making a workspace's capabilities available externally with rate limits, integration keys, and CORS scoping
* **Embeddable widgets** — the surface for putting Oraclous-powered agents into customer applications
* **Member-facing UIs** — task board views, harness review, manifest editing, consciousness inspection
* **Webhook receivers** — for external triggers (Git pushes, calendar events, third-party integrations)
* **MCP server endpoint** — exposing the platform's capabilities to external MCP clients (Claude Code, Cursor, etc.)
* **MCP client integrations** — letting harnesses consume capabilities from external MCP servers
* **Billing Service (cloud mode only)** — consumes metering data from the Substrate, applies pricing rules, generates invoices, manages payment relationships. In self-hosted mode, this service is not deployed; the metering surface is exposed to the customer for their own use.
* **Usage reporting API** — exposes metering data to organisation admins in both deployment modes (cloud customers see this alongside their invoices; self-hosted customers use it for internal chargeback or analytics)

### What the Gateway exposes

* The full external API surface
* The member application surface (task boards, harness editor, etc.)
* The bridge to external runtimes (Claude Code, Codex, others)

### What the Gateway does NOT do

* It does not execute harnesses — it delegates to the Runtime
* It does not store anything — it delegates to the Substrate
* It does not decide what is available — it delegates to the Registry and ReBAC

### What the Gateway depends on

All three layers below it. The Gateway is the orchestrator of external access but owns no domain state.

### Customisation surface

The Gateway is highly customisable. Customers can:

* Build their own member UIs against the Gateway's APIs
* Build their own external applications consuming workspaces
* Write custom MCP adapters
* Configure rate limits, CORS, and access policies per published harness
* Replace the default task board UI with a domain-specific one

---

## The bootstrap problem

Because the platform is recursive — the compiler is a harness, the consciousness system is a harness — there is a real bootstrap question: how does a workspace come up with no harnesses installed, when the harness that installs harnesses is itself a harness?

The platform resolves this with a **seeded default workspace template**. When a new workspace is created, the Substrate ships it with:

* A **default capability inventory** — the standard tools (knowledge graph operations, basic file readers, web fetch, etc.) and the standard skills (planning, summarisation, evaluation)
* A **default compiler harness** — pre-installed, with pre-allocated capabilities
* A **default consciousness pattern** — the skill-per-agent variant, with a coded default skill
* A **default policy envelope** — sensible budget caps, HITL on harness modification, etc.
* A **default task board** — empty but ready to receive

These defaults are themselves expressed as manifests, stored in the Substrate, and committed as the workspace's initial state. They are not platform code — they are _seed data_. Customers can immediately modify them; the platform never assumes they remain in their default state.

This is the recursion bottom: the platform ships **manifest templates as seed data**, and the Runtime can execute them from the first moment a workspace exists.

---

## Cross-layer concerns

A few concerns cut across layers and deserve explicit treatment:

### Multi-tenant isolation

Enforced primarily at the Substrate via `graph_id` and ReBAC, with every other layer required to route through Substrate's access decision API before acting. No layer is permitted to access cross-tenant data directly. The Runtime in particular must call the Substrate to resolve "what workspaces can this actor see" — never bypass it.

### Provenance

Every layer writes provenance entries through the Substrate. The Substrate is the single sink. This means an audit trail of a single harness run will include entries from the Runtime (each turn, each tool call), the Registry (each capability resolution), and the Gateway (the inbound trigger) — all anchored to the same execution context in the Substrate.

### Policy enforcement

The Substrate enforces _access_ policies (ReBAC, credentials). The Runtime enforces _operational_ policies (budgets, HITL, output redaction). The Gateway enforces _exposure_ policies (rate limits, CORS, integration key scopes). Policies declared in a harness manifest get routed to whichever layer is responsible for enforcing each kind.

### Portability

The Manifest format is the portability contract. Imports and exports happen at the Capability Registry (for individual capabilities) and at the Substrate (for committed harnesses). Adapters for external formats (Claude Code skills, Codex definitions, MCP servers) are themselves capabilities, written as tools or skills, and registered in the Registry. The platform's own _internal_ format is canonical; external formats are translated through adapters.

---

## Layer dependency summary

| Layer | Depends on | Exposes to |
| --- | --- | --- |
| Substrate | (infrastructure only) | All other layers |
| Capability Registry | Substrate | Runtime, Gateway |
| Runtime + Execution Engine | Substrate, Registry | Gateway, harnesses |
| Application Gateway | All three below | External world, members |

Harnesses (compiler, consciousness, applications, customer harnesses) all run on the Runtime and consume capabilities from the Registry. They are not part of the layer stack; they are _what the stack exists to run_.
