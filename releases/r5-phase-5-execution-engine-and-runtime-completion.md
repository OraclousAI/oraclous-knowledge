---
confluence_id: "164225"
title: "R5 — Phase 5: Execution engine and runtime completion"
---

# R5 — Phase 5: Execution engine and runtime completion

> **SUPERSEDED by [R3.5 — Make every service real](r3.5-make-every-service-real.md) (2026-06-04).** This phase is discarded as a standalone release; any still-needed surface folds into the R3.5 per-service sequence. R2/R3 shipped hollow and are being rebuilt real, per service, before any post-gateway work resumes. Content below is retained for reference only.

| Release ID | R5 |
| --- | --- |
| Status | <custom data-type="status" data-id="id-0">Planned</custom> |
| --- | --- |
| Window | Weeks 21-24 |
| --- | --- |
| Owner | [tech-lead](https://oraclous.atlassian.net/wiki/spaces/OP/pages/983101) |
| --- | --- |
| Briefer | [solution-architect](https://oraclous.atlassian.net/wiki/spaces/OP/pages/164068) |
| --- | --- |
| Dependencies | R0, R0.5, R1, R2, R3, R4 (the runtime must exist before the durable layer beneath it can be extracted) |
| --- | --- |

## Goal

Extract the durable execution side (tool execution service, job tracking, async progress) from `capability-registry-service` into a new `execution-engine-service`. Complete the harness runtime with HITL gates, round-tables, schedules, task boards, and cross-workspace federation traversal. After this release the runtime has every primitive the default compiler needs.

## Scope

### In scope

* `execution-engine-service` deployed as its own service with its own deployment unit and scaling profile
* Tool execution service code migrated from capability-registry-service: sync execution, async execution, job tracking, progress streaming
* Task board data model implemented in the Substrate; task board APIs exposed by the execution engine
* HITL primitive: task assignment to a human, notification dispatch through declared channels, execution pause and persistence, resumption on human action, timeout escalation
* Round-table primitive: lifecycle (open, contribute, close), invitation, contribution queue, decision capture, provenance
* Schedule firing: cron expressions registered with the execution engine; the engine fires triggers at scheduled times; scheduled wake-ups create execution contexts
* Multi-actor coordination via task boards: hand-offs, dependencies, status transitions, schedules
* Cross-workspace federation traversal in the runtime: every cross-workspace operation calls the substrate access decision API with the actor's delegated scope

### Out of scope

* Application gateway extraction (R6)
* Compiler harness (R7) — requires HITL and round-tables (this release) to exist first
* Schedule storm protection — deferred to R8
* Consciousness drift detection — deferred to R8
* Federation laundering audit reports — deferred to R8

## Deliverables

- [ ] **execution-engine-service deployed** — verified by the new service running with its own deployment unit; tool execution service code lives here; ports and APIs documented
- [ ] **Task board data model live** — verified by task boards persisting in the Substrate with full provenance and ReBAC enforcement; tasks can be queried, assigned, claimed, completed, escalated, cancelled
- [ ] **HITL primitive working** — verified by an integration test where a harness reaches a `policies.hitl.required_at` gate, execution pauses, a human is notified, the human acts via the task board, and execution resumes with the human's response
- [ ] **Round-table primitive working** — verified by an integration test where an actor opens a round-table, multiple invited actors contribute, a synthesiser proposes a decision, the round-table closes, and provenance captures the full conversation
- [ ] **Schedule firing live** — verified by a scheduled harness with a cron trigger waking at the declared time, the runtime loading the harness, the agent reading the task board and consciousness record, and the scheduled wake-up's work completing
- [ ] **Cross-workspace federation traversal in the runtime** — verified by an agent in workspace A reading from workspace B under a declared cross-workspace scope; the Substrate's access decision API gates the operation; provenance captures the cross-workspace action
- [ ] **Notification dispatch channels working** — verified by HITL notifications being dispatched via task board, email, and at least one of (Telegram, Slack, PagerDuty); test coverage for each declared channel
- [ ] **Checkpoints and resumability** — verified by a durable harness surviving a process restart mid-execution; state restored from the last checkpoint; the harness continues from where it paused

## Architecture references

* [Section 8 — Phase 5](https://oraclous.atlassian.net/wiki/spaces/OP/pages/688329)
* [Section 3 — Layered Architecture](https://oraclous.atlassian.net/wiki/spaces/OP/pages/65967) — Execution Engine ownership, the two operational modes (synchronous vs durable)
* [Section 5 — Flows](https://oraclous.atlassian.net/wiki/spaces/OP/pages/426016) — Flow 3 (Schedule), Flow 4 (Traversal), Flow 5 (Round-Table), Flow 7 (HITL)
* [Structured Governance Taxonomy](https://oraclous.atlassian.net/wiki/spaces/OP/pages/688439) — HITL gates are policy-declared

## ADRs implemented

* [ADR-004](https://oraclous.atlassian.net/wiki/spaces/OP/pages/131083) — Federation via ReBAC Traversal (R5 is where federation becomes a runtime concern in production)

## Threats addressed

| Threat | Mitigation IDs implemented | Coverage |
| --- | --- | --- |
| T1 — Data exfiltration | T1-M2 (cross-workspace traversal is gated by the substrate at every operation) | Full T1 coverage operationally — what was a substrate guarantee from R0.5 is now also a runtime guarantee |
| T4 — Resource exhaustion | T4-M1 (durable execution checkpoints prevent infinite-loop budget burn; the execution engine bounds work per wake-up) | Partial — full schedule-storm protection lands in R8 |
| T5 — Notification spoofing | T5-M1 (notifications are dispatched only by the runtime/execution engine; recipients can verify via the task board, which is the canonical source) | Full T5 baseline |

## Governance impact

R5 makes HITL gates declarative and runtime-enforced. Before this release, HITL is a concept in the Governance Taxonomy; after R5, a manifest's `policies.hitl.required_at` field actually causes the runtime to pause at the named transition, dispatch notifications, and wait for human action. Round-tables also become governable — the orchestration prose can declare round-tables at specific decision points, and provenance captures the resulting deliberation.

## Risks

| Risk | Likelihood | Mitigation | Owner |
| --- | --- | --- | --- |
| Durable execution introduces state-consistency bugs across restarts | High | Checkpoint format is versioned. Restart tests cover every documented harness pattern. Idempotency keys on every external side effect prevent double-execution. | backend-implementer + test-author |
| Schedule firing produces a thundering herd under load | Medium | Jitter is applied to cron firing per harness. Per-organisation rate limits on scheduled wake-ups. Schedule storm protection (R8) hardens this further. | devops-implementer |
| HITL notification channels fail silently | Medium | Every dispatch records a provenance entry with delivery outcome. Failed deliveries trigger fallback to the next channel and surface as a task board annotation visible to the workspace admin. | backend-implementer |
| Round-tables persist beyond their declared maximum duration | Low | The execution engine owns round-table timeouts; on timeout, the declared fallback decision applies and the round-table closes automatically. Test coverage for the timeout path. | backend-implementer |
| Cross-workspace traversal is too permissive because the runtime trusts a stale ReBAC decision | Medium | Per-invocation recheck from R4 applies to traversal as well. Decision cache TTL is bounded; revocation events invalidate cached decisions immediately. | security-architect |

## Dependencies

**Upstream:** R0–R4 (every prior release).

**Downstream:** R6 (gateway exposes task board UIs, round-table UIs, HITL approval surfaces). R7 (compiler harness is the first production harness that exercises HITL, round-tables, and schedules in full).

## Sprint references

Jira epics to be created during Group E.

## Revision history

| Date | Change | Author | Reason |
| --- | --- | --- | --- |
| 27 May 2026 | Page created with the canonical release-page template | tech-lead (via Group D follow-up 3) | Establish R5 as the execution engine + runtime completion release; matches Section 8 Phase 5 |
