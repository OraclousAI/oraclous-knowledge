# Section 3 — Layered Architecture

## Foundational principles

### Principle 1: Platform-as-code, actors-as-harnesses

The platform is divided between **machinery** (code) and **behaviour** (harnesses). Code enforces governance, executes deterministically, persists state. Harnesses reason, act on goals, adapt to context.

### Principle 2: Defaults plus customisation, all the way down

Every customer-facing behaviour follows: the platform ships a **default** that works out of the box; the default is composed from the same primitives customers have access to; customers can **replace, customise, or augment** any default.

## Layer 1: Substrate

The **trust root**. Owns: organisations, workspaces, identity, ReBAC graph, knowledge graphs, credentials, LLM provider configs, audit, metering, task boards, harness manifests, consciousness records.

Organisation isolation: every storage primitive carries an `organization_id`. Every query includes it as a non-negotiable filter. Cross-organisation traversal is **structurally impossible**.

## Layer 2: Capability Registry

The **single source of truth** for what can be invoked in a workspace. Owns capability descriptors, schemas, natural-language descriptions, credential requirements, workspace scoping, versioning.

## Layer 3: Harness Runtime + Execution Engine

The **executor**. The Runtime executes harnesses, dispatches actors, enforces policies. The Execution Engine owns: schedules, long-running jobs, checkpoints, retries, task board state.

## Layer 4: Application Gateway

The **public-facing surface**. Owns: external APIs (REST, MCP, WebSocket), published agents, embeddable widgets, member-facing UIs, webhook receivers, MCP server + client, Billing Service (cloud mode only).

## Layer dependency summary

| Layer | Depends on | Exposes to |
| --- | --- | --- |
| Substrate | (infrastructure only) | All other layers |
| Capability Registry | Substrate | Runtime, Gateway |
| Runtime + Execution Engine | Substrate, Registry | Gateway, harnesses |
| Application Gateway | All three below | External world, members |
