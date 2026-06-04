---
confluence_id: "786433"
title: "04. Services Reference"
---

# 04. Services Reference

This hub indexes one reference page per target service. Each page documents purpose, responsibilities, dependencies, and status against the migration plan. These are stable reference documents that update as services evolve.

**R3.5 reality (ORAA-4 §R3.5):** R2/R3 shipped most substrate services **hollow** — stub endpoints, `raise NotImplementedError`, a `GraphNodeService` class defined *inside* a route file, and ~6,300 LOC of real-but-dead logic still sitting in `oraclous-core-service`. R3.5 rebuilds every service **REAL, end-to-end, per service**, in a graph-first order, with Reza personally testing and signing off each before the next dependent one starts. The page Status lines below state the **honest current reality** and the **R3.5 target**. There is **no application gateway yet** — until it is built last, services are reached **directly by host IP:port** (legacy parity).

**R3.5 per-service order:** (1) [knowledge-graph-service](knowledge-graph-service.md) → (2) [knowledge-retriever-service](knowledge-retriever-service.md) → (3) [identity-org-service](identity-org-service.md) → (4) [credential-broker-service](credential-broker-service.md) → (5) [capability-registry-service](capability-registry-service.md) → (6) [application-gateway-service](application-gateway-service.md).

## Layer 1 — Substrate

* [knowledge-graph-service](knowledge-graph-service.md) (port 8003) — **hollow today; R3.5 step 1** rebuilds real recipe/primitive/unified-graph ingestion (text/PDF/DOCX/MD/CSV/JSON/code/temporal) per ADR-022. Orgs leave this service in step 3.
* [knowledge-retriever-service](knowledge-retriever-service.md) (port 8006) — **hollow today; R3.5 step 2** rebuilds real semantic/full-text/hybrid/graph/temporal retrieval + chat, uniform `NodeResult` envelope.
* [identity-org-service](identity-org-service.md) — **NEW in R3.5 step 3.** Human identity (email/password/verify/reset, OAuth Google/GitHub/Notion, JWT) + orgs/members/roles/invitations/subgraph-grants. Ported from legacy `auth-service` + org-mgmt buried in `knowledge-graph-builder`.
* [auth-service](auth-service.md) (port 8000) — **agent-only today.** Becomes the machine-identity service (agents, service accounts); human auth moves to [identity-org-service](identity-org-service.md).
* [credential-broker-service](credential-broker-service.md) (port 8002) — **R3.5 step 4:** AES-256-GCM encrypted credential store + runtime OAuth token resolution.

## Layer 2 — Capability Registry

* [capability-registry-service](capability-registry-service.md) (port 8001) — **136-LOC empty shell today; R3.5 step 5** ports the real tool registry + execution + connectors from `oraclous-core-service` (then salvage-then-delete it, human-gated).

## Layer 3 — Harness Runtime + Execution Engine

* [harness-runtime-service](https://oraclous.atlassian.net/wiki/spaces/OP/pages/688350) (port 8004) — AgentExecutor, actor dispatch, policy envelope, HITL, round-tables
* [execution-engine-service](https://oraclous.atlassian.net/wiki/spaces/OP/pages/884777) (port 8005) — durable execution, schedule firing, job tracking, task board state

## Layer 4 — Application Gateway

* [application-gateway-service](application-gateway-service.md) (port 8007) — **placeholder; built last (R3.5 step 6).** Public REST, MCP server + client, chat APIs, published agents, webhooks. Until it exists, services are reached directly by host IP:port.

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

* **Hollow today** — a PR merged with a stub/shell (stub endpoints, `NotImplementedError`, an empty LOC shell); it is **not** done. R3.5 rebuilds it real. "Merged PR + green stub-tests" satisfies none of the ORAA-4 §22 gates.
* **NEW in R3.5** — does not yet exist; R3.5 creates it.
* **Agent-only today** — the service exists but only covers machine principals; its human surface was dropped and lands elsewhere in R3.5.
* **Placeholder; built last** — defined but not built; the final R3.5 step.
* **Done (ORAA-4 §22)** — all 8 gates pass: structurally conformant, not hollow, runs, real endpoints, end-to-end smoke vs real substrate, and Reza-signed-off. No service is done while it carries `needs-human`.

A service is rebuilt REAL only when Reza personally tests it and signs off (ORAA-4 §22 gate 6); the next dependent service does not start until then.
