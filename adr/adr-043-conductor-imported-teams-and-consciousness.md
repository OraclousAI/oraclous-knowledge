# ADR-043 — Conductor for Cyclic Imported Teams + the Flow-6 Consciousness Learn Loop

## Status

| | |
| --- | --- |
| Status | Accepted |
| Date | 2026-06-26 |
| Deciders | Reza (directed the capability + the "self-consciousness / continuous learning" requirement, and accepts this ADR); CTO (drove the research + the design); solution-architect (shepherds the build) |
| Driving issue | [#552](https://github.com/OraclousAI/oraclous-backend/issues/552) (E3+E6 keystone) |
| Builds on | **#551 / ADR-042** (team-run completion — per-member status, non-abort, re-run-from-checkpoint; *shipped*) · **ADR-027** (agent memory — Ebbinghaus `:Memory` store, harness write hook, `core/recall-memory`; *shipped*, #332) · **Flow 6 (Learn)** + the Agent-Consciousness concept · ADR-035 (team runtime) · ADR-003 (consciousness skills are themselves harnesses) |

## Context

An imported `.claude/agents` team with **cyclic** hand-offs (analyst → critic → back to analyst, round after round) is flattened to a **single pass** at import: `assemble_team` demotes a cyclic hand-off to a routing-hint *string* with zero `depends_on`, so every member runs **once** on a thin objective and the team never iterates. A dormant LLM-coordinator loop (`run_team_coordinated`, `orchestrate.py:228`) exists but is unwired, unproven, and unbounded (no round / wall-clock / cost / convergence / loop limit). On a weak model the team runs away; on a capable one it burns the full budget without converging.

Reza's requirement is two-fold: a cyclic imported team must (a) **converge reliably**, and (b) **learn continuously** — its performance must improve across runs, with the learning **reflected in the agents' behaviour**, not merely accumulated. (b) is the documented **agent-consciousness** concept, whose runtime form is **Flow 6 (Learn)** and whose substrate — the **ADR-027 Ebbinghaus agent memory** (`:Memory(:Episodic|:Semantic|:Procedural)` with decay/contradiction/consolidation, a harness post-run write hook, the `core/recall-memory` tool) — is already **shipped** (#332). Consciousness records **five pattern families** (repetitive *solutions*, hand-off friction, recurring ambiguity, velocity, failures — successes and process, not just mistakes) and is **consulted before every turn** so it *"affects future behaviour rather than just accumulating"* — the mechanism by which a team improves itself over time.

A 5-agent research survey (LangGraph, AutoGen/CrewAI, OpenAI Swarm + Anthropic's orchestrator-worker, cross-platform reliability, and our own code) converged unambiguously: a **deterministic skeleton with a bounded coordinator only at the loops** is the reliable design. A pure LLM coordinator is the field's known-worst pattern (Swarm shipped unbounded — that was the bug; MAST: more rounds *amplify* errors). A pure fixed-N-round pipeline cannot express "iterate until good enough" (it reproduces today's run-once bug). And a model that grades/​"fixes" its own work **with no external signal degrades** (DeepMind) — so recalibration must be driven by coded external signals, never self-assessment.

## Decision

Adopt a **hybrid conductor** with a **bounded within-run recalibration loop** and the **Flow-6 cross-run consciousness Learn loop over the shipped ADR-027 memory**. The LLM only ever chooses *which* member runs next; every limit, gate, done-check, and behaviour change is governed by code.

1. **Hybrid execution model.** At import, classify the team into an acyclic **skeleton** (runs on the proven `run_team` pipeline) and isolate each genuine loop as a **strongly-connected component** (Tarjan SCC) that runs a **bounded coordinator seam**. The seam reuses the existing dispatch (tool ceiling, run-tree, cost callback, graph binding) and the **#551** completion model (non-abort, per-member status, re-run-from-checkpoint).

2. **Coded termination — never the model's word.** A round finishes only when *(coordinator-done **AND** a coded check confirms it)*: a **coverage floor** (every required member produced output **and** expected artifacts actually landed on the graph) **plus** a **separate-evaluator** quality grade. Four always-on **runaway bounds**, any one of which stops the run: max rounds, wall-clock, **cost budget**, **no-progress**.

3. **Within-run recalibration (tactical "get unstuck").** On a coded stall, insert **one** bounded recalibration step: diagnose the stall from the **external** signals (coverage gaps, grade dimensions, #551 member errors) → emit one directive from a **closed action set** (`re-plan` / `re-frame-objective` / `change-strategy` / `re-scope-member` / `escalate`) → resume over **failed+blocked members only**. Bounded so it converges: a hard cap (default 1–2, max 3); each recalibration spends one real round of the budget; it continues **only if the external signal improves**; an **anti-repeat guard** escalates rather than retry a tried strategy; it never fires on a satisfied done-check. **Driven by external coded signals, never the model's self-grade.**

4. **Cross-run consciousness Learn loop (strategic) — the documented Flow-6 over the shipped ADR-027 memory (NOT a new store).** Realize the four un-wired gaps so performance compounds:
   - **(a) Consult-before-turn** — every agent is fed its `## Relevant Memory` (recall over the ADR-027 `:Memory` store) *before* it acts. This is the line that turns memory into behaviour change.
   - **(b) Five-family write** — the consciousness skill records the *pattern* (repetitive solutions, hand-off friction, recurring ambiguity, velocity, failures — successes + process), not a bare run-record.
   - **(c) `consciousness.permissions` OHM gating** — record / suggest / propose / **never auto-apply**: no agent changes its own behaviour without human review (load-bearing per the consciousness doc).
   - **(d) Compounding proof** — a team measurably improves run-over-run, scored by the evaluator.
   Memory honesty inherits ADR-027: org+graph scoping (a customer's lessons are walled off), Ebbinghaus decay/recency, contradiction/supersede, and **advisory-only** retrieval — the coded done-check remains the source of truth.

## Consequences

- **Positive:** cyclic imported teams converge reliably; a stalled team gets *unstuck* via recalibration instead of looping or quitting; teams *improve across runs* (compounding performance); the design **realizes the documented consciousness over the already-shipped substrate**, not a new invention; everything risky is confined to the smallest region behind coded governors.
- **Costs / risks accepted:** recalibration + the coordinator + consult-before-turn add (capped) model-call cost; the design's value is gated on a **crisp external signal**, so it is weakest on objectives we cannot score (keep the coverage-floor strictly coded); memory introduces a poisoning/staleness surface, contained by ADR-027's scoping + decay + supersede + advisory-only retrieval and warranting a periodic human review of promoted lessons; the **evaluator must remain a separate step** from the producing members.
- **Invariants added:** (1) **the team never satisfies its own done-check** — only coded external signals (coverage-floor, landed-artifacts, tests, separate-evaluator grade) decide *done* and decide whether a recalibration helped; (2) **no agent auto-applies a learned behaviour change without human review** (`consciousness.permissions`, default no-auto-apply).

## Alternatives rejected

- **Pure A — wire the LLM coordinator alone.** The field's known-worst pattern (Swarm-without-a-bound; CrewAI manager-worker failures; MAST "more rounds amplify errors"); inherits unbounded, unproven behaviour.
- **Pure B — compile the loop to a fixed N-round pipeline.** Cannot express "iterate until good enough"; reproduces today's run-once bug.
- **A new `:Reflection` / `:Lesson` memory store.** Rejected — it reinvents the shipped **ADR-027** `:Memory` store; use it.

## Build outline (tests → impl, on #551 + ADR-027; every step proven on the deployed stack through the gateway on real BYOM — never CI-green alone)

1. **Importer fix** — preserve per-edge `next_task`; SCC-isolate each loop as a *small* seam (a single back-edge among 30 agents must not flip the whole team).
2. **Bounded coordinator seam** — a real BYOM coordinator; per-round dispatch through the existing closure; non-abort fan-in from #551; the four runaway bounds.
3. **Coded done-check** — coverage floor (produced-output + landed-artifacts) + the separate-evaluator grade; wire the currently-ignored convergence threshold.
4. **Budget enforcement** — the cost bound (today cost is accumulated, not checked); trip-to-settle, never abort.
5. **Within-run recalibration loop** — stall → diagnose → closed-action directive → resume failed+blocked only; the cap + per-recalibration budget charge + no-improvement stop + anti-repeat guard.
6. **Checkpoint / resume + HITL on the loop** — per-round checkpoint; within-round (not whole-run) de-dup; human-gate check before each round.
7. **Consciousness Learn loop (over ADR-027)** — consult-before-turn (`## Relevant Memory` auto-recall); the five-family write; `consciousness.permissions` OHM gating; the compounding proof.
8. **End-to-end** — DoefinGPT (artifacts land + converge), the ~30-agent book team (GO/HITL + tool ceiling + bounded cost + **improves across runs**), EURail (stays on the deterministic path; coordinator never engages).

## See also

- Issue [#552](https://github.com/OraclousAI/oraclous-backend/issues/552); #551 / ADR-042 (shipped foundation); ADR-027 (agent memory, #332 shipped); Flow 6 (Learn); ADR-003 (consciousness skills are harnesses); ADR-035 (team runtime).
