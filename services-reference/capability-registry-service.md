---
confluence_id: "884757"
title: "capability-registry-service"
---

# capability-registry-service

**Layer:** 2 (Capability Registry) · **Port:** 8001 · **Status:** **Hollow today — a 136-LOC empty shell. R3.5 step 5 rebuilds it real**, porting the tool registry + execution from `oraclous-core-service`, then salvaging-and-deleting that service (human-gated, destructive).

## Honest current reality

R2 marked this service "done" but it is **136 lines of total Python** — an empty shell with no real registry and no execution. The genuine tool registry, validation, credential bridge, connectors, and execution logic still live, undeleted, in `oraclous-backend/oraclous-core-service` (~6,800 LOC of real-but-dead code). Nothing here resolves or invokes a capability today. This page describes the **R3.5 target**.

R3.5 rebuilds this as **step 5** (after the graph, retriever, identity-org, and credential-broker services are each signed off), because it depends on all of them. It is the largest port: real tool registry + execution comes **from `oraclous-core-service`**, and only once that logic is ported **and tested here** does `oraclous-core-service` get salvaged-then-deleted. That deletion is **destructive and human-gated** (ORAA-4 §15): the source stays `port_source: true, deletable: false` until the port is proven.

## Purpose (R3.5 target)

`capability-registry-service` is the substrate's **discovery and execution surface** for what can be composed in a workspace — tools, skills, agents, harnesses, human roles, plus the **connectors** that back tool calls. Every capability has a uniform descriptor with kind discrimination; every resolution and invocation goes through one path.

## Responsibilities (R3.5 target)

* Unified capability descriptor model (one schema, kind-discriminated)
* Capability resolution: name → descriptor → invocation handle
* **Tool registry + execution** (ported from `oraclous-core-service`; the legacy dual-registry pattern collapses into one)
* **Connectors** (the external-provider integrations ported from `oraclous-core-service`)
* Validation service: input/output schema conformance, credential-requirement accuracy
* Versioning: content hash per descriptor, optional semver tags
* ReBAC-gated visibility (workspace-scoped; cross-workspace sharing needs explicit relationships)
* Capability registration API
* Credential bridge to [credential-broker-service](credential-broker-service.md) for token-backed tool calls

## The five kinds

* **tool** — invokable function with input/output schemas
* **skill** — Markdown-shaped prose loaded into an agent's context
* **agent** — actor with role, capability allocation, LLM config
* **harness** — orchestrated assembly of actors with task board, policies
* **human_role** — declared participation slot, resolved against the org member directory in [identity-org-service](identity-org-service.md)

A `capability_pack` is a bundling artifact, not a separate kind — it expands on registration.

## Dependencies

* **Upstream:** Postgres (descriptor storage), [identity-org-service](identity-org-service.md) + [auth-service](auth-service.md) (ReBAC visibility for human and machine principals), [credential-broker-service](credential-broker-service.md) (runtime token resolution for connector tool calls), [knowledge-graph-service](knowledge-graph-service.md) (`:Agent` nodes some kinds persist)
* **Downstream consumers:** every capability invocation path; the frontend reaches it **directly by host IP:port** until [application-gateway-service](application-gateway-service.md) exists

## Salvage-then-delete `oraclous-core-service` (ORAA-4 §15)

`oraclous-core-service` is marked `port_source: true, deletable: false`. It **stays** until its tool registry, validation, connectors, and execution are ported into this service **and** proven by integration + smoke tests. Only then does its deletion become eligible — and that deletion requires **Reza's human sign-off** because it is destructive. The hollowness audit (`tools/audit/hollowness_audit.py`) tracks this and re-opened the hollow R2 stories under R3.5.

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
