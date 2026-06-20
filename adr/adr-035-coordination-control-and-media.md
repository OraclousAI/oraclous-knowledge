---
title: "ADR-035 — Coordination Control & Media: the team runtime spine (orchestration agent, three orchestrators, hand-off envelope, media taxonomy, dispatch-time ceiling)"
---

# ADR-035 — Coordination Control & Media: the team runtime spine

## Status

| Field | Value |
| --- | --- |
| Status | Proposed |
| Date | 2026-06-20 |
| Approved by | pending (Reza/CTO) |
| Supersedes | None |
| Superseded by | None |
| Driving artifact | [Team-of-Agents — North-Star Lock & Acceptance Test](../product/team-of-agents-north-star-lock.md) — §2 makes acceptance **item 1 RUNNABLE** (the imported DAG must actually *run* a team), §6 acceptance items 4 / 4b / 16, §4 CUT list, §8 ADR list **#2 (Coordination-control & media)** |

## Context

[ADR-034](adr-034-adoption-first-import.md) imports an existing agent setup to a runnable OHM v1.1 Team Harness, and [ADR-031](adr-031-ohm-v1.1-team-manifest.md) decided the target schema (`members[]` with `depends_on`/`fan_out`/`outputs_schema`, `orchestration`, pooled `budget`, `task_board`). But importing a DAG is not running it. Lock §2 makes acceptance item 1 *RUNNABLE*: "bring the team you already have, press GO, and **it runs**." Today nothing runs a team. [ADR-033](adr-033-orchestrator-capabilities-status-and-retirement.md) Part 1 already converted the ADR-005 L77 promise — *"a small set of baseline orchestrator capabilities (sequential, parallel, conditional)"* — from an untracked aside into a tracked R7 E3 deliverable, but committed only that they exist as deliverables; it explicitly deferred the controller design to *"the coordination-control ADR (lock §8 item 2)."* **This ADR is that ADR.**

The gap is concrete and degenerate. The only multi-actor primitive that runs today is a single-driver round-table, `roundtable_service.drive` (`execution-engine-service/.../services/roundtable_service.py:117`). Its actor loop is naive round-robin (`actor = actors[turn % n]`, `roundtable_service.py:145`); each turn awaits one actor serially with no `asyncio.gather` (`roundtable_service.py:157`); its "fan-in" is an in-memory `transcript.append({...})` (`roundtable_service.py:167`); its "merge" is last-writer-wins (`final = transcript[-1]["output"]`, `roundtable_service.py:181`); and it threads context by concatenating the *entire* transcript into a flattened 4000-char-per-entry string for every actor (`_render_context`, `roundtable_service.py:336`; `_bounded`, `roundtable_service.py:327`). There is no parallelism, no real barrier, no conditional branching, no typed hand-off, and no member-ceiling check on what a routed actor may dispatch. `sequential` exists only in this degenerate form; `parallel` and `conditional` do not exist.

Three runtime seams already carry the durable, org-scoped, CAS-guarded machinery the orchestrators must reuse rather than rebuild, and this ADR reshapes (not replaces) them:

- **The round-table** (`roundtable_service.drive`, above) — the turn-sequencer skeleton the three orchestrators succeed.
- **The durable dispatch/retry/CAS seam** in `job_service` — `execute(job_id, principal)` runs one harness and settles the outcome (`job_service.py:160`); `_settle` re-queues a failed/timed-out job if retries remain (`job_service.py:282`); `_transition` does CAS into a target state (`job_service.py:319`) over a `with_for_update()` row lock (`job_repository.py:130`); enqueue is fire-and-forget to Celery (`run_tasks.py:194`). Orchestrators dispatch sub-runs through *this* seam (a `sub_run_dispatch_fn` that creates+enqueues a new job), never by calling `execute()` directly — retry stays at the job level.
- **The HITL task board** in `task_service` — the open board is the org's ESCALATED jobs (`task_service.py:45`); `complete` settles an entrypoint human task harness-first then CAS (`task_service.py:52`); `approve` resolves a mid-loop gate harness-first then CAS (`task_service.py:91`). The blocking-gate-node reshapes this into a first-class DAG node.

The single-agent execution spine is already shipped and pure: the plan-act-observe loop `run_tool_use_loop` (`harness-runtime-service/.../domain/loop/tool_use.py:92`) enforces all governance *before* dispatch, and the **single dispatch call site** is `result = await dispatch(spec, tc["args"])` (`tool_use.py:193`). [ADR-032](adr-032-capability-absence-structural-gate.md) shipped the capability-absence guard `assert_capability_allowed(member, requested)` (`packages/ohm/.../capabilities.py:27`) over the member's immutable `tools[]` ceiling — but it is not yet *threaded* into the loop: the current `dispatch` callback has no acting-member context. This ADR decides the controller that drives the orchestrators, the typed hand-off that replaces the flattened string, the media taxonomy that says when to use which, and where the ADR-032 ceiling check fires at dispatch.

## Decision

### 1. The orchestration-agent contract — "choice is prose, mechanics are coded"

The team runtime separates **what the controller chooses** (prose-interpreted) from **what the platform enforces** (coded, non-overridable). The prose-interpreting **Orchestration Agent** (design B2) reads the manifest `orchestration` block (`style`, `success_criteria`, `termination`) and the **live task-board state**, and decides only: *which member acts next, who acts first, when a round-table converges, and whether `success_criteria` is met* (declaring run completion). It reasons in prose over typed results; it never holds a key to any mechanism.

Everything load-bearing is **coded and not configurable by the controller's prose**:

- **Budgets** — the single pooled team envelope (ADR-031 `max_tokens_total`/`max_sub_runs`/`max_usd_total`/`ttl_seconds`); the controller cannot grant itself more.
- **Gates** — the HITL gating in `PolicyEnvelope.gated_bindings` (`policy.py:47`) and the blocking-gate-node (decision 6) halt the run regardless of what the controller wants to do next.
- **Barriers** — the fan-in barrier (decision 2) is structural over the `depends_on` DAG topology (`OHMManifest.execution_stages()` → `dag.topological_stages`), evaluated *before* any controller reasoning; the controller cannot dispatch a downstream stage before its upstream stage's barrier resolves.
- **Ceiling** — `assert_capability_allowed` (decision 5) fires at the dispatch seam against the *acting member*, after the controller has already chosen the route; no prose choice can widen a member's `tools[]`.

This is the invariant that makes the whole team a single governed unit: the controller's prose may be wrong, but a wrong prose choice can never exceed a budget, skip a gate, cross a barrier, or dispatch outside a ceiling. The Orchestration Agent is **opt-in** (decision 8); on the minimal path the generated static DAG (ADR-034 / E2) drives the orchestrators directly, no controller required.

### 2. The three orchestrators as `core` capabilities, reshaping `roundtable_service.drive`

The three baseline orchestrators (ADR-033 Part 1 / design B1) ship as `core`-registry capabilities (`orchestrate.sequential`, `orchestrate.parallel`, `orchestrate.conditional`), each receiving the Team Manifest + current run state, dispatching the next member set via the `job_service` `sub_run_dispatch_fn`, awaiting per its kind, and returning a **structured stage result** (not a flattened transcript string). All three are constrained by the R4 T3-M1 guardrail (route only to manifest-declared members/capabilities) and run under the one-harness-one-governance-unit invariant.

How each reshapes the degenerate round-table:

- **`orchestrate.sequential`** — the structured, typed-hand-off successor to the round-table. It replaces the `actor = actors[turn % n]` round-robin (`roundtable_service.py:145`) with a `depends_on`-ordered successor walk, and replaces the flattened `_render_context` replay (`roundtable_service.py:336`) + last-writer `final = transcript[-1]` merge (`roundtable_service.py:181`) with the typed hand-off envelope of decision 3 — each member receives the prior member's *typed* `outputs_schema` payload, not the whole concatenated transcript. The per-turn CAS update (`roundtable_service.py:176`) and the `_bounded` entry cap (`roundtable_service.py:327`) are preserved.
- **`orchestrate.parallel`** — runs a stage's members concurrently with `asyncio.gather` (replacing the serial per-turn `await` at `roundtable_service.py:157`) and **blocks on a real fan-in barrier** (replacing the in-memory `transcript.append`, `roundtable_service.py:167`). It drives `fan_out` (ADR-031 `OHMFanOut`): one instance per item of the `over` JSONPath list, capped at `max_parallel`. Its merge is a first-class reducer (design B3 `aggregate.reduce`/`aggregate.synthesize`), not last-writer-wins.
- **`orchestrate.conditional`** — routes on a predicate evaluated over prior members' typed results, expressed as conditional `depends_on`/`orchestration` edges. The predicate is coded; *which* branch is taken given the data is the deterministic mechanic, while the controller's prose chooses the branch only where the manifest leaves it open.

**Fan-in barrier semantics.** The barrier is structural over the `depends_on` DAG: members in the same stage fan out, members in a downstream stage wait on **all** upstream `depends_on` members of the prior stage (`execution_stages()` topological stages, fail-closed on cycle/unknown/duplicate via `dag.topological_stages`). Three completion rules are supported, declared in `orchestration.termination`: **all** (default — every branch completes), **quorum** (the first *k* of *N* branches satisfy `convergence`, the rest are cancelled), and **termination** (a `max_rounds`/`max_wall_seconds` deadline fires, settling whatever completed). The barrier is evaluated *before* controller reasoning — the controller cannot release a downstream stage early.

### 3. The structured hand-off envelope (B5) — typed, lives in `packages/ohm`

The flattened-string hand-off (`_render_context`, `roundtable_service.py:336`) is replaced by a typed envelope, defined once in `packages/ohm` (beside the OHM v1.1 `members[]`/`outputs_schema`/`schemas` it references — keeping the contract in lockstep with the schema, the same residency rationale ADR-034 §8 used for the importer):

```
HandoffEnvelope {
  from_role:       <member role>          # the producing member
  to_role:         <member role>          # the consuming member (depends_on edge)
  objective_slice: <str>                  # the specific sub-goal this hand-off addresses
  payload:         <dict>                  # schema-validated against the producer's outputs_schema
  provenance_ref:  <run-tree link>        # the sub-run that produced it (one provenance stream)
  cursor:          <opt continuation token># pagination / resume position for streamed work
}
```

`payload` is **schema-validated against the producing member's `outputs_schema`** at the hand-off boundary; a payload that fails the producer's `outputs_schema` is a fail-closed hand-off error, never silently truncated (unlike `_bounded`'s 4000-char cut). The envelope threads member→member along `depends_on` edges (`orchestrate.sequential`) and is the reducer's per-branch input (`orchestrate.parallel` fan-in). **Isolation:** the envelope carries *data only, never capability* — receiving it does not widen the receiver's ceiling (ADR-032 §1); the receiver still dispatches only within its own `tools[]`.

### 4. The coordination-media taxonomy (design §6) — when to use which

`OHMOrchestration.medium: list[str]` declares the chosen media per team. The decision guide:

| Medium | Realized on (seam) | Use when |
| --- | --- | --- |
| **structured hand-off** (B5) | `orchestrate.sequential` + the decision-3 envelope | Pipeline stages with a typed contract between them (producer→consumer); the default sequential medium. |
| **parallel fan-out + barrier** (B1) | `orchestrate.parallel` + fan-in barrier (decision 2) | Independent gathering at scale (EURail's 14 research subagents); N members do disjoint work, results merged by a reducer. |
| **round-table** (made structured) | `roundtable_service` reshaped onto `orchestrate.sequential` + envelope | Synchronous deliberation — debate, adversarial QA, consensus — where members *react to each other* over rounds until convergence. |
| **job / task board** | `task_service` (`task_service.py:45`) | Async long-running mixed human+agent work; a durable backlog of ESCALATED jobs; the substrate for the blocking-gate-node (decision 6). |
| **blackboard** (C4) | team-scope graph memory (ADR-027 `:Memory`/`:Finding` nodes) | Shared team-scope memory read by concurrent members via traversal; loosely-coupled accretion rather than directed hand-off. |
| **A2A invoke** (B4) | `core/invoke-harness` under scope-inheritance (child ⊆ parent) | A member calls a sub-agent as a capability; **opt-in / out of scope here** (decision 8). |
| **head-switching** (degenerate) | the inline single-context member (ADR-034 §2) | One agent, one context, rotating role-prompt — fallback for tiny jobs not worth a multi-member team. |

A team may declare more than one medium (e.g. a hand-off pipeline whose one stage fans out in parallel). The medium is the controller's *coordination vocabulary*; the orchestrators (decision 2) are its mechanics.

### 5. Dispatch-time capability-absence enforcement (acceptance item 4)

Every orchestrator routing path — sequential successor, parallel fan-out, conditional branch, hand-off transfer, blackboard write, A2A invoke — funnels through the single dispatch seam, where the **acting member's** ceiling is checked. The check is wired at the existing dispatch call site `result = await dispatch(spec, tc["args"])` (`tool_use.py:193`): E3 threads a `current_member` (`OHMMember`) through the loop's call chain and inserts, between `tool_calls_made += 1` (`tool_use.py:191`) and the dispatch (`tool_use.py:193`):

```python
assert_capability_allowed(current_member, spec.binding)   # packages/ohm/.../capabilities.py:27
```

so a `spec.binding` outside `current_member.tools` (the immutable ceiling, `capabilities.py:17`) is **fail-closed denied** before any side effect (a member with `tools: Read,Grep,Glob,Write` structurally cannot `send`/`publish`/`upload`/`spend`). **No routing path may widen the ceiling**: the check is keyed on the acting member resolved from the dispatch context, *never* the orchestrator or controller — the controller's prose choice of *who acts* is mechanically bounded by *that member's* declared `tools[]`. This is upstream of and distinct from governance policy (ReBAC, ADR-004/013): the ceiling is unconfigurable possession, policy is the configurable conditions of exercise.

### 6. The blocking-gate-node (acceptance item 4b) — non-opt-in for the book case

A member with `kind: human` (+ `human_role`, no `manifest_ref`) sitting on the DAG is a **blocking node**: when the run reaches it, the run **pauses** and does **not advance any dependent `depends_on` member** until the human advances it (approve / reject / edit-then-advance). It is realized on the existing engine task board + HITL claim/resolve seam (`task_service.complete`, `task_service.py:52`; `task_service.approve`, `task_service.py:91`) — but reshaped from inline job state into a **first-class DAG node** carrying metadata (decision options, deadline, assignment). The node's `done`/`approved` transition is the **sole satisfier** of its downstream `depends_on` edges; agents **cannot cross it by any routing path** (it is a structural DAG barrier, not a capability check). The book's 7-gate sequence A–G imports to an ordered chain of these nodes (ADR-034 §6). **The blocking-gate-node itself is mandatory** (Lock §4 — the book case needs it); only the HITL **SLA / capacity / time-to-resolution apparatus** (D4) is cut to opt-in.

### 7. ADR-005 L77 status note — orchestrators tracked-and-built; original primitives retired-vs-deferred

This ADR completes the L77 promise that ADR-033 Part 1 tracked: `sequential`/`parallel`/`conditional` are now not only tracked deliverables but **designed and being built** under R7 E3 — `orchestrate.sequential` is the typed-hand-off successor to the degenerate round-table, `orchestrate.parallel` adds the real `asyncio.gather` fan-in barrier, `orchestrate.conditional` adds predicate routing. The **retired-vs-deferred ledger stands as ADR-033 Part 2 recorded it**: the original *graph-resident `:Agent` team ontology* (retired by ADR-029) and *cascading per-agent inherited budgets* (retired by ADR-005; re-opened only as the ADR-031 pooled envelope) stay **retired** — no orchestrator or controller path may re-introduce them; *cross-harness task boards* and *consciousness drift-detection* stay **deferred** (the R7 task board is per-Team-Harness; closed-loop re-planning is bounded by explicit `success_criteria`, not a drift signal). This ADR introduces no new retirement; it ratifies that the coordination spine is built within that ledger.

### 8. Scope / CUT

- **B2 dynamic Orchestration Agent = opt-in (flag).** The minimal path runs the static generated DAG (ADR-034 / E2) directly against the three orchestrators — no prose-interpreting controller required. The Orchestration Agent is enabled per-team via an `orchestration` opt-in flag for cases that need dynamic who-acts-next reasoning. (Lock §4 CUT: "orchestration agent (opt-in)".)
- **B4 A2A invoke-harness / recursive agent-calls-agent = out (opt-in / later).** Listed in the media taxonomy for completeness; not built in E3 (EURail unused; book's one delegation covered by the coordinator; bitcoin no-direct-coupling). When built it inherits scope (child ⊆ parent) and funnels through the decision-5 ceiling check.
- **D4 HITL SLA / capacity / time-to-resolution apparatus = out (opt-in).** Keep the capability-absence gate (decision 5) **and** the blocking-gate-node (decision 6); cut only the SLA/queue machinery.
- **D5 cross-org / confused-deputy serving-time isolation = out (opt-in).** Keep within-run write-scope isolation (the book case needs it).

## Alternatives considered

### A. Keep the degenerate round-table (do nothing)

Ship the team layer on `roundtable_service.drive` as it stands — round-robin `turn % n`, serial awaits, `transcript.append` fan-in, `transcript[-1]` merge, flattened-string context. **Rejected** — this is exactly the gap the audit named (ADR-033 Context) and the wall Lock §2 makes falsifiable: it cannot run EURail's 14-way parallel research (no `asyncio.gather`, no barrier), cannot express the book's conditional gate routing, cannot pass a typed payload between members (only a 4000-char concatenation), and has no member-ceiling check — so a routed actor could dispatch any capability, voiding ADR-032 item 4. "It runs" (Lock §2) is false on this seam for all three north-star cases.

### B. Build a generic workflow / DAG-execution engine

Stand up a dedicated workflow engine (nodes, edges, a scheduler) as the team runtime. **Rejected** — [ADR-005](adr-005-workflow-concept-retirement-harness-as-replacement.md) retired the "workflow" concept precisely to avoid a second orchestration model alongside the harness: a team is a **Team Harness (OHM v1.1)** interpreted by the runtime, and orchestration is a `core` *capability* (ADR-002/003), never platform code baked into an engine. A workflow engine would fork governance/budget/provenance away from the one-harness-one-governance-unit invariant and re-introduce the exact duplicated-control-plane cost ADR-005 and ADR-033's ledger forbid.

### C. LLM-coordinator-only — let the controller do everything in prose

Make the Orchestration Agent the whole mechanism: it reasons over prose and directly calls members, gates, and budgets, with no coded barrier/ceiling/budget enforcement. **Rejected** — this collapses the "choice is prose, mechanics are coded" invariant (decision 1) that makes the team a single *governed* unit. A prose-only controller can hallucinate past a budget, skip a human gate, release a barrier early, or route a member to a capability it never declared — directly failing acceptance items 4 (no path widens a ceiling) and 4b (agents cannot cross a human gate). The coded mechanisms exist exactly so a wrong prose choice cannot become an unsafe action.

### D. Per-member sub-orchestrators (each member runs its own coordination)

Let each member carry and run its own orchestration sub-block, composing recursively. **Rejected for E3** — this is the recursive A2A shape (B4), which is cut to opt-in (decision 8): no north-star case needs deep recursion, and unbounded per-member orchestration re-opens the multi-governance-surface and cascading-budget problems ADR-033 retired. The flat, manifest-declared DAG with one pooled envelope covers EURail / bitcoin / book; recursion is a later, gated grant.

## Consequences

### Positive

- **"It runs" becomes true (Lock §2).** The imported DAG (ADR-034) actually executes: EURail's 14-way parallel research runs under a real `asyncio.gather` barrier, book's gate sequence pauses on blocking human nodes, and a typed payload threads member→member. Acceptance items 4 and 4b move red→green, and item 16's evaluator battery has a loop to run inside.
- **The team is one governed unit.** "Choice is prose, mechanics are coded" (decision 1) guarantees that budgets, gates, barriers, and ceilings hold regardless of controller reasoning — one budget surface, one provenance stream, one ReBAC envelope (ADR-005 invariant).
- **ADR-032's ceiling becomes load-bearing at runtime.** Threading `current_member` into `tool_use.py:193` makes the shipped-but-unwired guard actually fire on every orchestrator routing path — no orchestrator/A2A/hand-off/coordinator path can widen a member's `tools[]`.
- **Reshape, not rebuild.** The CAS/retry/durable-dispatch seam (`job_service`/`job_repository`), the task board (`task_service`), and the round-table skeleton are preserved and reshaped; only dispatch, actor-selection, fan-in/merge, and context-threading change. Lower risk, smaller PRs.
- **The minimal path needs no controller.** The static generated DAG drives the orchestrators directly; the prose Orchestration Agent is opt-in, so the common case has no LLM-in-the-coordination-loop cost or non-determinism.

### Negative

- **The typed hand-off raises the schema bar.** A member with a missing or wrong `outputs_schema` now fails the hand-off boundary (fail-closed) where the old flattened string silently truncated. This surfaces import-fidelity bugs (good) but means the importer/dry-run (ADR-034 §7) must populate `outputs_schema` faithfully or hand-offs break — a load-bearing dependency on ADR-034.
- **Two ADRs to assemble the orchestrator picture.** ADR-033 commits the orchestrators as deliverables and the retirement ledger; this ADR designs the controller/envelope/media/ceiling. A reader needs both. The split is deliberate (one decision per ADR) but is friction.
- **The barrier/ceiling threading touches a hot path.** Inserting `assert_capability_allowed` at `tool_use.py:193` and threading `current_member` through the loop signature is a change to the shipped single-agent spine; it must not regress the single-agent (non-team) path, which has one implicit member whose ceiling is its own manifest `tools[]`.
- **Quorum/termination barriers add cancellation complexity.** "First k of N, cancel the rest" and deadline-fire settling introduce sub-run cancellation that must race-safely interact with the `job_service` CAS (`_transition`, `job_service.py:319`) — a cancelled branch settling concurrently with the worker must not corrupt the pooled budget accounting.

## Implementation notes

This ADR is R7 epic **E3 — the runtime spine** (oraclous-backend #384 / #418), decomposed into child issues:

- **#419** — `orchestrate.sequential` as a `core` capability: the typed-hand-off successor reshaping `roundtable_service.drive` (`roundtable_service.py:117`) — `depends_on`-ordered successor walk replacing `turn % n` (`:145`), envelope replacing `_render_context` (`:336`) + `transcript[-1]` merge (`:181`); preserve the per-turn CAS update (`:176`).
- **#420** — `orchestrate.parallel` + the real fan-in barrier: `asyncio.gather` over a stage, `fan_out{over,max_parallel}` (ADR-031 `OHMFanOut`), barrier semantics all / quorum / termination over `execution_stages()` (`dag.topological_stages`); the B3 reducer (`aggregate.reduce`/`synthesize`). Sub-runs dispatched via the `job_service` `sub_run_dispatch_fn` (create+enqueue, `run_tasks.py:194`), retry stays at the job level (`_settle`, `job_service.py:282`).
- **#421** — `orchestrate.conditional`: predicate routing over prior members' typed results; conditional `depends_on`/`orchestration` edges.
- **#422** — the `HandoffEnvelope` type in `packages/ohm` (decision 3) + `outputs_schema` validation at the hand-off boundary; thread it through `orchestrate.sequential` and the parallel reducer.
- **#423** — dispatch-time ceiling enforcement (decision 5): thread `current_member` through `run_tool_use_loop` (`tool_use.py:92`) and insert `assert_capability_allowed(current_member, spec.binding)` (`capabilities.py:27`) between `tool_use.py:191` and `:193`; the single-agent path uses its own manifest as the implicit member.
- **#424** — the blocking-gate-node (decision 6) reshaping `task_service` (`task_service.py:45/52/91`) into a first-class `kind: human` DAG node whose advance is the sole satisfier of downstream `depends_on`; the opt-in Orchestration Agent (B2) flag (decision 8 — minimal path uses the static DAG).

All three orchestrators reuse the **CAS transition + org-scoped RLS** pattern unchanged (`job_service._transition`, `job_service.py:319` over `with_for_update()`, `job_repository.py:130`; the round-table `transition`, `roundtable_repository.py:71`) — only dispatch, actor selection, fan-in/merge, and context-threading are reshaped. The B2 dynamic controller, B4 A2A, D4 HITL-SLA, and D5 serving-time isolation are out of E3 (decision 8). Validation reuses the shipped v1.1 DAG checks (`topological_stages` — acyclic / unknown / duplicate, fail-closed).

## References

- [Team-of-Agents — North-Star Lock & Acceptance Test](../product/team-of-agents-north-star-lock.md) — the driving artifact: §2 makes item 1 RUNNABLE + the capability-absence/blocking-gate corrections, §6 acceptance items 4 / 4b / 16, §4 CUT list (orchestration-agent opt-in, A2A/HITL-SLA/D5 out), §8 ADR list #2 (Coordination-control & media)
- [Team-of-Agents Capability Design](../../oraclous-backend/docs/team-of-agents-capability-design.md) — §5 B1 (the three orchestrators + fan-in barrier), B2 (orchestration agent), B3 (aggregator/reducer), B5 (hand-off envelope), D4 (HITL-member); §6 (media taxonomy); §10 (R7 build sequence, E3 position); §11 item 2 (this coordination-control ADR)
- [ADR-033 — Orchestrator Capabilities Status (ADR-005 L77) and Original-Primitive Retirement](adr-033-orchestrator-capabilities-status-and-retirement.md) — Part 1 tracked the three orchestrators as E3 deliverables and deferred the controller design to *this* ADR; Part 2's retired-vs-deferred ledger this ADR ratifies (decision 7)
- [ADR-032 — Capability-Absence as a Structural Gate](adr-032-capability-absence-structural-gate.md) — the `assert_capability_allowed` ceiling guard (`packages/ohm/.../capabilities.py:27`) this ADR wires at the dispatch seam (decision 5) and the blocking-gate-node it shipped (decision 6)
- [ADR-031 — OHM v1.1 Team Manifest](adr-031-ohm-v1.1-team-manifest.md) — the schema the orchestrators consume (`members[]`, `depends_on`, `fan_out`, `outputs_schema`, `orchestration`, pooled `budget`, `task_board`, `schemas`); `execution_stages()` / `dag.topological_stages`
- [ADR-034 — Adoption-First Import](adr-034-adoption-first-import.md) — emits the DAG this ADR runs; the importer must populate `outputs_schema` faithfully for typed hand-offs (Consequences, Negative)
- [ADR-005 — Workflow Concept Retirement; Harness as Replacement](adr-005-workflow-concept-retirement-harness-as-replacement.md) — the L77 orchestrator promise (decision 7) and the one-harness-one-governance-unit / "no workflow engine" invariants (Alternative B)
- [ADR-002 — OHM as Canonical Manifest Format](adr-002-ohm-as-canonical-manifest-format.md) / [ADR-003 — Platform-as-Code, Actors-as-Harnesses](adr-003-platform-as-code-actors-as-harnesses.md) — orchestrators are `core` capabilities, never platform code
- The reshaped seams (read, by path): `execution-engine-service/.../services/roundtable_service.py:117,145,157,167,181,327,336` (degenerate round-table); `.../services/job_service.py:160,282,319` + `.../repositories/job_repository.py:130` (durable dispatch/retry/CAS); `.../services/task_service.py:45,52,91` (HITL task board); `harness-runtime-service/.../domain/loop/tool_use.py:92,191,193` (dispatch seam) + `.../domain/policy.py:39,47` (`PolicyEnvelope`/`gated_bindings`); `packages/ohm/.../capabilities.py:17,27` (ceiling guard) + `.../dag.py` (`topological_stages`)
- [ADR index](index.md)

## Revision history

| Date | Change |
| --- | --- |
| 2026-06-20 | Initial draft (Proposed). Decides the team runtime spine: (1) the orchestration-agent contract "choice is prose, mechanics are coded" (controller decides routing/completion; budgets/gates/barriers/ceiling are coded); (2) the three orchestrators as `core` capabilities reshaping `roundtable_service.drive` (sequential typed-hand-off successor, parallel `asyncio.gather` + real fan-in barrier driving `fan_out`, conditional predicate routing) with all/quorum/termination barrier semantics; (3) the typed `HandoffEnvelope` in `packages/ohm` replacing `_render_context`; (4) the coordination-media taxonomy + §6 decision guide; (5) dispatch-time `assert_capability_allowed` at `tool_use.py:193`, no path widens a ceiling; (6) the blocking-gate-node (non-opt-in for book) on the task board; (7) the ADR-005 L77 built-status note + ratifying ADR-033's retired-vs-deferred ledger; (8) scope/CUT (B2 controller opt-in, A2A/HITL-SLA/D5 out). R7 epic E3, child issues #419–#424. Pending Reza/CTO. |
