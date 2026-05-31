---
confluence_id: "884777"
title: "execution-engine-service"
---

# execution-engine-service

**Layer:** 3 (Harness Runtime + Execution Engine) · **Port:** 8005 · **Status:** NEW in Phase 5

## Purpose

`execution-engine-service` handles the work that lives outside a single request: long-running jobs with checkpoints, scheduled wake-ups, task board state, and durable execution context. The harness runtime (`harness-runtime-service`) handles synchronous request handling; the execution engine handles everything that needs to survive a process restart or wait days for a human response.

Separating the two prevents schedule firing from being constrained by API request limits and lets each side scale independently.

## Responsibilities

* Durable execution context (checkpointed harness state that survives restarts)
* Schedule registration and firing (per the OHM `triggers` block — cron expressions, recurring events)
* Job tracking (sync, async, progress streaming) — lifted from `oraclous-core-service`'s `tool_execution_service.py`
* Task board state management in the substrate (the data model)
* Pause / resume / cancel for durable executions
* Timeout enforcement (per-step, per-run, per-HITL)
* Retry policy enforcement (declared count, no more)
* Sub-harness invocation isolation

## Dependencies

* **Upstream:** Postgres (durable state, job tracking), Redis (job queues, schedule fire times), `knowledge-graph-service` (for substrate-side state writes), `harness-runtime-service` (which delegates durable work here)
* **Downstream consumers:** the harness runtime (which dispatches durable jobs to the engine and polls for results), the gateway (for pause/resume/cancel APIs exposed to customers)

## Synchronous vs. durable

A harness execution that completes in one HTTP context (chat, quick automation) runs entirely in the harness runtime. A harness execution that involves humans, schedules, or long-running external work runs durably through the execution engine. The same `AgentExecutor` powers both; the trigger and the harness's declared characteristics decide the mode (Section 5 Flow 2).

## Schedule firing

When a harness is committed (Flow 1 Step 12), each schedule trigger registers with the engine. The engine maintains a persistent schedule table: which harness, which trigger, next fire time, schedule definition. At the scheduled time, the engine fires the trigger by creating a new execution context in the harness runtime.

Schedule density and per-workspace schedule counts are bounded to prevent the schedule storm threat (Section 6.5 Threat 7.3).

## Security commitments

* Pause/resume/cancel operations are ReBAC-checked; only authorised members can affect a running execution
* Schedule registration requires `schedule.register` permission
* Durable state is `organization_id`-scoped at every read and write
* Retry counts are bounded by OHM declaration; the engine cannot exceed them

## What lifts in

From `oraclous-core-service`:

* `tool_execution_service.py` (sync + async + jobs)
* Background job orchestration logic
* Progress streaming infrastructure

## Related

* ADR-001 — Four-Layer Architecture (Layer 3)
* Section 3 — Harness Runtime + Execution Engine
* Section 5 — Flow 2 (Execute), Flow 3 (Schedule)
* Section 6.5 — Threat 7 (resource exhaustion)
* Section 8 — Phase 5 (execution engine and runtime completion)
