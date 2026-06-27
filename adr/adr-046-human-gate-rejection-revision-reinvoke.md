---
title: "ADR-046 — Human-gate rejection → revision → re-invoke: wiring ADR-035's edit-then-advance (typed gate decision, scoped re-run, bounded loop)"
---

# ADR-046 — Human-gate rejection → revision → re-invoke

## Status

| Field | Value |
| --- | --- |
| Status | Proposed |
| Date | 2026-06-27 |
| Approved by | — (pending Reza/CTO) |
| Supersedes | None |
| Superseded by | None |
| Driving artifact | The #440 book-GO end-to-end run (the studio Team Harness, 7-gate A–G human sequence) — the first run on which a human gate actually paused, and the first on which a reviewer pressed *reject* and discovered the run was over with nowhere to put the feedback. Parent: the team-run completion / re-route line ([ADR-042](adr-042-team-run-completion-non-abort.md) completion, [ADR-043](adr-043-conductor-recalibration-reroute.md) recalibration / #553). |

## Context

The #440 book-GO run is the first time a Team Harness (ADR-031) drove a real human gate to a pause and back. The studio book's charter imports to an ordered chain of `kind: human` blocking nodes — Gate D (a barrier before production), Gate E (the author's upload gate) and so on, the A–G sequence (ADR-034 §6, ADR-035 §6). On that run the human reviewer reached a gate, looked at the draft, and wanted to say *"this chapter is wrong, redo it with the bible's voice."* The platform had no way to carry that. The only thing the human can send is the verb `approve` or `reject`, and `reject` ends the run. The reviewer's intent — the single most valuable signal a human gate exists to capture — was thrown away, and the team's work (every completed member upstream of the gate) went to a terminal `REJECTED` with it.

This is the gap [ADR-035](adr-035-coordination-control-and-media.md) §6 named but did not close. ADR-035 declared the blocking-gate-node supports "approve / **reject** / **edit-then-advance**" (`adr-035-…:104`), but only two of the three are wired, and reject is wired as a dead-end. The current state, grounded:

- **The gate channel carries a bare token.** The wire DTO is `gate_decisions: dict[str, Literal["approve", "reject"]]` at both create (`engine_schemas.py:289`) and advance (`engine_schemas.py:304`). There is **no field for an edited payload and no field for rejection feedback** — `edit-then-advance` has no data path at all, and `reject` cannot carry a reason.
- **Reject is terminal.** The orchestrator reads `gate_decisions[role]`; any role mapped to `"reject"` returns `status="rejected"` and downstream `depends_on` members never run (`packages/ohm/src/oraclous_ohm/orchestrate.py:193-202`). The service maps that straight to a terminal row state via `_STATUS_TO_STATE = {"completed": "SUCCEEDED", "paused": "PAUSED", "rejected": "REJECTED"}` (`team_run_service.py:53`, applied at `:536`). A `REJECTED` run is over; there is no re-drive path off it.
- **Approve already resumes correctly, and idempotently.** `advance()` merges the new decision into the persisted decisions (`merged = {**row.gate_decisions, **gate_decisions}`, `team_run_service.py:428`), CAS-transitions `PAUSED → QUEUED` under a row lock (`transition(... allowed_from={"PAUSED"})`, `team_run_service.py:430` over `team_run_repository.py:92`'s `with_for_update()`), and re-enqueues the worker. On resume `_drive` seeds `completed=dict(row.results)` (`team_run_service.py:325`), and the orchestrator reuses those members without re-dispatching them (`if role in done: return`, `orchestrate.py:132`; seeded into `results` at `orchestrate.py:121`) — the "G-D" idempotency that makes a resume not re-run finished work. **The durable, CAS-guarded, org-scoped resume substrate is already right.** What is impoverished is only the *decision vocabulary* the human can put through it.

So the team has the half that is hard (a durable, idempotent, org-scoped checkpoint-and-resume) and lacks the half that is a small typed extension (a third decision that carries feedback and re-runs the right slice). Every leading agent framework treats reject as a route back into the loop, not a dead-end, and carries the human's correction as a typed payload:

- **LangGraph** — a node `interrupt()`s, the graph checkpoints, and `Command(resume=<decision>)` resumes. `reject` is **explicitly non-terminal**: it "routes back to the model with context" — the rejection message "is added to the conversation as feedback to help the agent understand why the action was rejected and what it should do instead." `edit` modifies the proposed call before it runs. (LangChain — *Human-in-the-loop*.)
- **CrewAI** — `@human_feedback` collapses free-text into a declared outcome (`approved` / `rejected` / `needs_revision`); a `needs_revision` `@listen(or_("generate", "revise"))` self-loop re-runs the same producing method, which reads `self.last_human_feedback` to guide the redo, "until the human approves or rejects." (CrewAI — *Human Feedback in Flows*.)
- **Temporal** — the workflow sleeps durably on a signal (`approve` / `reject` / edit-the-prompt), with explicit state (`submitted → acknowledged → approved | rejected | timed_out`), **idempotent** handlers ("humans click submit twice"), and the decision **durably stored** so a downstream retry never re-asks. "Request revisions" signals an edited prompt and the workflow **regenerates** the producing step. (Temporal — *Durable Human-in-the-Loop*.)
- **AutoGen** — `UserProxyAgent` injects the human's reply as the next conversational message; the loop continues. Most flexible, least typed/governable.

The cross-framework consensus is sharp: **reject is almost never a dead-end** (a separate hard *abort* exists, distinct from "this output is wrong"); the human's correction is a **captured typed payload**, not a bare verb; resume is **re-entrant, checkpoint-based, idempotent**; the loop is **bounded**, not infinite; and the **unit of redo is the rejected producer's sub-tree, not the whole run**. Oraclous already satisfies the re-entrant/idempotent/checkpoint half; this ADR adds the typed decision, the bounded scoped re-run, and keeps a real terminal-reject as an explicit, separate option.

This ADR decides exactly that wiring: how a gate decision carries feedback and an edited payload, what a `revise` decision re-runs (and reuses), how the loop stays bounded, where the edit is captured and persisted on the durable checkpoint, the cascade semantics over the DAG, and that terminal-`REJECTED` survives as a distinct, deliberate choice.

## Decision

### 1. A third gate decision — `revise` — alongside `approve` and `reject`; the channel becomes typed

The human-gate decision vocabulary is **three** verbs, each explicit (never LLM-inferred):

| Verb | Meaning | Run outcome |
| --- | --- | --- |
| `approve` | The gated output is accepted. | Resume past the gate; downstream `depends_on` members run. **Unchanged from today.** |
| `revise` | The gated output is wrong; redo it with the attached feedback / edit. | Re-run the rejected producer's sub-tree with the feedback threaded in; pause again at the gate when the redo completes (bounded — decision 4). **This is ADR-035's edit-then-advance, wired.** |
| `reject` | Kill this run definitively. | Terminal `REJECTED` — the current behavior, kept as an **explicit, separate** choice (decision 6). |

The gate channel is promoted from a bare token to a small typed object. Where today the value is a `Literal["approve","reject"]`, it becomes a `GateDecision`:

```
GateDecision {
  decision:       approve | revise | reject     # the explicit verb (never LLM-inferred)
  feedback:       str = ""                        # the human's correction, threaded to the re-run
  edited_payload: dict | None = None              # an inline edit of the producer's output (edit-then-advance)
}
```

The wire DTOs `CreateTeamRunRequest.gate_decisions` (`engine_schemas.py:289`) and `AdvanceTeamRunRequest.gate_decisions` (`engine_schemas.py:304`) move from `dict[str, Literal["approve","reject"]]` to `dict[str, GateDecision]`. **Backward-compatible parse:** a bare string `"approve"`/`"reject"` (the v1 wire shape) is accepted and normalized to `GateDecision(decision=<str>)`, so a v1.0/v1.1 client and every existing test keep working — additive, never a breaking change (the ADR-031 §6 additive-evolution discipline).

The verb is **explicit and typed**, not inferred. We deliberately diverge from CrewAI's LLM-router-collapses-free-text design (alternative C): for a governed, fail-closed, org-scoped gate the decision mechanic must be coded, not a model's guess at intent ("choice is prose, mechanics are coded" — ADR-035 §1). Free-text `feedback` rides *alongside* the typed verb, never in place of it.

### 2. `revise` re-runs the rejected producer's sub-tree — reusing the resume substrate, not a new engine

The orchestrator's gate read (`orchestrate.py:182-202`) gains a third arm. Today: `undecided → paused`, `"reject" → rejected`. New: a gate whose decision is `revise` is **neither paused nor terminal** — it triggers a *scoped re-drive*.

The unit of redo is **the rejected producer's sub-tree**, never the whole run — the cross-framework consensus (LangGraph re-plans the producer; CrewAI self-loops the producing method; Temporal regenerates the producing step; none re-run the whole DAG). On Oraclous's DAG this is precise and mechanical:

- The producer of a gate is the gate member's `depends_on` upstream (the member(s) whose output the human just judged). Call that set **R** (the directly-rejected producers).
- The **invalidation set** is R ∪ {every member transitively downstream of R *up to and including the gate*} — i.e. the slice of `execution_stages()` between the producer and the gate, recomputed over the `depends_on` topology. Members *outside* that slice (sibling branches the human did not touch, and everything already past an earlier approved gate) are **untouched**.
- Re-drive reuses the **existing `completed=` seed machinery inverted**: instead of seeding *all* prior results, the resume seeds `completed = row.results − invalidation_set`. The invalidated members are absent from `done`, so `run_member` dispatches them again (`orchestrate.py:131-133`); every other member is present in `done` and is reused, not re-run (`orchestrate.py:132`). **No new execution path** — it is the same idempotency seam (`team_run_service.py:325`, `orchestrate.py:121`) driven with a pruned seed.
- The gate's own decision for this round is **cleared** (the gate returns to undecided), so when the re-driven slice completes, the run **pauses again at the same gate** with the fresh output for the human to judge. This is the revise *loop*: produce → gate → revise → re-produce → gate, bounded by decision 4.

This is the same shape the #553 recalibration / re-route substrate ([ADR-043](adr-043-conductor-recalibration-reroute.md)) uses to get a stalled team unstuck — invalidate a slice, re-seed, re-drive — and `revise` is built **on that substrate**, not a parallel mechanism. Where the conductor decides *autonomously* to re-route on a stall, `revise` is the **human-initiated** entry to the identical re-drive: one re-drive primitive, two triggers (the conductor and the human gate).

We do **not** stand up a workflow/DAG engine to do this (alternative A) — that is exactly what ADR-005 retired and ADR-035 alternative B re-rejected. The re-run rides the harness/orchestrator the team already is.

### 3. The feedback / edit is threaded to the re-run producer as a typed inbound `HandoffEnvelope` — and persisted on the checkpoint

The human's correction reaches the re-running producer through the **existing typed hand-off contract** (ADR-035 §3, `packages/ohm/src/oraclous_ohm/envelope.py`), not a side channel. When the invalidated producer is re-dispatched, the orchestrator synthesizes an inbound `HandoffEnvelope` *from the gate to the producer* carrying the revision:

```
HandoffEnvelope {
  from_role:       <gate role>            # the human gate that requested the revision
  to_role:         <producer role>        # the member being re-run
  objective_slice: "revision: <feedback>" # the human's correction, made the redo's sub-goal
  payload:         { feedback, edited_payload, revision_round }
  provenance_ref:  <the gate decision>    # one provenance stream
}
```

This is the LangGraph default — **auto-inject** the rejection message as context so the producer self-corrects, rather than CrewAI's manual `self.last_human_feedback` read. The producer member does not have to know it is in a redo; it receives a typed inbound envelope like any other `depends_on` input. **Isolation holds unchanged:** the envelope carries *data only, never capability* (`envelope.py:7,22`) — a revision can never widen the producer's `tools[]` ceiling (ADR-032 §1 / ADR-035 §5). When `edited_payload` is present (a literal edit-then-advance — the human hand-corrected the output), the orchestrator can short-circuit the re-dispatch and seed the edited value directly as the producer's result, then re-pause at the gate for confirmation; the choice between *re-run with feedback* and *accept the edit verbatim* is the human's, expressed by which field they fill.

**Where it is captured and persisted (the checkpoint).** The durable row `EngineTeamRun` (`models/team_run.py`) is the checkpoint. The `gate_decisions` JSONB column (`team_run.py:41`) already persists the per-gate decision; it now persists the full `GateDecision` object (decision + feedback + edited_payload) instead of a bare string — a JSONB column, so this is a value-shape change, **not a migration**. A new nullable `revision_rounds: dict[str, int]` JSONB column on the same row tracks the per-gate revise count for the bound (decision 4); it is set through `transition(**fields)`'s generic `setattr` loop (`team_run_repository.py:98`), so the repository needs no signature change. Persisting on the row means a revise survives a worker crash, a redelivered Celery task, and a request retry — the same durability the approve path already has.

### 4. The revise loop is bounded — coded, fail-closed to terminal `REJECTED`

A human must not be able to loop a producer forever against the **pooled** team budget (ADR-031: one Team Harness = one budget surface). The revise loop is bounded by a coded ceiling, in the spirit of CrewAI's "until approve/reject" and Temporal's timer bounds, and in the exact spirit of ADR-035 §1 ("choice is prose, the ceiling is coded"):

- A per-gate **`max_revisions`** declared on the manifest — reusing the `OHMTermination` shape already in the schema (`manifest.py:151-159`, `max_rounds`/`max_wall_seconds`), scoped to the gate. Default is a small finite number (proposed: 3), never unbounded.
- On the `N`-th `revise` that would exceed `max_revisions`, the run **fail-closes to terminal `REJECTED`** with an `error_message` recording revision exhaustion. Fail-closed (ADR §3.5): the ambiguous "they keep rejecting and won't approve" state resolves to *stop*, not *loop*.
- The pooled `OHMBudget` (ADR-031) is the **outer** bound regardless: every re-run spends from the *same* team envelope (`max_tokens_total` / `max_sub_runs` / `max_usd_total`, `manifest.py:236-246`), so a revise loop can never escape the team's one budget surface — it is bounded by *both* `max_revisions` *and* the pooled budget, whichever bites first. There is no per-revision fresh budget.

### 5. Cascade semantics — only the invalidated slice; approved gates upstream are sealed

Revise must not silently undo work the human already blessed. The cascade is scoped and fail-closed:

- **Downstream of the gate** has not run yet (the gate is a structural barrier — `orchestrate.py:182-192` blocks dependents until the gate is decided), so there is nothing downstream to invalidate; it simply runs once the re-produced output is finally `approve`d.
- **Upstream of the gate, inside the producer slice** (set R and members between R and the gate) is invalidated and re-run (decision 2).
- **Earlier approved gates are sealed.** A member whose output already passed an *earlier* approved human gate is **not** re-run by a *later* gate's revise — the invalidation set is bounded by the nearest upstream approved gate. (Rationale: the human already accepted that output at its own gate; a later revise is about the later producer, not a license to silently re-run sealed work. If the human truly wants to redo sealed work, they revise at *that* gate.)
- **Sibling branches** (members the gate does not `depends_on`, even if they ran concurrently) are untouched — their cached results stay in the `completed=` seed.
- **Side effects already applied** by an invalidated member are the one genuinely hard case (a member that already wrote to the file-native workspace or ingested to the graph before the gate). For E-this-ADR we **re-run forward over them** (the file-native blackboard and graph are the trusted per-run substrate the team mutates in place — `workspace_root`/`graph_id` are re-threaded to the re-run, `team_run_service.py:491-492`), and we **note compensation/saga (Temporal's model) as explicitly deferred**: a member that performs an *irreversible external* side effect before a gate should sit *after* its gate, not before it, and the importer/dry-run (ADR-034 §7 / O8) is where that ordering is surfaced. No automatic rollback is attempted in this ADR.

### 6. Terminal `REJECTED` survives as an explicit, separate choice

Unlike LangGraph (where reject ≡ re-plan), Oraclous keeps a **real terminal reject** — and this is a deliberate divergence. Oraclous is an org-scoped, multi-tenant product where a user must be able to *kill* a run definitively (a misfired run, a run on the wrong data, a run the user simply wants gone). So the platform provides **both**:

- `revise` — the new default for "this output is wrong, redo it" (route back into the loop).
- `reject` — terminal `REJECTED`, the **current** orchestrator behavior (`orchestrate.py:193-202`) and row state (`team_run_service.py:53`), kept verbatim, reached only by the *explicit* `reject` verb.

We do **not** collapse them. The distinction is the whole point of the framework consensus: "this is wrong" (revise) and "stop this run" (abort) are different intents, and conflating them either strands feedback (today's bug) or removes the user's ability to kill a run (over-correcting). The `revise` vs `reject` choice is the human's, explicit and typed.

### 7. Re-grade after revise — close the evaluation loop

Because the run already grades its completed output at the `success_criteria` flow-evaluation gate (`_grade_gate`, `team_run_service.py:353-416`; ADR-037 / #477), a revised-and-finally-approved run re-runs that grader on the **new** output — the run only reaches `_grade_gate` when `result.status == "completed"` (`team_run_service.py:529-531`), and a revise that finally converges to `approve` reaches completion through the normal path, so the grader naturally re-runs on the revised output. No special wiring: the existing gate grades whatever the converged output is. This closes a loop none of the surveyed frameworks close (CrewAI's `learn=True` is the nearest analog). As a forward note (out of scope here, flagged for the consciousness/Learn line): the human's `feedback` is a high-value correction to write to the ADR-027 `:Memory` store so the producer improves on future *pre-gate* output — but that is ADR-043/ADR-027 territory, not this ADR.

### 8. Scope / CUT

- **In:** the `revise` verb + typed `GateDecision` (feedback + edited_payload) on the wire and the checkpoint; the scoped sub-tree re-drive on the existing resume substrate; the auto-injected revision `HandoffEnvelope`; the coded `max_revisions` bound fail-closing to `REJECTED`; the cascade semantics; the kept terminal `reject`; re-grade-on-converge.
- **Out / deferred:** automatic **saga / compensation** rollback of already-applied irreversible side effects (decision 5 — note only; correct ordering is the importer's job). **SLA / timeout / auto-action** on a human who never decides (kept opt-in, consistent with ADR-035 §8 D4). **Writing feedback to the `:Memory` Learn store** (decision 7 — ADR-027/ADR-043 territory). An **LLM router** that infers the verb from free text (decision 1 — explicitly rejected, alternative C).

## Alternatives considered

### A. Build a workflow/DAG engine to model revise as a graph re-entry
Stand up a dedicated workflow engine whose scheduler can re-enter a node with edited state (LangGraph's time-travel `update_state` + fork-checkpoint shape, ported wholesale). **Rejected** — [ADR-005](adr-005-workflow-concept-retirement-harness-as-replacement.md) retired the workflow concept and ADR-035 (alternative B) re-rejected a generic engine: a team is a Team Harness interpreted by the runtime, and re-entry must ride the harness/orchestrator, not a second control plane that forks governance/budget/provenance. The scoped re-drive (decision 2) gets the same re-entry on the *existing* `completed=`/`advance`/CAS substrate, no engine.

### B. Make reject re-plan with feedback and have no terminal option (the LangGraph default)
Adopt LangGraph's semantics directly: `reject` is never terminal, it always routes back to the producer with the rejection message. **Rejected** — Oraclous is org-scoped and multi-tenant; a user must be able to *kill* a run definitively (decision 6). Collapsing reject into re-plan removes that ability. We take LangGraph's *non-terminal, feedback-carrying* idea but bind it to a **new** verb (`revise`) and keep `reject` terminal — both, explicitly chosen.

### C. An LLM router collapses free-text human feedback into the outcome (the CrewAI default)
Let the human type free text and have a model classify it into `approve`/`revise`/`reject` (CrewAI's `emit=[…]` router). **Rejected** — for a governed, fail-closed gate the decision mechanic must be **coded**, not a model's inference of intent ("choice is prose, mechanics are coded" — ADR-035 §1). A misclassification could approve a run the human meant to reject, or vice versa — exactly the class of failure the coded gate exists to prevent. We take CrewAI's *captured-feedback* and *self-loop* ideas (`feedback` rides alongside the verb; revise re-runs the producer) but the verb itself is explicit and typed.

### D. Re-run the whole DAG on revise (re-execute everything)
On any revise, discard all results and re-drive the entire team from the start with the feedback in state. **Rejected** — it violates the cross-framework consensus that the unit of redo is the rejected producer's sub-tree, it re-runs sealed work the human already approved at earlier gates (decision 5), and it burns the pooled budget (ADR-031) on members that did not change. The scoped invalidation (decision 2) re-runs only what the human's judgment actually invalidated.

### E. Carry feedback in a side channel (a separate `/feedback` endpoint or a free-string column), not the typed envelope
Add a separate feedback field/endpoint decoupled from the hand-off contract. **Rejected** — it forks the inter-member medium into two shapes (typed envelopes for normal hand-offs, an ad-hoc string for revisions) and breaks the one-provenance-stream / one-typed-contract invariant (ADR-035 §3). Threading the revision as a `HandoffEnvelope` (decision 3) keeps every inter-member transfer — including a human's correction — inside the single typed, schema-checked, capability-free contract.

## Consequences

### Positive
- **The book-GO gap closes.** A reviewer at a book gate can say "redo this with the bible's voice," and the run re-produces the gated slice with that feedback and re-pauses for judgment — the #440 trigger is fixed. ADR-035 §6's "edit-then-advance" is wired, not just named.
- **Reject stops being a feedback black hole.** The single most valuable signal a human gate captures — *why* this is wrong and *what to do instead* — is now carried as typed data, persisted on the checkpoint, and threaded to the re-run, matching the LangGraph/CrewAI/Temporal consensus.
- **Reshape, not rebuild.** `revise` rides the *existing* durable resume substrate (`advance` CAS `PAUSED→QUEUED`, `completed=` seed, idempotent reuse) and the *existing* typed `HandoffEnvelope` and the #553 re-drive primitive. The new surface is a typed value shape on a JSONB column, a third arm in the gate read, and a pruned re-seed — small, low-risk PRs, no migration for the decision shape.
- **The team stays one governed unit.** Revise spends from the one pooled `OHMBudget`, can never widen a ceiling (data-only envelope), is bounded by a coded `max_revisions`, and fail-closes to terminal `REJECTED` on exhaustion — a wrong/abusive human loop can no more exceed governance than a wrong prose route can (the ADR-035 §1 invariant extends to the human channel).
- **The evaluation loop closes.** A revised-and-approved run is re-graded at the flow-evaluation gate (ADR-037) on its *new* output — something the surveyed frameworks do not do.

### Negative
- **The decision shape is a (compatible) breaking-shaped change.** `gate_decisions` values move from `Literal["approve","reject"]` to a typed `GateDecision`. The backward-compatible parse (decision 1) keeps v1 clients/tests working, but every reader of `gate_decisions` (`orchestrate.py`, `team_run_service.py`, the route) must handle both shapes during the transition — a careful, well-tested normalization seam.
- **Scoped invalidation is the subtle part.** Computing R ∪ {slice up to the gate}, bounded by the nearest upstream approved gate, over the `depends_on` topology must be exactly right — too wide re-runs sealed work and burns budget; too narrow leaves stale upstream output feeding the redo. This is the one genuinely new algorithm and needs adversarial tests (diamond dependencies, multi-gate chains, sibling branches).
- **Side effects before a gate are re-run forward, not compensated.** A member that mutated the file-native workspace or the graph before its gate is re-run over that mutated substrate (decision 5). For idempotent/overwriting writes this is fine; for an irreversible external side effect it is a latent footgun until saga/compensation lands — mitigated only by the convention that irreversible-side-effect members belong *after* their gate, which the importer/dry-run must surface.
- **Bounded loops can still frustrate a human.** A human who keeps revising hits `max_revisions` and the run terminates `REJECTED` — correct fail-closed behavior, but it must be surfaced clearly (the `error_message` and the O4 status) so a user understands *why* their run stopped rather than experiencing a silent dead-end.

## Implementation notes

This ADR is a slice under the team-run completion / re-route line ([ADR-042](adr-042-team-run-completion-non-abort.md) / [ADR-043](adr-043-conductor-recalibration-reroute.md), #553), decomposed as:

- **`packages/ohm`** — add the `GateDecision` type (decision 1) beside the envelope/manifest it relates to; add the third gate arm in `run_team` (`orchestrate.py:182-202`): a `revise` decision computes the invalidation slice (a pure function over `execution_stages()` / `depends_on`, bounded by the nearest upstream approved gate — decision 5), re-seeds `completed = results − invalidated`, synthesizes the revision `HandoffEnvelope` (decision 3) for each re-run producer, and re-pauses at the gate; the `max_revisions` bound fail-closing to `rejected` (decision 4). Keep the `"reject"` arm verbatim (decision 6) and the backward-compatible string-or-object parse.
- **execution-engine-service** — `engine_schemas.py:289,304`: widen `gate_decisions` to `dict[str, GateDecision]` with the compat parse; `team_run_service.advance` (`:418-441`) and `_drive` (`:443-544`): persist the full `GateDecision` in the `gate_decisions` JSONB and the new `revision_rounds` count through `transition(**fields)` (`team_run_repository.py:98`, no signature change); on a `revise`, drive the scoped re-seed instead of the full `completed=dict(row.results)` (`:325`). `models/team_run.py`: the new nullable `revision_rounds` JSONB column (additive; the `gate_decisions` value-shape change is migration-free — it is already JSONB).
- **The flow-evaluation re-grade** (decision 7) needs **no new code** — a converged revise reaches `_grade_gate` through the existing `result.status == "completed"` path (`team_run_service.py:529-531`).
- **Tests** (TDD per ADR-010) must cover: revise re-runs only the invalidated slice (diamond + multi-gate); sealed earlier-approved gates are not re-run; sibling branches untouched; the revision envelope reaches the producer and is data-only (no ceiling widening — ADR-032); `max_revisions` exhaustion fail-closes to `REJECTED`; the pooled budget binds across revise loops; backward-compatible parse of the v1 string shape; idempotent advance (a duplicate `revise` is a no-op on the same round). The deployed-stack e2e drives the book-GO 7-gate run through the gateway: reach a gate, POST `advance` with `{decision: revise, feedback: …}`, assert the producer re-runs and the run re-pauses, then `approve` and assert completion + re-grade.

## References

- [ADR-035 — Coordination Control & Media: the team runtime spine](adr-035-coordination-control-and-media.md) — §6 named "approve / reject / **edit-then-advance**" (`:104`) this ADR wires; §1 "choice is prose, mechanics are coded"; §3 the typed `HandoffEnvelope` this ADR threads the revision through; §5 the data-only / no-ceiling-widening isolation; §8 D4 the opt-in HITL-SLA this ADR keeps out
- [ADR-042 — Team-run completion (non-abort)](adr-042-team-run-completion-non-abort.md) / [ADR-043 — Conductor: recalibration & re-route](adr-043-conductor-recalibration-reroute.md) — the parent completion/re-route line; the #553 recalibration substrate (invalidate-slice + re-seed + re-drive) this ADR's `revise` reuses (human-triggered vs conductor-triggered, one primitive)
- [ADR-031 — OHM v1.1 Team Manifest](adr-031-ohm-v1.1-team-manifest.md) — the pooled `OHMBudget` (one Team Harness = one budget surface) that bounds revise loops (`manifest.py:236-246`); `OHMTermination` shape reused for `max_revisions` (`manifest.py:151-159`); additive-versioned evolution discipline (the compat parse)
- [ADR-032 — Capability-Absence as a Structural Gate](adr-032-capability-absence-structural-gate.md) — the immutable `tools[]` ceiling a revision can never widen (the envelope is data-only)
- [ADR-034 — Adoption-First Import](adr-034-adoption-first-import.md) — §6 the book's 7-gate A–G sequence → `kind: human` blocking nodes; §7/O8 the dry-run that should surface irreversible-side-effect ordering (decision 5)
- [ADR-037 — Flow-level Evaluation, Named Batteries, Run-Tree](adr-037-flow-level-evaluation-named-batteries-run-tree.md) — the `success_criteria` flow-evaluation gate (`_grade_gate`, `team_run_service.py:353-416`) re-run on a converged revise (decision 7)
- [ADR-005 — Workflow Concept Retirement; Harness as Replacement](adr-005-workflow-concept-retirement-harness-as-replacement.md) — "no workflow engine"; revise rides the harness/orchestrator (alternative A)
- [ADR-027 — Agent Memory (Ebbinghaus Store)](adr-027-agent-memory-ebbinghaus-store.md) — the `:Memory` Learn store the human's correction should later feed (decision 7, forward note — out of scope here)
- The wired/reshaped seams (read, by path): `packages/ohm/src/oraclous_ohm/orchestrate.py:121,131-133,182-202` (gate read, reject→terminal, `completed=` resume seed); `packages/ohm/src/oraclous_ohm/envelope.py:7,22,51-77` (the typed, data-only `HandoffEnvelope` + `build_handoff`); `packages/ohm/src/oraclous_ohm/manifest.py:122-148,151-159,236-246` (`OHMMember` human kind, `OHMTermination`, `OHMBudget`); `services/execution-engine-service/.../services/team_run_service.py:53,325,418-441,443-544,529-531` (`_STATUS_TO_STATE`, resume seed, `advance`, `_drive`, `_grade_gate` gating); `.../repositories/team_run_repository.py:72-102` (generic `transition(**fields)` CAS); `.../models/team_run.py:41,44,46,75` (the durable checkpoint: `gate_decisions`/`results`/`paused_at`/`verdict` JSONB); `.../schema/engine_schemas.py:277-304` (the wire DTOs — the `Literal["approve","reject"]` this ADR widens); `.../routes/team_run_routes.py:121-134` (the advance route); `.../services/task_service.py:91-96` (the HITL `approve` seam — note the precedent `decision_reason: str | None`)
- [ADR index](index.md)

## Revision history

| Date | Change |
| --- | --- |
| 2026-06-27 | Initial draft (Proposed). Decides the human-gate rejection→revision→re-invoke flow, wiring ADR-035 §6's named-but-unwired edit-then-advance: (1) a third typed gate decision `revise` alongside `approve`/`reject`, the channel promoted from `Literal["approve","reject"]` to a `GateDecision{decision,feedback,edited_payload}` with a backward-compatible string parse; (2) `revise` re-runs only the rejected producer's sub-tree on the existing `completed=`/`advance`/CAS resume substrate (reusing the #553/ADR-043 re-drive primitive, human-triggered), re-pausing at the gate; (3) the feedback/edit threaded to the re-run producer as an auto-injected data-only `HandoffEnvelope`, captured + persisted on the durable `EngineTeamRun` checkpoint (JSONB `gate_decisions` value-shape change, migration-free; new nullable `revision_rounds`); (4) a coded per-gate `max_revisions` bound fail-closing to terminal `REJECTED`, with the pooled `OHMBudget` as the outer bound; (5) scoped cascade — only the invalidated slice up to the gate, earlier approved gates sealed, siblings untouched, side-effects re-run-forward with saga/compensation deferred; (6) terminal `reject` kept as an explicit, separate choice (diverging from LangGraph's reject≡re-plan); (7) re-grade-on-converge at the ADR-037 flow-evaluation gate; (8) scope/CUT (saga, HITL-SLA, :Memory-write, LLM-router all out). Grounded in the #440 book-GO trigger and the current-state file:line. Pending Reza/CTO. |
