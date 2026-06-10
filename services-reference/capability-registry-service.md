---
confluence_id: "884757"
title: "capability-registry-service"
---

# capability-registry-service

**Layer:** 2 (Capability Registry) · **Port:** 8001 · **Status:** **Real — R3.5-complete, §22-signed-off** (Reza ran both `smoke.sh` and `smoke_real_broker.sh`). The real tool registry + **synchronous** execution was ported from `oraclous-core-service`, which was then salvaged-and-deleted (human-gated, ORAA-4 §15). Reachable directly by host IP:port until the [application-gateway-service](application-gateway-service.md) fronts it.

## What it is now

R3.5 service #5 rebuilt this real, end-to-end. It owns the unified capability registry and **synchronous** tool execution, with real connector dispatch to PostgreSQL, MySQL, Notion, and GitHub, and a real credential bridge to [credential-broker-service](credential-broker-service.md) (with a deterministic fake-broker fallback for key-free smokes). **Since the R6 MCP-client follow-on** it also runs an `McpToolExecutor` that invokes a tool on an **external MCP server** (the mirror of the gateway's MCP server) behind an **SSRF egress guard** + an optional broker-resolved bearer; built-ins dispatch by descriptor id, an imported MCP tool by `spec.type=="mcp"`. External servers are brought in via `POST /api/v1/tools/import-mcp` (admin-only — egress-check the URL, call its `tools/list`, register each tool as a `pending_approval` descriptor), and a **supply-chain HITL gate** refuses to execute any `spec.type=="mcp"` tool whose `status != "active"` until an admin approves it (`POST /api/v1/tools/{id}/approve`). The gate is forced at the single write point — an MCP descriptor is *always* created `pending_approval`, so the public register/create routes cannot smuggle in an executable one. The Google Drive Reader exists as a registered tool **descriptor only**; its live OAuth connector/executor is deferred (no Drive executor is registered, and there is no key-free smoke for it). The generic `oauth_token` credential path is exercised via the fake broker, but no Drive-specific connector code has been ported. **Asynchronous / queued / streaming execution is out of scope here by design** — that is the R5 execution-engine-service.

`oraclous-core-service` (~6,800 LOC of real-but-dead legacy code) was the port-source. Once its registry/validation/connectors/execution were ported here **and proven** by integration + smoke tests, it was deleted under the §15 destructive-change protocol with explicit Reza sign-off. No legacy port-source remains (`service_status.yaml` `legacy: {}`).

## Purpose

`capability-registry-service` is the substrate's **discovery and execution surface** for what can be composed in a workspace — tools, skills, agents, harnesses, human roles, plus the **connectors** that back tool calls. Every capability has a uniform descriptor with kind discrimination; every resolution and invocation goes through one path.

## Responsibilities

* Unified capability descriptor model (one schema, kind-discriminated)
* Capability resolution: name → descriptor → invocation handle
* **Tool registry + execution** (ported from `oraclous-core-service`; the legacy dual-registry pattern collapses into one)
* **Connectors** (the external-provider integrations ported from `oraclous-core-service`)
* Validation service: input/output schema conformance, credential-requirement accuracy
* Versioning: content hash per descriptor, optional semver tags
* Organisation-scoped visibility — every read/write is parameterised by `organisation_id` (ADR-006); platform/built-in tools are seeded under `PLATFORM_ORG_ID` and read-widened to every tenant org. Cross-org ReBAC sharing is not yet wired in this service
* Capability registration API
* Credential bridge to [credential-broker-service](credential-broker-service.md) for token-backed tool calls

## The five kinds

* **tool** — invokable function with input/output schemas
* **skill** — Markdown-shaped prose loaded into an agent's context
* **agent** — actor with role, capability allocation, LLM config
* **harness** — orchestrated assembly of actors with task board, policies
* **human_role** — declared participation slot, resolved against the org member directory in [auth-service](auth-service.md)

A `capability_pack` is a bundling artifact, not a separate kind — it expands on registration.

## Dependencies

* **Upstream:** Postgres (descriptor storage + local `executions` table), [auth-service](auth-service.md) (principal/organisation identity — JWT-decode under `AUTH_MODE=jwt`, or trusted `X-Principal-*`/`X-Organisation-Id` headers under `AUTH_MODE=gateway`, ADR-018), [credential-broker-service](credential-broker-service.md) (runtime token resolution for connector tool calls)
* **Downstream consumers:** every capability invocation path; the frontend reaches it **directly by host IP:port** until [application-gateway-service](application-gateway-service.md) fronts it

## Salvage-then-delete `oraclous-core-service` (ORAA-4 §15) — DONE

`oraclous-core-service` was the `port_source`. Its tool registry, validation, connectors, and execution were ported into this service **and proven** by integration + smoke tests, after which it was **deleted** (44 files, ~6.3k LOC) under the §15 destructive-change protocol with **explicit Reza sign-off**. No legacy port-source remains (`service_status.yaml` `legacy: {}`). The hollowness audit (`tools/audit/hollowness_audit.py`) that re-opened the hollow R2 stories now reports this service CLEAN.

## Architecture conformance (ORAA-4 §21)

Rebuilt to the layered shape: package root `services/capability-registry-service/src/oraclous_capability_registry_service/` with `routes/` (parse → one service call → HTTP map), all registry/validation/execution logic in `services/`, the only Postgres access in `repositories/(+models.py)`, Pydantic-only `schema/`, `core/{config,dependencies,lifespan}.py`. No logic in handlers; no non-`BaseModel` classes or DB drivers in `routes/`.

## Definition of Done (ORAA-4 §22)

Done only when all 8 gates pass: structurally conformant; not hollow (`check_no_stubs` zero findings + `claimed_done` flipped in `service_status.yaml`); runs (`docker compose up` healthy, `GET /health` 200); real endpoints (integration: register → resolve → invoke a real connector tool vs real substrate via testcontainers, no stub/501); end-to-end smoke (`tests/smoke/smoke.sh`, run as the docker-required `r3_5_gate` job); Reza personally tests and signs off. Per §23: one service, ≤6 coarse vertical slices.

## Related

* ADR-001 — Four-Layer Architecture (Layer 2)
* ADR-002 — OHM as Canonical Manifest Format
* ADR-005 — Workflow Concept Retirement
* [credential-broker-service](credential-broker-service.md) — runtime token source for connector tool calls
* Section 4 — Manifest Format Specification (all five kinds)
