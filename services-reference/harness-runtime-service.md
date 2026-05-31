---
source_page_id: 688350
title: "harness-runtime-service"
---

# harness-runtime-service

**Layer:** 3 (Harness Runtime + Execution Engine) · **Port:** 8004 · **Status:** NEW in Phase 4 (lifted from `knowledge-graph-builder`)

## Purpose

`harness-runtime-service` is the platform's central nervous system. It executes harnesses: loads OHM manifests, resolves capability allocations, dispatches actors (agents and humans), enforces the policy envelope, and coordinates multi-actor work. The compiler, consciousness agents, and customer harnesses all run on this same runtime — there is no privileged code path for platform-internal harnesses (ADR-003).

## Responsibilities

* Harness execution (loads the OHM, runs to completion or escalation)
* Actor dispatch (agents go through tool-use loop; humans get task board assignments)
* Multi-mode tool-use loop (`AgentExecutor` and its streaming variant, lifted from `knowledge-graph-builder`)
* Capability resolution at every invocation (calls `capability-registry-service`)
* Credential resolution at every invocation (calls `credential-broker-service`)
* Policy envelope enforcement (budget caps, HITL gates, output redaction, cross-workspace traversal checks)
* Round-table primitive (lifecycle, invitation, contribution, decision capture — Phase 5)
* HITL primitive (task assignment, notification dispatch, resumption — Phase 5)
* Provenance write-through (every action recorded; storage lives in `knowledge-graph-service`)
* LLM client factory supporting the three v1 protocol shapes (ADR-007)
* LLM config resolution (agent → workspace → organisation)
* Agent CRUD APIs (the `:Agent` Neo4j nodes live in the graph substrate; the lifecycle service lives here)
* Chat engine (synthetic-agent pattern for chat-shaped interactions)

## Dependencies

* **Upstream:** `auth-service`, `credential-broker-service`, `capability-registry-service`, `knowledge-retriever-service`, `knowledge-graph-service` (for provenance writes and `:Agent` node persistence)
* **Downstream consumers:** `execution-engine-service` (for durable jobs and schedules), `application-gateway-service` (which proxies customer-facing interactions)

## What lifts in (Phase 4)

From `knowledge-graph-builder`:

* `AgentExecutor` (`agent_executor.py`) and its streaming variant
* Agent toolkit (`agent_tools.py`, `agent_tool_schemas.py`) — graph tools become one category of capability among many
* LLM client factory + LLM config service
* Provenance collector (`provenance.py`) for in-flight collection; persistent storage stays in the graph substrate
* Chat engine (`chat_engine.py`)
* Agent CRUD service (`agent_service.py`)

## What lifts in (Phase 5)

* Multi-actor coordination primitives (HITL, round-tables)
* Task board state management (the data model lives in the substrate; the lifecycle lives here)
* Cross-workspace federation traversal coordination
* Schedule-trigger dispatch (interacting with `execution-engine-service`)

## Security commitments

* Capability allocation checked on every invocation; the runtime never invokes a capability outside the agent's OHM allocation (Section 6.5 Threat 4.3)
* Privilege separation: system prompt, capability prompts, and user content go through distinct LLM message channels (Section 6.5 Threat 1.1)
* Inter-actor messages presented as content, not instructions (Section 6.5 Threat 1.3)
* Budget caps enforced unconditionally; prose cannot raise budgets (Section 6 governance model)
* Output redaction post-actor-turn (Section 6.5 Threat 3.1)
* Provenance on every action — actor turns, tool invocations, hand-offs, policy enforcements

## Related

* ADR-001 — Four-Layer Architecture (Layer 3)
* ADR-003 — Platform-as-Code, Actors-as-Harnesses
* ADR-007 — BYOM with Three Protocol Shapes
* Section 3 — Harness Runtime layer
* Section 5 — Flows (especially Flow 2 Execute, Flow 7 HITL)
* Section 6 — Governance Model
* Section 8 — Phase 4 (harness runtime extraction)
