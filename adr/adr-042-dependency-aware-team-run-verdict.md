---
title: "ADR-042 — Team-Run Completion: Per-Member Status + Re-run-from-Checkpoint (amends ADR-035)"
---

# ADR-042 — Team-Run Completion: Per-Member Status + Re-run-from-Checkpoint (amends ADR-035)

| | |
| --- | --- |
| Status | **Accepted** |
| Date | 2026-06-26 |
| Deciders | Drafted by the CTO (johnkennII); **decided by Reza — 2026-06-26**. (A first draft used a three-state SUCCEEDED/PARTIAL/FAILED + required/optional model; Reza simplified it to the per-member-status + re-run-from-checkpoint model recorded below — no partial-success.) |
| Amends | ADR-035 (team runtime spine — replaces its strict fail-closed team-run *completion* state) |
| Implements | oraclous-backend#551 · gates oraclous-backend#549 (the DoefinGPT use-case) |

## Context

ADR-035 made a member whose harness does not `SUCCEED` fail the whole team run (strict fail-closed).
When the team runtime was made real (oraclous-backend#543/#549 — the imported DoefinGPT team: 18
members that both **hand off** to each other and **independently produce + persist** artifacts), this
proved too fragile: one stalling member aborts the run **and discards the other 17 members' already-
persisted work**, even though their artifacts landed.

The naive opposite — "succeed if most members worked" (a head-count / majority vote) — is also wrong,
for the reason the founder named directly: a team run must **never** be called successful if an agent
failed to deliver its job. A majority vote would falsely report SUCCESS while a piece is missing.

We researched what mature systems do (Apache Airflow, AWS Step Functions, Temporal, Microsoft AutoGen
GraphFlow, CrewAI Flows, Claude Code Agent Teams, the UC-Berkeley **MAST** study). Two things
converge: (1) none reports a run "done" while a step failed; and (2) the recovery is **resume / re-run
the failed step from its checkpoint** while preserving the steps that already succeeded — not re-doing
the whole run, and not tolerating a partial result.

## Decision

A team run is judged by **per-member status + re-run-from-checkpoint**, and a team run is `SUCCEEDED`
**only when every member has delivered its job** — there is no partial-success that masks a missing
piece.

- **Each member run carries its own terminal status** (`SUCCEEDED` / `FAILED` / …) and a durable
  **checkpoint** (its last good state).
- **A failed member is re-run from its last checkpoint** — it resumes, it does not start over.
  Members that already succeeded are **NOT** re-run; their persisted work + checkpoints are kept.
  Re-running a failed member also re-runs the members that were **BLOCKED** waiting on its output (its
  downstream dependents — the hand-off map decides who); independent members are untouched.
- **A team run is `SUCCEEDED` only when EVERY member delivered.** If any member failed, the team run
  is **NOT successful** — it is `FAILED` / `INCOMPLETE`, with the failed members listed and
  re-runnable. No member that failed to deliver its job is given a free pass; the run is completed by
  re-running the failed members (from their checkpoints) until all deliver.
- **Transient errors are retried automatically** (rate-limit / timeout / model-overload, with backoff
  + jitter) before a member is marked `FAILED`; permanent errors (bad input, malformed output,
  validation) fail fast and leave the member `FAILED` + checkpointed for a re-run.
- A failed member's downstream dependents are recorded `BLOCKED` (waiting on a missing input) — never
  `SUCCEEDED`, and distinct from a member that itself errored.

This is the **durable-workflow** model (resume-until-complete), not graceful-degradation. There is
**no REQUIRED/OPTIONAL tagging** — every member must deliver — so the recovery is
re-run-from-checkpoint, never partial-success tolerance.

## Consequences

- ADR-035's strict fail-closed team-run state — *abort the whole team and discard its work when one
  member fails* — is replaced. A member's failure now records that member `FAILED` + checkpointed and
  its dependents `BLOCKED`, while independent members finish and keep their work; the run is completed
  by re-running the failed members. (The fail-closed **security/authority** principle of ADR-013/021 —
  deny-on-ambiguous, capability ceiling — is unchanged; this governs only team-run completion +
  recovery.)
- A team run is **never** reported `SUCCEEDED` while a member failed to deliver — the founder's
  invariant. The fragility of all-or-nothing is solved by **recovery (re-run)**, not by tolerating a
  partial result.
- **Maps onto existing primitives:** the harness loop's `LoopCheckpoint` / resume_state, and
  `run_team`'s `completed` parameter (already skips members that ran in a prior drive and reuses their
  output). New work (tracked on oraclous-backend#551): durable per-member status + checkpoints; the
  failure path no longer cancels the stage (`orchestrate.py` `asyncio.gather`); transient/permanent
  retry classification; a team-run **re-run** entrypoint that resumes failed + blocked members from
  their checkpoints, skipping succeeded ones; and the #549 e2e asserting a `SUCCEEDED` run (every
  member delivered + artifacts land + serve).

## Grounding

- **Resume / re-run from checkpoint, preserving succeeded steps** (the core of this decision): Airflow
  "clear + re-run" restarts only the failed task and its downstream, leaving upstream successes intact;
  AWS Step Functions **Redrive** resumes a failed execution from the failed state (not from the start);
  Temporal's durable execution replays history to resume exactly where it left off.
- **Never "done" while a step failed; failure follows the dependency edges:** Airflow `upstream_failed`
  (dependents are BLOCKED, not succeeded; independent branches finish); AutoGen GraphFlow (downstream
  nodes don't activate); CrewAI Flows (`@listen` fires only when its named upstream completes); Claude
  Code Agent Teams (a task with unresolved dependencies cannot be claimed; a failed teammate is not
  fatal — re-run / replace it).
- **Validate at the hand-off seam:** UC-Berkeley **MAST** (NeurIPS 2025) — broken hand-offs are the
  dominant multi-agent failure cause, so a member's output is checked before it is passed downstream.

None of these reports a run successful by a head-count, and all recover a failure by re-running the
failed work from its checkpoint rather than discarding the run.
