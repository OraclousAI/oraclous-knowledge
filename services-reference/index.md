---
confluence_id: "786433"
title: "04. Services Reference"
---

# 04. Services Reference

This hub indexes one reference page per service. Each page documents purpose, responsibilities, dependencies, and status. These are stable reference documents that update as services evolve.

**R3.5 is complete (ORAA-4 §R3.5).** R2/R3 had shipped most substrate services **hollow** — stub endpoints, `raise NotImplementedError`, a `GraphNodeService` class defined *inside* a route file, and ~6,300 LOC of real-but-dead logic in `oraclous-core-service`. R3.5 **rebuilt all six services REAL, end-to-end, per service**, in a graph-first order, with Reza personally testing and signing off each. All six carry `claimed_done: true` (the no-stub checker now fails CI on any regression). `oraclous-core-service` was salvaged-then-deleted (§15, Reza-approved). See the [R3.5 retrospective](../releases/r3.5-retrospective.md). There is **no application gateway fronting traffic in production yet** — the gateway exists as a reverse-proxy edge; until it is the sole ingress (R6), services are also reachable **directly by host IP:port**.

**As-built order (per-service, graph-first):** (1) [knowledge-graph-service](knowledge-graph-service.md) → (2) [knowledge-retriever-service](knowledge-retriever-service.md) → (3) [auth-service](auth-service.md) (the single identity service) → (4) [credential-broker-service](credential-broker-service.md) → (5) [capability-registry-service](capability-registry-service.md) → (6) [application-gateway-service](application-gateway-service.md). The planned separate `identity-org-service` (ADR-017) was **not** built — identity was consolidated into `auth-service` (see [tombstone](identity-org-service.md)).

## Layer 1 — Substrate

* [knowledge-graph-service](knowledge-graph-service.md) (port 8003) — **Real (R3.5-complete).** Graph CRUD + recipe-driven ingestion (text/PDF/DOCX/MD/CSV/JSON/code) into the unified graph (ADR-022) + ontology + jobs. Org/member management left this service. Heavy analytics (community/centrality) deferred.
* [knowledge-retriever-service](knowledge-retriever-service.md) (port 8004) — **Real (R3.5-complete).** Semantic/full-text/hybrid/graph retrieval, uniform `NodeResult` envelope. Chat + temporal-slice + dedicated query-cache deferred.
* [auth-service](auth-service.md) (port 8005) — **Real (R3.5-complete).** The single **identity authority**: human users (email/password + OAuth Google/GitHub/Notion), orgs/members/invitations, and machine principals (agents, service accounts). Consolidates what ADR-017 had planned as a separate identity-org-service.
* [credential-broker-service](credential-broker-service.md) (port 8002) — **Real (R3.5-complete).** AES-256-GCM encrypted credential store + runtime OAuth token resolution + delegated tokens. (External KMS is the ADR-008 cloud-mode posture, later.)

## Layer 2 — Capability Registry

* [capability-registry-service](capability-registry-service.md) (port 8001) — **Real (R3.5-complete).** Unified registry + **synchronous** tool execution with real connectors (PostgreSQL/MySQL/Notion/GitHub) and a credential bridge to the broker. Ported from `oraclous-core-service`, which was then deleted (§15, human-gated). Async/streaming execution is the R5 execution-engine.

## Layer 3 — Harness Runtime + Execution Engine (deferred scaffolds)

* [harness-runtime-service](https://oraclous.atlassian.net/wiki/spaces/OP/pages/688350) — **R4-deferred scaffold** (README + pyproject only; not wired into compose; `claimed_done: false`). AgentExecutor, actor dispatch, policy envelope, HITL, round-tables.
* [execution-engine-service](https://oraclous.atlassian.net/wiki/spaces/OP/pages/884777) — **R5-deferred scaffold** (README + pyproject only; not wired into compose; `claimed_done: false`). Durable/async execution, schedule firing, job tracking, task-board state, SSE streaming.

## Layer 4 — Application Gateway

* [application-gateway-service](application-gateway-service.md) (port 8006) — **Real (R3.5-complete) as a reverse-proxy edge:** longest-prefix route table → streaming proxy to the five lower services, edge JWT termination + identity forwarding (anti-spoof), CORS, health aggregation; no DB. The richer surface (MCP server/client, chat APIs, published agents, webhooks, rate-limiting, API keys, versioned public OpenAPI, the unified ORA-37 error envelope, sole-ingress) is **R6 hardening — not built yet**.

## Cross-service patterns

A few patterns thread through all services:

* **Multi-tenant isolation** — every service includes `organisation_id` and (where relevant) `graph_id` in every query. The pattern is uniform; the enforcement is layered (every service smoke asserts a cross-org denial).
* **ReBAC checks** — every access decision routes through the substrate's ReBAC graph. No service makes authorisation decisions independently.
* **Provenance write-through** — actions record to provenance; storage lives in the knowledge-graph substrate.
* **Capability resolution** — every capability invocation goes through the registry. There is no path that bypasses descriptor lookup.
* **Credential resolution** — every secret use goes through the broker. Services never cache, log, or transmit credentials.

## How these pages relate to the architecture

Each service page is a _reference_ document for an architectural commitment. The architecture document (Sections 1-9) and the ADRs say _what_ and _why_; these pages document _where each responsibility lives_.

When a service grows new responsibilities or absorbs existing ones, its reference page updates. When the architecture changes (via ADR or document revision), the service pages update to reflect.

## Status legend

* **Real (R3.5-complete)** — all 8 ORAA-4 §22 gates passed: structurally conformant, not hollow (`check_no_stubs` clean, `claimed_done: true`), runs, real endpoints, end-to-end smoke vs real substrate, and Reza-signed-off. The structure + no-stub checkers fail CI on any regression.
* **Deferred scaffold** — a package placeholder (README + pyproject) for a future release (R4/R5); not wired into compose, `claimed_done: false`. Not hollow-claimed-done — it makes no claim to be real.
* **R6 hardening — not built yet** — a real service whose *additional* surface is scheduled for a later release; the page states what is real today vs deferred.
* **Tombstone (superseded)** — a planned service that was not built; its scope landed elsewhere (e.g. [identity-org-service](identity-org-service.md) → [auth-service](auth-service.md)).
