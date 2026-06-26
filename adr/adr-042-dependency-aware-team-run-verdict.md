---
title: "ADR-042 — Dependency-Aware Three-State Team-Run Verdict (amends ADR-035)"
---

# ADR-042 — Dependency-Aware Three-State Team-Run Verdict (amends ADR-035)

| | |
| --- | --- |
| Status | **Accepted** |
| Date | 2026-06-26 |
| Deciders | Drafted by the CTO (johnkennII) capturing the decision; **accepted by Reza — 2026-06-26** (johnkennII drafts; Reza accepts). |
| Amends | ADR-035 (team runtime spine — replaces its strict fail-closed team-run *completion* state) |
| Implements | oraclous-backend#551 · gates oraclous-backend#549 (the DoefinGPT use-case) |

## Context

ADR-035 made a member whose harness does not `SUCCEED` fail the whole team run (strict fail-closed).
When the team runtime was made real (oraclous-backend#543/#549 — the imported DoefinGPT team: 18
members that both **hand off** to each other and **independently produce + persist** artifacts), this
proved too fragile: one stalling member aborts the run and discards the other 17 members' already-
persisted work, even though their artifacts landed.

But the naive opposite — "succeed if most members worked" (a head-count / majority vote) — is also
wrong, and for the reason the founder named directly: it falsely reports SUCCESS when the failure
**cascades** — a member that everyone downstream depended on fails, the chain breaks, and a promised
output is missing while a majority vote happily says "done."

We researched what mature systems do (Apache Airflow, AWS Step Functions, Temporal, Microsoft AutoGen
GraphFlow, CrewAI Flows, Claude Code Agent Teams, and the UC-Berkeley **MAST** failure study). They
**converge**: none judges a run by a head-count. Every one models the run as a hand-off **dependency
map (a DAG)** and propagates a failure **only along the arrows** — it strands the agents downstream
that needed the failed output and leaves independent branches untouched — then judges the run by
whether the **required** outputs survived. (MAST's finding: the #1 real-world cause of multi-agent
failure is broken hand-offs, so output is validated at each seam.)

## Decision

A team-run terminal verdict is **dependency-aware and three-state**, computed AFTER transient-retries
are exhausted and the hand-off dependency map is resolved. Each member output is tagged **REQUIRED**
(a declared deliverable, or a hard input to a downstream member) or **OPTIONAL**.

- **SUCCEEDED** — every REQUIRED output is present and valid (passed its hand-off check). Optional
  members may have failed.
- **PARTIAL** (degraded / completed-with-warnings) — every REQUIRED output is present and valid, but
  ≥1 OPTIONAL/independent member failed. All persisted work is kept and surfaced, with an explicit
  list of which members failed or were skipped.
- **FAILED** — a REQUIRED output is missing, OR a failure stranded a downstream member whose output
  was REQUIRED (the cascade) — **even if most members finished.**

A failed member's direct + transitive downstream dependents are recorded in a distinct **BLOCKED /
upstream-failed** state — never `SUCCEEDED`, and never lumped together with members that themselves
errored. **The verdict is a function of WHICH members failed relative to the dependency map and their
REQUIRED/OPTIONAL tag — never a count or majority vote.**

Supporting mechanics:
- **Transient-only retry** before judging — retry rate-limit / timeout / model-overload with backoff
  + jitter; fail permanent errors (bad input, malformed output, validation) fast.
- **Hand-off validation** — validate a member's output against the shape the next member expects, at
  each seam, before passing it downstream (the MAST highest-leverage fix).
- **Propagate along edges** — a failure strands only the members that depended on the failed output;
  independent branches finish and keep their work.
- **Store consistency on FAILED** — members persist as they go, so a FAILED run's already-written
  artifacts are marked as belonging to a failed run (or a SAGA-style cleanup / human-escalation).

**REQUIRED/OPTIONAL tagging model:** REQUIRED is largely **derived** — a member with downstream
dependents (an outgoing hand-off arrow) is REQUIRED automatically; the team author additionally marks
the declared **deliverables** (outputs promised to the user) as REQUIRED; everything else defaults
OPTIONAL. The product owner confirms the deliverable tagging per team.

## Consequences

- The strict fail-closed *team-run completion state* of ADR-035 is replaced by this verdict. The
  fail-closed **security/authority** principle (ADR-013/021 — deny-on-ambiguous, capability ceiling)
  is unchanged; this governs only the team-run *completion verdict*.
- A team run no longer discards persisted work because one independent member stalled (→ PARTIAL),
  but a cascading failure that breaks a promised output still FAILS — the founder's invariant.
- Stranded dependents are visible (BLOCKED), not silently dropped or falsely succeeded.
- Open implementation items (tracked on oraclous-backend#551): BLOCKED-state propagation in
  `orchestrate.py` (replacing the `gather`-aborts-all); the transient/permanent retry classification
  + caps; the per-seam hand-off schemas and their ownership; the store-consistency policy on FAILED;
  and the #549 e2e updated to assert REQUIRED-outputs-land-and-serve on a SUCCEEDED/PARTIAL run.

## Grounding

Airflow `upstream_failed` + trigger rules (`none_failed_min_one_success`); AWS Step Functions
per-state `Catch` + Distributed-Map tolerated-failure %; Temporal automatic transient-retry + SAGA
compensation; Microsoft AutoGen **GraphFlow** (declared edges; downstream nodes don't activate;
independent branches finish); CrewAI **Flows** (`@listen` fires only when its named upstream
completes); **Claude Code Agent Teams** (a pending task with unresolved dependencies cannot be
claimed; a failed teammate is not fatal — spawn a replacement); UC-Berkeley **MAST** (NeurIPS 2025 —
broken hand-offs are the dominant failure cause). None judges a run by a head-count.
