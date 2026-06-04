---
title: "Revised Release Plan: Gateway-from-R5 + FE/BE Vertical Slices"
status: "Draft — pending board approval on ORAA-28"
author: "product-planner"
date: "2026-06-01"
---

# Revised Release Plan: Gateway-from-R5 + FE/BE Vertical Slices

> **SUPERSEDED by [R3.5 — Make every service real](r3.5-make-every-service-real.md) (2026-06-04).** This gateway-from-R5 vertical-slice plan is discarded. R2/R3 shipped hollow; the platform is being rebuilt real, per service, in the graph-first sequence (1) ingest → (2) retrieve → (3) identity/org → (4) credential-broker → (5) capability-registry (then salvage-delete `oraclous-core-service`) → (6) gateway. Content below is retained for reference only.

> **Status:** Draft — see [ORAA-28](/ORAA/issues/ORAA-28) for board approval.  
> This page supersedes the per-release FE notes in r5–r8 once approved.

---

## 1. Locked Decisions

1. **Every release from R5 ships a FE+BE vertical slice** — a usable, shippable product increment. FE features are tracked with the BE endpoints that enable them.
2. **API Gateway incremental from R5:** stand up a thin `application-gateway-service` right after R4 with a versioned/provisional contract. Each release R5→R8 adds its newly-introduced endpoints. R6 becomes gateway consolidation/hardening — not first appearance.
3. **FE asymmetry holds until RF Phase B:** manual review + CI gates (api-client-boundary, no-token-in-storage, axe AA, bundle budget) remain in place. No FE test/review agents until RF Phase B.

---

## 2. Per-Release FE+BE Deliverables

### R0.5 — Organisation Tenancy & Metering Substrate ✅ Done
- **BE only** (FE: none)
- Organisation-ID scoping on all substrate primitives
- Metering substrate (tokens/count/bytes); never USD/credits (ADR-009)
- Usage-reporting aggregation primitive (HTTP endpoint deferred to R6)

### R1 — Auth & Credential Extensions ✅ Done
- **BE only** (FE: none)
- Agent principal type in auth-service
- Delegated identity tokens in credential-broker
- ReBAC delegation relations extracted to `packages/rebac`

### R2 — Capability Registry Consolidation ⚙️ In progress
- **BE only** (FE: RF Phase A runs in parallel)
- `capability-registry-service` extracted from `oraclous-core-service`
- OHM descriptors for all tools; MCP inbound importer
- Content-hash versioning

### R3 — Knowledge Graph Decomposition
- **BE only** (FE: RF Phase A completes)
- `knowledge-graph-service` (write) + `knowledge-retriever-service` (reads/federation)
- Read-only Neo4j role; NodeResult envelope
- ORA-19 B1 API-authz suite lift

### R4 — Harness Runtime Extraction
- **BE + FE-Medium** (agent CRUD surfaces — gateway pivot point)
- `harness-runtime-service` extracted (AgentExecutor + toolkit + LLM services)
- Per-invocation ReBAC recheck (T2-M1)
- Agent-to-agent handoff via task board
- **Gateway:** provisional `application-gateway-service` stands up after R4 with versioned contract shell. RF api-client absorbs contract churn.

### R5 — Execution Engine & Runtime Completion 🔴 FE-Heavy
- **BE:** execution-engine-service extraction; task board + HITL + round-table + schedule APIs; checkpoints & resumability; cross-workspace federation
- **FE:** task-board UI; HITL approval surfaces; round-table UI
- **Gateway endpoints added in R5:**
  - `POST /tasks` — create task
  - `GET /tasks/{id}` — get task
  - `PATCH /tasks/{id}` — update task (claim, complete, handoff)
  - `GET /tasks/{id}/subtasks` — list subtasks
  - `POST /hitl/{id}/approve` — HITL approval action
  - `POST /hitl/{id}/reject` — HITL reject action
  - `GET /roundtable/{id}` — get round-table session
  - `POST /roundtable` — create round-table
  - `POST /schedules` — create schedule (cron)
  - `DELETE /schedules/{id}` — delete schedule

### R6 — Application Gateway Consolidation 🟡 FE-Medium
- **BE:** consolidate all remaining public APIs into gateway; chat APIs; published agents + integration keys; MCP server (ReBAC-gated); MCP client integration; webhooks; embeddable widgets; usage reporting HTTP endpoint
- **FE:** chat UI; published agents UI; integration keys management; embeddable widget surfaces
- **Gateway endpoints added in R6 (consolidation):**
  - `POST /chat/messages` — send chat message
  - `GET /chat/sessions/{id}` — get session
  - `GET /agents/published` — list published agents
  - `POST /agents/{id}/invoke` — invoke published agent
  - `GET /integration-keys` — list integration keys
  - `POST /integration-keys` — create integration key
  - `DELETE /integration-keys/{id}` — revoke key
  - `GET /widgets/{id}` — embeddable widget config
  - `GET /usage` — usage report (org admins)
  - MCP endpoint (multi-auth: integration keys / member / agent credentials)
  - Webhook receiver endpoints

### R7 — Compiler Harness & Seed Manifests 🟢 FE-Light
- **BE:** default compiler harness (planner, surveyor, drafter, reviewer); consciousness skill; agent-MCP server as Capability Registry entry; seed manifests
- **FE:** diff-and-accept UI; performance & polish window
- **Gateway endpoints added in R7:**
  - `GET /agents/{id}/manifest` — get agent manifest
  - `POST /agents/{id}/manifest/review` — submit diff-and-accept decision
  - `GET /capabilities` — list available capabilities (public surface)
  - Agent-MCP server tools: `my_tasks`, `claim_next`, `handoff_to`, `escalate_to_human`, `complete`, `observe`, `review_request`

### R8 — Security Hardening Pass 🔴 FE-Heavy
- **BE:** prompt injection sanitisation; custom output redaction; audit reports; service-account hardening; cache-key isolation; consciousness drift detection; pen-test; KMS-envelope reshape (deferred from R1)
- **FE:** admin redaction-pattern UI; security-event notification surfaces; audit-report views
- **Gateway:** no new endpoints — hardening pass only. Closes T3, T4, T6, T7, T6.2, T9.2.

### RF Phase A — Frontend Foundation ⚙️ In progress (parallel to R2–R4)
- pnpm-workspace monorepo scaffold; CI invariant gates
- `packages/design-system` (tokens + 48 shadcn primitives)
- `packages/api-client` typed contract shell
- `apps/console` app shell (routing, ProtectedRoute, token store)
- No FE test/review agents; manual review + CI gates apply

### R-Compliance — Cloud Mode Compliance Track (parallel post-R8)
- ISO 27001 + SOC 2 Type II; audit firm engagement
- Trust centre; operational controls
- Not ticket-shaped; tracked in compliance subspace

---

## 3. Gateway Incremental Contract — Open Design

> **Delegated to solution-architect** via child issue of ORAA-28.  
> Questions pending design:
> - Versioning scheme: `/v1/` prefix vs. `Accept: application/vnd.oraclous.v1+json` header?
> - How provisional endpoints are marked in the OpenAPI spec (x-stability: provisional)?
> - Contract enforcement mechanism R5→R5 (shared fixture) vs. R6 (OpenAPI diff gate)?
> - Which endpoints live on the MCP surface vs. REST surface vs. both?

---

## 4. Paperclip Model: Goals & Projects

| Release | Paperclip Goal | Status |
|---------|---------------|--------|
| R0.5 | R0.5 — Organisation Tenancy & Metering Substrate | achieved |
| R1 | R1 — Auth & Credential Extensions | achieved |
| R2 | R2 — Capability Registry Consolidation | active |
| R3 | R3 — Knowledge Graph Decomposition | planned |
| R4 | R4 — Harness Runtime Extraction | planned |
| R5 | R5 — Execution Engine & Runtime Completion (FE+BE Slice) | planned |
| R6 | R6 — Application Gateway Consolidation (FE+BE Slice) | planned |
| R7 | R7 — Compiler Harness & Seed Manifests (FE+BE Slice) | planned |
| R8 | R8 — Security Hardening Pass (FE+BE Slice) | planned |
| RF Phase A | RF Phase A — Frontend Foundation | active |
| R-Compliance | R-Compliance — Cloud Mode Compliance Track | planned |

Each Goal has Projects per epic. R5–R8 have explicit BE and FE Projects.

---

## 5. Revision History

| Date | Change | Author | Reason |
|------|--------|--------|--------|
| 2026-06-01 | Initial draft | product-planner (ORAA-28) | Board-approved direction: gateway from R5, FE+BE vertical slices |
