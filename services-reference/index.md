---
source_page_id: 786433
title: "04. Services Reference"
---

# 04. Services Reference

This hub indexes one reference page per target service. Each page documents purpose, responsibilities, dependencies, and status against the migration plan. These are stable reference documents that update as services evolve through the migration phases.

## Layer 1 — Substrate

* [auth-service](https://oraclous.atlassian.net/wiki/spaces/OP/pages/622756) (port 8000) — identity authority; users, service accounts, agents, delegated identity
* [credential-broker-service](https://oraclous.atlassian.net/wiki/spaces/OP/pages/753812) (port 8002) — encrypted credential storage, OAuth, BYOM provider credentials
* [knowledge-graph-service](https://oraclous.atlassian.net/wiki/spaces/OP/pages/753832) (port 8003) — ingestion, ReBAC graph, schema, analytics, provenance writes
* [knowledge-retriever-service](https://oraclous.atlassian.net/wiki/spaces/OP/pages/622776) (port 8006) — read-side queries with uniform NodeResult envelope

## Layer 2 — Capability Registry

* [capability-registry-service](https://oraclous.atlassian.net/wiki/spaces/OP/pages/884757) (port 8001) — unified descriptors for tools, skills, agents, harnesses, human roles

## Layer 3 — Harness Runtime + Execution Engine

* [harness-runtime-service](https://oraclous.atlassian.net/wiki/spaces/OP/pages/688350) (port 8004) — AgentExecutor, actor dispatch, policy envelope, HITL, round-tables
* [execution-engine-service](https://oraclous.atlassian.net/wiki/spaces/OP/pages/884777) (port 8005) — durable execution, schedule firing, job tracking, task board state

## Layer 4 — Application Gateway

* [application-gateway-service](https://oraclous.atlassian.net/wiki/spaces/OP/pages/131124) (port 8007) — public REST, MCP server + client, chat APIs, published agents, webhooks

## Cross-service patterns

A few patterns thread through all services:

* **Multi-tenant isolation** — every service includes `organization_id` and (where relevant) `graph_id` in every query. The pattern is uniform; the enforcement is layered.
* **ReBAC checks** — every access decision routes through the substrate's ReBAC graph. No service makes authorisation decisions independently.
* **Provenance write-through** — every action records to provenance. The collector lives in the harness runtime; the storage lives in the knowledge graph substrate.
* **Capability resolution** — every capability invocation goes through the registry. There is no path that bypasses descriptor lookup.
* **Credential resolution** — every secret use goes through the broker. Services never cache, log, or transmit credentials.

## How these pages relate to the architecture

Each service page is a _reference_ document for an architectural commitment. The architecture document (Sections 1-9) and the ADRs say _what_ and _why_; these pages document _where each responsibility lives in the target service set_.

When a service grows new responsibilities or absorbs existing ones, its reference page updates. When the architecture changes (via ADR or document revision), the service pages update to reflect.

## Status legend

* **Production-grade** — exists and is working in the current codebase, with appropriate test coverage
* **Production-grade (extension pending)** — exists; the next migration phase adds specific capabilities
* **NEW in Phase N** — does not yet exist; the named phase creates it
* **Evolved from X** — exists as another service today, becomes the named service through a migration phase
* **Renamed from X** — same code, different name and possibly different scope after a migration phase
