---
title: "ADR-048 — Three Team Lifecycles: Bounded Run / Standing Team / Seeded Refresh — a stable standing_team_id binds a persistent graph workspace seeded run-to-run (the keystone), a typed seeded-refresh what-changed delta, a schedule-level recurring cap + cost pre-flight distinct from the run-level pool (#585), and closed-loop verdict-consumption that branches on the E4 recommended_action instead of a blind re-run"
---

# ADR-048 — Three Team Lifecycles (Bounded Run / Standing Team / Seeded Refresh)

## Status

| Field | Value |
| --- | --- |
| Status | Proposed |
| Date | 2026-06-27 |
| Approved by | Pending Reza/CTO |
| Supersedes | None |
| Superseded by | None |
| Driving artifact | The platform runs a team **once** and forgets it. There is no notion of a team that *persists* across scheduled fires, no cross-run *refresh*, and no closed-loop *consumption* of the evaluation verdict — so two of the three north-star use cases (bitcoin-gpt standing teams; EURail `--refresh-from`) have **no path**. Epic: [oraclous-backend #389](https://github.com/OraclousAI/oraclous-backend/issues/389) (E8 — the team lifecycles). Lock mandate: [Team-of-Agents — North-Star Lock](../product/team-of-agents-north-star-lock.md) §8 ADR #5 ("Three Lifecycles") + §6 items 12/13/14 + R6(b). Design: [Team-of-Agents Capability Design](../../oraclous-backend/docs/team-of-agents-capability-design.md) Phase C (C5 seeded-refresh) + Phase D (D-NEW-2 standing-team lifecycle, D-NEW-3 cost defaults/pre-flight). |
| Builds on | [ADR-031](adr-031-ohm-v1.1-team-manifest.md) (the team-pooled `OHMBudget` keystone — one Team Harness = one budget surface; the §D3 pooled cap) · [ADR-037](adr-037-flow-level-evaluation-named-batteries-run-tree.md) (the `Verdict` / `recommended_action` this ADR *consumes*; E4 produces it, **E8 consumes it** — ADR-037 §4 deferred the consumer here) · [ADR-043](adr-043-conductor.md) (the within-run prose-routed conductor + bounded recalibration — referenced, not re-litigated) · [ADR-044](adr-044-per-member-budget-and-iteration-governance.md) / **#585** (**run-level pooled** budget enforcement — the run-level cap is referenced and built upon, never duplicated) |

## Context

The team runtime ships a real **single-run** spine and forgets everything after it settles. Reading the engine confirms the three gaps E8 must close, each grounded in a shipped seam:

1. **A team has no lifecycle — only a run.** `POST /v1/engine/team-runs` creates **one** `EngineTeamRun`, `_drive` (`execution-engine-service/.../services/team_run_service.py:443`) drives it once, and the row settles terminal. The scheduler (`EngineSchedule`, `models/schedule.py:23`) can fire a recurring *harness job* or an *adopted-tool run* — its `target_kind` enum (`models/enums.py:16-21`: `HARNESS_JOB` | `ADOPTED_TOOL_RUN`) has **no `team` member**, and `_fire_one` (`schedule_service.py:159`) branches only those two. So a scheduled team is impossible today, and even if it were fired it would **cold re-spawn**: each fire would build a brand-new run with a brand-new (empty) substrate. There is no `standing_team_id`, no persistent workspace, and no seed of run N from run N−1. The Lock §6 item 12 is explicit that a standing team "runs on crons **sharing live state** … **not modeled as re-spawned one-shots**" — exactly what a cold re-spawn is.

2. **There is no cross-run refresh.** EURail's shipped `--refresh-from 909-merged` re-verifies a *prior* ledger against a seed and emits a what-changed delta (Lock §6 item 13; the `eurail-report --refresh-from` skill). The engine has **no seed-prior-output mode** and **no delta output** — a "refresh" today is just a second cold run that re-derives everything from zero and overwrites, with no notion of added/removed/changed and no way to *skip* a record whose evidence did not move. `OHMPrecedence` (`manifest.py`) and the graph substrate exist, but nothing consumes a prior run's output *as a typed input*.

3. **The evaluation verdict is produced but never consumed — the loop is open.** This is the sharpest gap. `_grade_gate` (`team_run_service.py:353`) grades a completed run and `_drive` **stores** the `Verdict` on the SUCCEEDED row (`team_run_service.py:530`, `verdict=verdict`) — but the comment on that very line records the deferral: *"the run STATE is NOT branched on the verdict and NOTHING is enqueued off it — consuming it (re-dispatch / termination) is E8 (ADR-037 §4)."* ADR-037 fixed the *policy line* and explicitly deferred the *mechanism* to E8. The `Verdict` carries a `recommended_action` (`re_task` / `re_route` / `escalate_human` — ADR-037 Decision 1) that **nothing reads to branch on**. Worse, the within-run conductor's convergence signal is also unread for branching: `OHMTermination.convergence` (`manifest.py:158`, e.g. `"evaluator>=0.8"`) is a string **nothing parses**, and `run_team_coordinated` (`orchestrate.py:228`) bounds its loop only by `max_rounds` ∩ `termination.max_rounds` (`orchestrate.py:255`) with **no quorum, no deadlock/livelock detection, and no evaluator-threshold gate** on whether to continue. So a below-threshold run today either strands (no re-dispatch) or, if a naïve loop were wired, would blindly re-run the identical team — the field's known-worst pattern (a model re-running itself with no external signal degrades; more rounds amplify errors — ADR-043 Context).

The three north-star use cases bind these three gaps respectively: **bitcoin-gpt** is four *standing* teams on crons sharing a world-model graph (gap 1); **EURail** is the *seeded refresh* with a 909-record delta (gap 2); and **all three** need a below-threshold run to *do something useful* rather than strand or blindly retry (gap 3). The Lock §8 makes "Three Lifecycles" a binding ADR; this is it.

**This ADR does NOT re-litigate budget enforcement or the within-run loop.** ADR-044 / **#585** own run-level *pooled* budget enforcement; ADR-043 owns the within-run prose-routed conductor and its bounded recalibration. This ADR **references and builds on** both: the *run-level* pooled cap (#585) is the draw-down every re-dispatch in decision 5 spends against, and the within-run conductor (ADR-043) is the engine each individual run uses. What is new here is the layer *above* a run — the lifecycle that owns runs over time — plus the verdict-consumption branch the conductor's convergence field has been waiting for.

**Two budget caps, deliberately non-overlapping (read this once, it governs decisions 2 + 4):**
- **Run-level pooled cap — OWNED BY ADR-044 / #585, NOT this ADR.** `OHMBudget.max_*_total` (`manifest.py:236-247`) is the single enforced ceiling for **one** team run's whole fan-out (ADR-031 keystone; ADR-044 wires it to engine-side atomic draw-down). It bounds *one run*. **Every re-dispatch in decision 5 draws this down** so a closed loop cannot run forever *within a run/refresh*.
- **Schedule-level recurring cap — NEW HERE.** A *per-cadence* ceiling over the **standing fleet** — the sum of accrued spend across the *sequence* of scheduled runs in a window (e.g. `$X/day`). It bounds *the lifecycle*, pausing the whole standing team when the cadence ceiling is hit. It does **not** replace the run-level pool: a single run is still bounded by #585; the schedule-level cap bounds the *recurring accrual* the pool can never see (a pool resets every run; the fleet's daily burn does not).

## Decision

**Adopt three first-class team lifecycles over the shipped single-run spine — Bounded Run, Standing Team, Seeded Refresh — by binding a stable `standing_team_id` to a persistent graph workspace seeded run-to-run (the keystone), emitting a typed what-changed delta on refresh, enforcing a schedule-level recurring cap with a cadence-aware cost pre-flight distinct from the run-level pool, and closing the evaluation loop by branching on the E4 `recommended_action` instead of a blind re-run.** Five sub-decisions.

### 1. The Three-Lifecycle model (the Lock §8 ADR #5 mandate, made structural)

A team is run under exactly one of three declared lifecycles. The lifecycle is a property of *how runs relate over time*, orthogonal to the manifest (the same Team Harness can run under any of the three):

| Lifecycle | What it is | Termination | Binds (Lock §6) |
| --- | --- | --- | --- |
| **Bounded Run** | The shipped behaviour: one `EngineTeamRun`, fan-out, settle terminal. The default. | The run ends (success / fail / escalate). | all (the base case) |
| **Standing Team** | A long-lived, **non-terminating** team on a cron whose every fire seeds run N from run N−1's persistent graph state, with per-cadence recurring-budget accrual. | **The lifecycle never ends; each individual run is bounded** (two-level termination). | item 12 (bitcoin; book marketing) |
| **Seeded Refresh** | A run that takes a **prior run's output as a typed seed**, re-verifies it, and emits a what-changed delta — an *incremental* cross-run pass, not a cold re-derive. | The refresh run ends; the seed→delta is its first-class output. | item 13 (EURail `--refresh-from`) |

**Why a model, not three disconnected features:** Standing Team and Seeded Refresh are *compositions* of the same two primitives — persistent state (decision 2) and a typed seed-and-diff (decision 3) — over the Bounded Run base. A standing team that seeds each fire from the prior graph *is* a recurring seeded refresh on its own state; an EURail `--refresh-from` *is* a single seeded refresh from a named prior run. Naming the three explicitly stops the design from drifting back to "a team is a run" (the prior-iteration failure the Lock §1 names).

**The seam:** the lifecycle is recorded on the standing-team / schedule record (decision 2) and on the team-run request, never inferred. **Rejects:** treating "scheduled" as merely "fire the same one-shot again" (the cold-re-spawn the Lock §6 item 12 forbids), and treating "refresh" as "run it again and overwrite" (decision 3 forbids).

### 2. THE KEYSTONE — standing-team state-binding: a stable `standing_team_id` ⇄ a persistent graph workspace, seeded run-to-run

> **This is the keystone of E8. Everything else hangs on it.** Standing Team (decision 1) is meaningless and Seeded Refresh (decision 3) has nothing to refresh *from* unless a team's identity and its substrate persist across fires. A cold re-spawn — the only thing the engine can do today — is precisely the failure the Lock forbids.

**Decide:** a **standing team is a durable, org-scoped record** carrying a stable **`standing_team_id`** bound 1:1 to a **persistent graph workspace** (an org-scoped graph id — the substrate the team's runs read and write). Each scheduled fire creates run N as a **Bounded Run whose `graph_id` is the standing team's persistent workspace**, so run N **reads the state run N−1 wrote** rather than starting empty. The lifecycle never ends; each run is bounded — **two-level termination**.

The exact seams:

- **`target_kind='team'` on the schedule enum.** Add a third member to `TargetKind` (`models/enums.py:16-21`, today `HARNESS_JOB | ADOPTED_TOOL_RUN`): `TEAM`. It joins the existing pattern verbatim — the migration carries a `server_default` so old rows read clean (the §43 comment's discipline), and `register` (`schedule_service.py:70-119`) gains a `team` branch alongside the conditional manifest-exclusivity rules already there (`schedule_service.py:86-97`). A `team` schedule carries the standing-team reference (its `standing_team_id` → manifest + persistent `graph_id`), not an inline harness manifest or an `instance_id`.

- **An `enqueue_team_run` fire branch.** `_fire_one` (`schedule_service.py:159-176`) gains a third branch beside `_fire_harness_job` (`:178`) and `_fire_adopted_tool` (`:196`): **`_fire_team_run`**, which creates an `EngineTeamRun` for the standing team's manifest **bound to the standing team's persistent `graph_id`** and enqueues it via a new `enqueue_team_run` callback (the exact parallel of the injected `EnqueueFn` / `AdoptedToolEnqueueFn`, `schedule_service.py:37/51`). The fire runs under the same `org_scope(sched.org)` cross-org carve the other two branches use (ADR-006/ADR-030; `schedule_service.py:153`).

- **A `team_run` idempotency key.** The fire is idempotent on the **same** `(org, idempotency_key=f"{sched.id}:{window}")` row the harness/adopted paths already use (`schedule_service.py:169`, the at-least-once dedupe with the `(org, idempotency_key)` unique constraint), so a duplicate Beat tick never double-fires a standing run.

- **Per-cadence recurring-budget accrual.** The standing-team record accrues spend **across the sequence of fires** (drawn from each run's settled `cost_tokens`, `team_run_service.py:530`/`:536`) into a per-cadence window total. This is the accumulator decision 4's schedule-level cap reads. **It is NOT the run-level pool** (#585) — that resets every run; this accrues across runs.

- **Two-level termination.** The *lifecycle* is unbounded (a standing team runs until disabled/deleted, like a cron schedule). Each *run* is bounded by its own run-level budget (#585) + `OHMTermination.max_wall_seconds` (`orchestrate.py:127`) + the conductor's bounds (ADR-043). The standing team never "completes"; its runs do.

**Precedent borrowed (and where Oraclous already *is* the precedent):** this is **Temporal's continue-as-new / seed-state-as-input** pattern — a long-running entity does not accumulate unbounded history in one execution; each iteration starts a fresh, bounded run **seeded with the prior run's carried-forward state**. And it is **Dagster's asset-is-the-substrate** model — the durable thing is not the run, it is the materialized *asset*; a scheduled run re-materializes the asset incrementally. **Oraclous already has the Dagster shape natively: the persistent graph workspace *is* the durable asset, and a standing run re-materializes it.** We do not need Dagster's asset graph as a new abstraction — the graph substrate *is* it; decision 2 simply binds a `standing_team_id` to that asset and seeds each run from it.

**Rejects:** (a) cold re-spawn (a fresh empty substrate per fire — the Lock-forbidden one-shot); (b) one ever-growing run that never settles (Temporal's anti-pattern: unbounded history, no per-run governance/audit/checkpoint — it would void the ADR-031 "one run = one governed unit" boundary and the #551 per-run completion model); (c) a *second* graph forced per standing team (the Lock §6 item 8 / R5 "never force a second graph" — the workspace is the user's adopted graph where one exists).

### 3. Seeded-refresh mode — prior output as a typed seed → a first-class 5-way what-changed delta, with a per-record evidence fingerprint to skip-unchanged

**Decide:** a refresh run takes a **named prior run's output as a typed seed input** and produces, as a **first-class output alongside the deliverable**, a **5-way what-changed delta**: each record in the prior output is classified `added` | `removed` | `changed` | `unchanged` | `re_confirmed` (re-verified and still true vs. simply not re-examined — these are distinct, and conflating them is exactly the "silently worse" failure Lock O3 forbids). The delta is the refresh's contract, not a side effect.

To keep refresh **incremental** (not a disguised cold re-run), each prior record carries a **per-record evidence fingerprint** — a content/evidence hash (**Dagster's data-version**): on refresh, a record whose upstream evidence fingerprint is unchanged is **skipped** (classified `unchanged` without re-running its producer), and only records whose evidence moved are re-derived (→ `changed` / `re_confirmed` / `removed`) plus genuinely new ones (→ `added`). This is what makes a 909-record refresh cheap: most records skip.

**The seams:** the seed is threaded as a typed input on the team-run request (the prior run's stored `results`, `team_run_service.py:536`, read as the seed), the fingerprint rides each record into and out of the graph workspace (decision 2's substrate), and the delta is computed engine-side at settle and stored beside the verdict. The acceptance target is **reproduce EURail `--refresh-from 909-merged`**: give the EURail team a prior 909-record ledger as the seed and assert the emitted delta matches the shipped skill's what-changed output, passing the report-editor 10-gate `OHMGateBattery` refresh-only checks (gates 9–10, ADR-037 Decision 2 / `applies_when`).

**Rejects:** (a) "refresh = run again and overwrite" (no delta, no skip — re-derives everything, the cold-run-in-disguise); (b) a binary changed/unchanged (loses `added`/`removed`/`re_confirmed` — the user cannot tell a re-verified-still-true record from an un-examined one); (c) trusting recency over evidence (skip-by-timestamp re-confirms nothing — the fingerprint is evidence-content, not a clock).

### 4. Cost pre-flight + a schedule-level recurring cap + a cheaper scheduled-scan tier (distinct from the run-level pool, #585)

**Decide three things, all at the *lifecycle* level (above one run):**

- **(a) A forward, cadence-aware cost pre-flight, surfaced BEFORE GO.** Pressing GO on a standing fleet projects **"~$X/day at this cadence"** with a **per-member breakdown**, computed from each member's model tier × expected tokens × the cron cadence (the shipped `billing/rates.py` price function ADR-044 already uses, projected forward over the cadence). This is Lock O2 / §6 item 14 ("surfaces model-tier economics + a projected recurring cost **up front**"). It runs on the request path before the standing team is enabled.

- **(b) A SCHEDULE-LEVEL recurring cap that pauses the whole standing fleet.** A per-cadence ceiling (e.g. `$X/day`) checked against the recurring accrual decision 2 maintains; when the accrual crosses it, the standing team is **paused** (the schedule disabled, like the cron `enabled` flag, `models/schedule.py:37`) — it does **not** silently overrun (Lock O2: "a cap that **pauses**, not silently overruns"). A paused fleet surfaces in the O4 status surface and resumes on the next cadence window or human resume.

  > **This is DISTINCT from the run-level pooled cap (#585) — reference and build on it, do not duplicate.** #585 bounds **one run's** fan-out (`OHMBudget.max_*_total`, reset every run). The schedule-level cap bounds **the recurring accrual across the sequence of runs** — a thing the per-run pool structurally cannot see (it resets). A single standing run is bounded by #585; the *fleet's daily burn* is bounded here. The two compose: a run halts on #585; the fleet pauses on this cap.

- **(c) A cheaper scheduled-scan model-tier default.** A routine scheduled scan (a standing team's recurring fire) defaults to a **cheaper member model tier** than an interactive run, because a 06:00 scan over mostly-unchanged data does not need the top tier (Lock §6 item 14: "a cheaper default for routine scheduled scans"). The default is overridable per member (the manifest still wins); it only changes the *unset* default for scheduled fires.

**The seams:** the pre-flight is a request-path projection over `rates.price`; the cap is the standing-team record's per-cadence accrual (decision 2) checked at fire time in `_fire_team_run`; the tier default is applied when a `team` schedule fires (the scheduled-scan branch picks the cheaper default for members that did not declare a tier). **Rejects:** (a) no pre-flight (GO blind — the bitcoin author cannot see "$40/day" before committing, Lock O2 P0); (b) folding the recurring cap into the run-level pool (it cannot see cross-run accrual — they are different ceilings); (c) one tier for both interactive and scheduled (overpays on every routine scan).

### 5. Closed-loop verdict-consumption — branch on the E4 `recommended_action`, never a blind identical re-run

**Decide:** the E4 `Verdict` (ADR-037) is finally **consumed**. On settle, the engine reads the stored verdict (`team_run_service.py:530`) and, when the run is **below threshold**, branches on the verdict's `recommended_action` from a **closed action set** — it **never** blindly re-runs the identical team:

| `recommended_action` (ADR-037) | E8 consumption |
| --- | --- |
| `re_task` | re-dispatch with a **revised objective/sub-goal** (the failing members re-run on a corrected task, not the same one) |
| `re_route` | re-dispatch with a **different routing** (a different member/strategy handles the gap — the conductor's `re-route`, ADR-043) |
| `escalate_human` | pause to HITL — the run does not retry; the human decides (the shipped escalate path) |

And two coded loop-safety controls, both external-signal-driven (never the model's self-grade — ADR-043 invariant):

- **Wire `evaluator>=threshold` into the conductor's `coordinate()`.** `OHMTermination.convergence` (`manifest.py:158`, e.g. `"evaluator>=0.8"`) is today an **unparsed string**; `run_team_coordinated` (`orchestrate.py:228`) ignores it for branching. Parse it and feed the **evaluator's score** into the loop's continue/stop decision: the loop continues (recalibrates, ADR-043) only while below threshold and the external signal is *improving*; it stops on threshold-met **or** no-progress. This closes the gap ADR-043 build-step 3 named ("wire the currently-ignored convergence threshold").
- **Quorum + deadlock/livelock detection.** Add a **quorum** check (a multi-evaluator/multi-check threshold — proceed only when a quorum of checks pass, reusing the `OHMGateBattery` floor semantics) and **deadlock/livelock detection** (the loop is stuck if the same below-threshold state recurs with no score improvement — the anti-repeat guard ADR-043 names, lifted to the verdict layer): a detected deadlock/livelock **escalates** rather than re-dispatching into the same wall.

- **EVERY re-dispatch draws down the run-level pool (#585), so the loop cannot run forever.** Each `re_task` / `re_route` re-dispatch spends one real draw-down against `OHMBudget.max_*_total` (ADR-044 / #585); when the pool is exhausted the loop **halts and escalates** — the same hard kill-switch ADR-044 §3 defines. This is the bound that makes closed-loop consumption safe: the loop is bounded by the *already-shipped* run-level pool, not by a new limiter. (Within a standing team, the *fleet* is additionally bounded by decision 4's schedule-level cap.)

**The seam:** the branch lands in `_drive` at the point the verdict is produced (`team_run_service.py:526-530`) — today a comment marks it deferred to E8 ("consuming it … is E8"); E8 replaces the no-op with the branch above, re-enqueuing through the existing `enqueue`/`advance` path (`team_run_service.py:418/440`) for `re_task`/`re_route` and the escalate path for `escalate_human`. **Rejects:** (a) a blind identical re-run (the field's known-worst pattern — a model re-running itself with no external signal degrades, more rounds amplify errors, ADR-043 Context); (b) self-grading the convergence (the team must never satisfy its own done-check — ADR-043 invariant 1; the evaluator is a *separate* step); (c) an unbounded loop (every re-dispatch is pool-bounded by #585 — no new limiter, no runaway).

## Consequences

### Positive

- **A team finally has a life beyond one run.** Standing Team and Seeded Refresh become first-class lifecycles, closing Lock §6 items 12/13 and unblocking bitcoin-gpt's standing fleets and EURail's `--refresh-from` — the two north-star cases with no path today.
- **The keystone makes "standing" real, not aspirational.** A stable `standing_team_id` bound to a persistent graph workspace, seeded run-to-run, replaces the cold re-spawn with the Temporal continue-as-new + Dagster asset-is-substrate shape Oraclous already fits natively (the graph *is* the durable asset). Two-level termination keeps each run governed (ADR-031/#551) while the lifecycle persists.
- **Refresh is incremental and honest.** The 5-way delta + per-record evidence fingerprint make a 909-record refresh cheap (most records skip) and *legible* — `re_confirmed` ≠ `unchanged`, so the user is never silently-worse (Lock O3).
- **Two non-overlapping budget ceilings, cleanly composed.** The run-level pool (#585) bounds one run; the schedule-level cap bounds the recurring fleet — neither duplicates the other, and a forward cost pre-flight + cheaper scheduled tier make a standing fleet cost-sane *before* GO (Lock O2 / item 14).
- **The evaluation loop closes.** The `recommended_action` ADR-037 produced and deferred is finally consumed; a below-threshold run re-tasks/re-routes/escalates instead of stranding or blindly retrying, bounded by the existing run-level pool — the convergence field the conductor has been ignoring is finally wired.
- **Almost entirely Reshape, not Greenfield.** Every seam is an *extension* of a shipped one (a third `TargetKind`, a third `_fire_*` branch beside two, a `recommended_action` branch where a deferral comment sits, the shipped `rates.price`/graph/verdict). Small PRs, low blast radius.

### Negative

- **State-binding adds a persistence + concurrency surface.** A standing team's persistent workspace must be written transactionally per fire and read seed-consistently by the next fire; two fires of the same standing team (a slow run N overlapping fire N+1) must not corrupt the seed — the idempotency key blocks double-fire, but overlap-vs-skip on a long run is a real ordering decision (proposed default: skip the new window if the prior run is still RUNNING, like `last_fired_at` semantics).
- **The evidence fingerprint must be sound, or refresh lies.** A fingerprint that misses an upstream change silently skips a record that *did* move (a false `unchanged`); the fingerprint must hash the actual evidence, not a proxy, and a fingerprint-scheme bug degrades the delta's trust. Mitigation: fail-open on fingerprint *absence* (re-derive when unsure), fail-closed only on a *match* — an uncertain record is re-run, never skipped.
- **Two budget caps raise the "why did it pause/halt?" surface.** A run can halt on #585 *or* the fleet pause on the schedule-level cap; the status surface (O4) must name *which* ceiling fired, or a paused fleet is opaque (mirrors the ADR-044 three-layer "which layer bound it" cost).
- **Closed-loop consumption adds (bounded) re-dispatch cost.** Each `re_task`/`re_route` spends a real pool draw-down; a pathological objective could exhaust the pool in retries. This is by design (the pool is the bound), but it means a below-threshold run can cost up to its full pool before escalating — the cost pre-flight (decision 4) must price the *worst case* (full-pool), not the happy path.

## Alternatives considered

### A. Model a standing team as one long-running execution that never settles

Keep a single `EngineTeamRun` alive forever, appending each scheduled iteration to it. **Rejected** — it is Temporal's named anti-pattern (unbounded history in one execution) and it voids Oraclous's "one run = one governed unit" boundary (ADR-031) and the #551 per-run completion/checkpoint model: there would be no per-run budget reset, no per-run audit/provenance close, no per-run verdict. The two-level model (decision 2: lifecycle unbounded, each run bounded) keeps governance per-run while persisting the team — the continue-as-new shape, not the unbounded-run shape.

### B. Cold re-spawn — fire the scheduled team as a fresh one-shot each window

Reuse the existing `_fire_harness_job` shape and just build a new team run with a fresh substrate each fire. **Rejected** — it is exactly the Lock §6 item 12-forbidden "re-spawned one-shots" with no shared live state; run N learns nothing from run N−1, and Seeded Refresh (decision 3) has nothing to seed from. State-binding to a persistent workspace (decision 2) is the whole point of "standing".

### C. A schedule-level cap that reuses the run-level pool (one budget, not two)

Enforce the recurring fleet ceiling by widening `OHMBudget.max_*_total` to cover the fleet. **Rejected** — the run-level pool resets every run by construction (ADR-031/044: one run = one pool); it *structurally cannot* observe cross-run accrual. A fleet that fires 24×/day, each run under its pool, would burn 24× the per-run budget with no ceiling ever tripping. The recurring accrual (decision 2) and its cap (decision 4) are a *different ceiling over a different scope*; conflating them is unenforceable. (This mirrors ADR-031 Alternative-C's "per-member that sums" rejection, one scope up: per-run pools do not sum to a fleet ceiling either.)

### D. A binary refresh delta (changed / unchanged)

Emit only whether each record changed. **Rejected** — it loses `added`/`removed` (the user cannot see records that appeared or vanished) and collapses `unchanged` with `re_confirmed` (a re-verified-still-true record is indistinguishable from one that was never re-examined — the "silently worse" failure Lock O3 forbids). The 5-way delta is the minimum that is *legible*.

### E. Blind re-run on a below-threshold verdict (no branch on `recommended_action`)

When the grade is below threshold, re-run the same team. **Rejected** — it is the field's known-worst pattern (ADR-043 Context: a model re-running itself with no external signal degrades; MAST "more rounds amplify errors"; Swarm-without-a-bound). A below-threshold run must *change something* — re-task, re-route, or escalate — driven by the external `recommended_action`, never a self-graded identical retry. The convergence threshold and quorum/deadlock detection (decision 5) make the loop converge or escalate, never spin.

### F. Re-litigate budget enforcement / the within-run conductor here

Fold per-member + run-level budget enforcement and the within-run loop into this ADR. **Rejected as out of scope** — ADR-044 / #585 own budget enforcement (run-level pooled) and ADR-043 owns the within-run prose-routed conductor + recalibration. This ADR *references and builds on* both (every re-dispatch draws the #585 pool; each run uses the ADR-043 conductor) and adds only the layer above a run (the lifecycle) + the verdict-consumption branch the conductor's convergence field was left waiting for. Duplicating those decisions here would create two drifting definitions of the same ceiling/loop.

## Proof note — E8's lifecycles are not done until proven on the deployed stack (the Lock milestone batteries)

Per the deployed-stack verification law (`FUCK_CLAUDE_FUCK_PAPERCLIP.md` rules 1/3/5) and the Lock's milestone batteries, E8 is **not done on CI-green**. Each lifecycle needs a real proof, driven through the gateway (`:8006`) on real BYOM, on the deployed docker stack:

- **Standing Team (the keystone) — bitcoin-gpt standing teams.** A `target_kind='team'` schedule fires a standing team on a cron; fire N reads the graph state fire N−1 wrote (assert the seeded carry-forward, not a cold empty substrate); the per-cadence accrual climbs and the schedule-level cap pauses the fleet when crossed; the cost pre-flight shows "~$X/day at this cadence" before GO. The keystone fails if fire N starts empty.
- **Seeded Refresh — EURail `--refresh-from 909-merged`.** The EURail team runs in refresh mode seeded from the shipped 909-record ledger and emits the 5-way delta; assert the delta matches the shipped skill's what-changed output and that fingerprint-unchanged records are *skipped* (not re-derived), passing the report-editor 10-gate refresh-only checks.
- **Closed-loop consumption.** A deliberately below-threshold run branches on `recommended_action` (re-task / re-route / escalate) — assert it does **not** blindly re-run, that each re-dispatch draws the run-level pool (#585), and that an exhausted pool / detected livelock escalates rather than spinning.

The `use-case-guardian` checks each PR against the bound Lock items (§6 items 12/13/14, O2/O3/O4); a regression on a bound item fails the guardian gate.

## Implementation notes — the E8 child issues this implies

E8 (#389) is **Reshape** (it extends shipped seams; only the delta-compute + fingerprint + the verdict-branch are net logic). Each ships as a `[tests]`→`[impl]` pair (ADR-010, TDD), bundled per the PR-bundling law (one PR / multiple commits), guardian-checked, proven on the deployed stack through the gateway on real BYOM — never CI-green alone. The child issues:

1. **`[adr]` Three Team Lifecycles (this ADR-048)** — the three-lifecycle model, the state-binding keystone, the seeded-refresh delta, the two-cap distinction, the closed-loop branch. **Gates all other E8 issues.** Authored by `solution-architect`, CTO-accepted.
2. **Standing-team state-binding (THE KEYSTONE)** — the durable `standing_team_id` ⇄ persistent graph workspace; `TargetKind.TEAM` (migration with `server_default`); the `_fire_team_run` branch + `enqueue_team_run` callback; the `team_run` idempotency key; per-cadence recurring-budget accrual; two-level termination. *(Serves Lock item 12.)*
3. **Seeded-refresh mode** — prior output as a typed seed; the 5-way `added/removed/changed/unchanged/re_confirmed` delta as a first-class output; the per-record evidence fingerprint (skip-unchanged, fail-open on absence / fail-closed on match); reproduce EURail `--refresh-from 909-merged`. *(Serves Lock item 13.)*
4. **Cost pre-flight + schedule-level recurring cap + cheaper scheduled tier** — the cadence-aware "~$X/day" forward projection (per-member, over `rates.price`); the schedule-level pause-the-fleet cap (DISTINCT from #585's run-level pool — reference, build on, do not duplicate); the cheaper scheduled-scan default tier. *(Serves Lock O2 / item 14.)*
5. **Closed-loop verdict-consumption** — branch on `recommended_action` (`re_task` / `re_route` / `escalate_human`, never a blind re-run); parse `evaluator>=threshold` into the conductor's `coordinate()` continue/stop; quorum + deadlock/livelock detection; every re-dispatch draws the run-level pool (#585) so the loop halts. *(Serves the open-loop gap ADR-037 §4 deferred to E8.)*

**Explicitly OUT (referenced, not re-litigated):** **run-level pooled** budget *enforcement* (ADR-044 / #585 — this ADR *spends* the pool, never redefines it); the within-run prose-routed conductor + bounded recalibration (ADR-043 — each run *uses* it). E8 *consumes* E4's verdict (ADR-037) and *builds on* the #585 pool + the ADR-043 conductor; it does not rebuild them.

## References

- **Epic** [oraclous-backend #389](https://github.com/OraclousAI/oraclous-backend/issues/389) — E8 (the three team lifecycles).
- **Lock** [Team-of-Agents — North-Star Lock](../product/team-of-agents-north-star-lock.md) — §8 ADR #5 ("Three Lifecycles"), §6 items 12 (standing/non-terminating/recurring-budget), 13 (seeded refresh / `--refresh-from`), 14 (cost pre-flight + cheaper scheduled tier), R6(b), O2 (cost pre-flight + pause-cap), O3 (partial/legible delivery — the `re_confirmed`≠`unchanged` honesty), O4 (status surface).
- **Design** [Team-of-Agents Capability Design](../../oraclous-backend/docs/team-of-agents-capability-design.md) — Phase C (C5 seeded-refresh cross-run lifecycle), Phase D (D-NEW-2 standing-team lifecycle, D-NEW-3 cost defaults / O2 pre-flight/cap).
- [ADR-031 — OHM v1.1 Team Manifest](adr-031-ohm-v1.1-team-manifest.md) — the team-pooled `OHMBudget` keystone (one Team Harness = one budget surface, the §D3 pooled cap) and its per-run governance boundary the two-level termination preserves; Alternative-C (no-summing) the schedule-level cap honours one scope up.
- [ADR-037 — Flow-Level Evaluation, Named Batteries, Run-Tree](adr-037-flow-level-evaluation-named-batteries-run-tree.md) — the `Verdict` / `recommended_action` this ADR **consumes**; E4 produces the verdict + progress, §4 explicitly **defers the closed-loop re-dispatch consumer to E8** (decision 5); the `OHMGateBattery` floor reused for quorum + refresh-only gates.
- [ADR-043 — the conductor](adr-043-conductor.md) — the within-run prose-routed conductor + bounded recalibration (referenced, not re-litigated); decision 5 wires the convergence field it left ignored; its "team never satisfies its own done-check" + anti-repeat invariants are inherited.
- [ADR-044 — Per-Member Budget & Iteration Governance](adr-044-per-member-budget-and-iteration-governance.md) / **#585** — **run-level pooled** budget enforcement (the run-level pool every re-dispatch draws down; **referenced and built upon, never duplicated** — the schedule-level cap is a different ceiling over a different scope).
- [ADR-006 — Organisation as Outermost Tenancy Unit](adr-006-organisation-as-tenancy-unit.md) / [ADR-030 — Realize the Postgres RLS Backstop](adr-030-realize-postgres-rls-backstop.md) — the org-scope carve the cross-org Beat sweep + per-fire `org_scope` already use; standing teams + their workspaces are org-scoped.
- **Shipped code anchors (read in this repo):** `services/execution-engine-service/.../models/enums.py:16-21` (`TargetKind` — `HARNESS_JOB`/`ADOPTED_TOOL_RUN`, the third `TEAM` member added here); `.../models/schedule.py:23,37,43` (`EngineSchedule`, `enabled`, `target_kind` + `server_default`); `.../services/schedule_service.py:37,51,70-119,159-176,178,196` (the injected enqueue callbacks, `register`'s conditional branches, `_fire_one` + `_fire_harness_job`/`_fire_adopted_tool` the `_fire_team_run`/`enqueue_team_run` branch parallels, the `(org, idempotency_key)` dedupe `:169`, the `org_scope(sched.org)` carve `:153`); `.../services/team_run_service.py:353` (`_grade_gate`), `:443` (`_drive`), `:526-530,536` (the verdict produced + STORED with the "consuming it … is E8" deferral comment, `cost_tokens` accrual), `:418,440` (the `advance`/`enqueue` resume path the `re_task`/`re_route` branch reuses); `.../services/team_run.py:59,65-66,88,112-113` (`make_harness_dispatch`, `on_child`/`on_cost`, the per-member ceiling, the token cost surfaced); `packages/ohm/src/oraclous_ohm/orchestrate.py:96` (`run_team`), `:127` (the per-run wall-clock termination), `:228,255,274` (`run_team_coordinated`, the `max_rounds` ∩ `termination.max_rounds` bound, the `coordinate()` call the convergence threshold wires into); `packages/ohm/src/oraclous_ohm/manifest.py:151-158` (`OHMTermination` — `convergence` the unparsed string decision 5 wires), `:207-215` (`OHMOrchestration.success_criteria`), `:236-247` (`OHMBudget` — the run-level pool, #585's surface).
- **Precedents surveyed:** Temporal **continue-as-new** / seed-state-as-input (the bounded-run-with-carried-state shape standing teams adopt); Dagster **asset-is-the-substrate** + **data-version** (the persistent graph workspace as the durable asset; the per-record evidence fingerprint / skip-unchanged). EURail `eurail-report --refresh-from` (the seeded-refresh oracle, the 909-record ledger).
- [ADR index](index.md)

## Revision history

| Date | Change |
| --- | --- |
| 2026-06-27 | Initial draft (Proposed). Decides the **Three Team Lifecycles** (E8 / #389). (1) The Bounded Run / Standing Team / Seeded Refresh model (Lock §8 ADR #5) — Standing + Refresh as compositions of persistent-state + typed-seed-and-diff over the Bounded base. (2) **THE KEYSTONE — standing-team state-binding:** a stable `standing_team_id` ⇄ a persistent graph workspace, each scheduled fire seeding run N from run N−1's graph state (not a cold re-spawn); `TargetKind.TEAM` (+ `server_default` migration), an `_fire_team_run`/`enqueue_team_run` branch, the `team_run` idempotency key, per-cadence recurring-budget accrual, two-level termination (lifecycle unbounded, each run bounded) — Temporal continue-as-new + Dagster asset-is-substrate, which the graph workspace already is. (3) Seeded-refresh — prior output as a typed seed → a first-class 5-way `added/removed/changed/unchanged/re_confirmed` delta + a per-record evidence fingerprint (Dagster data-version) to skip-unchanged; reproduce EURail `--refresh-from 909-merged`. (4) A cadence-aware cost pre-flight ("~$X/day", per-member) before GO + a SCHEDULE-LEVEL recurring cap that pauses the whole fleet (DISTINCT from #585's run-level pool — built on, not duplicated) + a cheaper scheduled-scan tier default. (5) Closed-loop verdict-consumption — branch on the E4 `recommended_action` (re_task/re_route/escalate, never a blind re-run); wire `evaluator>=threshold` into the conductor's `coordinate()`; quorum + deadlock/livelock detection; every re-dispatch draws the run-level pool (#585) so the loop halts. OUT (referenced, not re-litigated): budget enforcement (ADR-044/#585); the within-run conductor (ADR-043). Proven on the deployed stack via bitcoin-gpt standing teams + EURail seeded-refresh (the Lock milestone batteries). Pending Reza/CTO. |
