---
confluence_id: "884777"
title: "execution-engine-service"
---

# execution-engine-service

**Layer:** 3 (Harness Runtime + Execution Engine) · **Port:** 8008 (gateway prefix `/v1/engine`) · **Status:** **Real — R5 code-complete** (all 7 slices merged; the consolidated `smoke.sh` is green end-to-end against the real substrate; awaiting the ORAA-4 §22 Reza sign-off to flip `claimed_done`). Reached directly by host IP:port behind the [application-gateway-service](application-gateway-service.md), which fronts it on `/v1/engine`.

## What it is now

R5 built this real, end-to-end, in seven vertical slices. It is the **durable orchestration layer above the harness**: it never re-implements the agent loop — it **wraps [harness-runtime-service](harness-runtime-service.md) over HTTP** (both are Layer 3, so they talk by API exactly as the harness calls the registry; ADR-001), and adds everything that must survive a process restart or wait days for a human:

* **Durable async jobs** (S1–S3) — `POST /v1/engine/jobs` accepts an OHM and returns **202 + a QUEUED** `engine_jobs` row; a **Celery worker** (Redis DB 1, isolated from the knowledge-graph worker) calls the harness `/v1/harnesses/execute`, maps the harness status onto the engine state machine (`QUEUED → RUNNING → SUCCEEDED | FAILED | ESCALATED | TIMED_OUT | CANCELLED`), and checkpoints the terminal state with a provenance event per transition. Every state change is a **CAS transition under a row lock**, so cancel can never race the worker. `max_retries` re-queues a failed/timed-out attempt; `timeout_seconds` bounds the harness call; a **lease reaper** (Celery Beat) re-drives jobs stranded RUNNING by a dead worker.
* **Human task board** (S4, S6) — `GET /v1/engine/tasks` is the org's ESCALATED jobs. Two resolutions: `POST /tasks/{id}/complete` for an **entrypoint** human task (the job carries an `assignment_id`) drives the harness assignment complete → both the parked run and the job flip SUCCEEDED; `POST /tasks/{id}/approve` for a **mid-loop HITL** approval (the job carries a `harness_execution_id`, no `assignment_id`) drives the harness `/resume` → APPROVED resumes the agent loop where it paused, DENIED terminates it FAILED.
* **Schedules** (S5) — `POST/GET/DELETE /v1/engine/schedules` register durable cron schedules; a **single Celery Beat** process fires each due schedule as a normal engine job, **idempotent** on `(organisation_id, idempotency_key=schedule:window)` so a duplicate tick never double-fires.
* **Round-table** (S7) — `POST /v1/engine/roundtables` coordinates N actors (agents + humans) over **one shared transcript**, turn by turn: the driver runs each agent turn through the harness (the accumulated transcript is that turn's input) and pauses ESCALATED at a human turn; `POST /roundtables/{id}/respond` appends the human's output and resumes the driver until `max_rounds` complete. A single-driver CAS claim makes the driver redelivery-safe.

Each slice was adversarially reviewed and live-verified through the gateway. The service owns `engine_jobs`, `engine_schedules`, `engine_roundtables`, and `engine_provenance` (its own `alembic_version_execution_engine` table — no shared-DB migration collision).

## API surface (through the gateway, `/v1/engine`)

| Method + path | Purpose |
| --- | --- |
| `POST /v1/engine/jobs` (202) · `GET /jobs` · `GET /jobs/{id}` · `POST /jobs/{id}/cancel` | Durable async job: submit, list, read, cancel |
| `GET /v1/engine/tasks` | The human task board (ESCALATED jobs) |
| `POST /v1/engine/tasks/{id}/complete` | Complete an entrypoint human task (output → SUCCEEDED) |
| `POST /v1/engine/tasks/{id}/approve` | Resolve a mid-loop HITL task (APPROVED resumes / DENIED fails) |
| `POST /v1/engine/schedules` (201) · `GET /schedules` · `DELETE /schedules/{id}` (204) | Register / list / delete a cron schedule |
| `POST /v1/engine/roundtables` (202) · `GET /roundtables/{id}` · `POST /roundtables/{id}/respond` | Start / read / advance a round-table |

## Purpose

`execution-engine-service` handles the work that lives outside a single request: long-running jobs with checkpoints, scheduled wake-ups, task-board state, the mid-loop HITL pause/resume, and multi-actor coordination. The harness runtime handles one synchronous OHM run; the engine handles everything that needs to survive a restart or wait for a human. Separating the two keeps the **governance enforcement point single** (in the harness) and lets schedule firing scale independently of API request limits.

## Architecture (resolved)

* **Engine wraps harness over HTTP** (ADR-001) — never imports harness internals, never re-runs the loop; it records the job + maps `HarnessExecutionOut.status` onto its own state machine. The one exception is the mid-loop HITL **resume**, which the harness owns (it persists the redacted loop checkpoint + re-enters the loop); the engine drives it via `POST /v1/harnesses/{id}/resume`.
* **Durable state = checkpoint-in-Postgres** + a state machine (no event-sourcing; the harness already emits a per-step provenance log as the audit trail).
* **Async = Celery + Redis** (DB 1), lifted from [knowledge-graph-service](knowledge-graph-service.md): a fresh-loop executor per task, org-context rebind, NullPool engine per task (ADR-012), downstream identity reconstructed from the durable job's stored user/org and forwarded to the harness (ADR-018 trusted gateway).
* **Scheduler = Celery Beat** + a DB-backed schedule source (`croniter`); HA/leader-lock deferred (at-least-once via the idempotency key — a missed tick is a missed fire, never a duplicate).

## Dependencies

* **Upstream:** Postgres (durable state), Redis DB 1 (job queue + Beat), [harness-runtime-service](harness-runtime-service.md) (every agent run, over HTTP).
* **Edge:** the [application-gateway-service](application-gateway-service.md) verifies the bearer once and injects `X-Principal-*` + `X-Internal-Key` (ADR-018); the engine trusts them in gateway mode and forwards the same identity downstream to the harness.

## Security commitments

* Org-scoped at every read and write (the org is the principal's, never inbound — ADR-006, fail-closed).
* Cancel/approve/complete/respond go through CAS transitions so a concurrent action can't corrupt state.
* Round-table fan-out is bounded (≤64 total turns, ≤16 actors); transcript entries are bounded; schedule firing is idempotent — the resource-exhaustion threats (Section 6.5 Threat 7) are coded, not advisory.
* A provenance event per job/task/schedule/round-table transition; the HITL checkpoint never persists an unredacted secret (redaction-at-source in the harness loop).

## Known follow-ons (deliberately out of R5)

* Round-table per-turn **retry** (today any agent-turn failure fails the whole round-table — fail-closed) and transcript **context windowing** (the transcript is replayed per turn; bounded per-entry but not summarised).
* Celery Beat HA / leader-lock; SSE progress streaming (poll `GET /jobs/{id}` today).

## Related

* ADR-001 — Four-Layer Architecture (Layer 3) · ADR-006 — org-scoping · ADR-012 — worker DB pooling · ADR-018 — trusted gateway
* [harness-runtime-service](harness-runtime-service.md) — the synchronous OHM runtime the engine drives
* Section 5 — Flow 2 (Execute), Flow 3 (Schedule), Flow 7 (HITL)
