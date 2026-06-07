---
confluence_id: "688350"
title: "harness-runtime-service"
---

# harness-runtime-service

**Layer:** 3 (Harness Runtime + Execution Engine) · **Port:** 8007 (gateway prefix `/v1/harnesses`) · **Status:** **Real — R4 code-complete** (synchronous OHM runtime: the plan→act→observe loop over real registry tools, under a governance/budget envelope, BYOM live LLM, human-actor dispatch, provenance + consciousness; awaiting the §22 Reza sign-off). **R5 added the mid-loop HITL resume + the assignment claim/complete endpoints** the [execution-engine-service](execution-engine-service.md) drives.

## Purpose

`harness-runtime-service` is the platform's central nervous system. It runs **one OHM synchronously, in-request**: loads the manifest, resolves capability allocations, dispatches the entrypoint actor (agent or human), enforces the policy envelope, runs the agent tool-use loop, and returns the execution row. Durable/async work — long jobs, schedules, multi-actor **round-table** coordination — is the [execution-engine-service](execution-engine-service.md), which drives this runtime over HTTP (ADR-001); the **governance enforcement point stays single here**. The compiler, consciousness agents, and customer harnesses all run on this same runtime — no privileged code path (ADR-003).

## Responsibilities

* Harness execution (loads the OHM, runs to completion or escalation)
* Actor dispatch (agents go through tool-use loop; humans get task board assignments)
* Multi-mode tool-use loop (`AgentExecutor` and its streaming variant, lifted from `knowledge-graph-builder`)
* Capability resolution at every invocation (calls `capability-registry-service`)
* Credential resolution at every invocation (calls `credential-broker-service`)
* Policy envelope enforcement (budget caps, **HITL gates**, output redaction, cross-workspace traversal checks) — coded, prose can't relax it
* **Human-actor dispatch** — an entrypoint human actor parks the run ESCALATED as a `harness_assignments` task; `POST /v1/harnesses/assignments/{id}/claim` + `/complete` resolve it (R5-S4)
* **Mid-loop HITL pause + resume** (R5-S6) — a gated capability halts the loop ESCALATED and persists a redacted loop checkpoint (`harness_checkpoints`); `POST /v1/harnesses/{id}/resume` re-enters the loop on APPROVED (the approved tool runs) or terminates it on DENIED. Secrets never enter the checkpoint (redaction-at-source); provenance emits only the new step tail.
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

## R5 additions (the harness side of the execution engine)

* **Assignment lifecycle** — `AssignmentRepository.claim/complete` + `POST /v1/harnesses/assignments/{id}/{claim,complete}`; complete flips the parked execution ESCALATED → SUCCEEDED with the human's output.
* **Loop checkpoint + resume** — `run_tool_use_loop` returns a `LoopCheckpoint` on a HITL pause (the redacted transcript + the not-yet-dispatched tool calls + the budget cursor); `POST /v1/harnesses/{id}/resume` rehydrates it and re-enters the loop. The drift-proof manifest is replayed from the checkpoint, and load-policy + signatures are re-enforced on resume.

**Multi-actor round-tables are NOT here** — they are coordinated by the [execution-engine-service](execution-engine-service.md), which sequences single-actor harness runs over a shared transcript. The harness stays a single-OHM, single-run service.

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
