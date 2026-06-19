---
title: "ADR-033 — Orchestrator Capabilities Status (ADR-005 L77) and Original-Primitive Retirement"
---

# ADR-033 — Orchestrator Capabilities Status (ADR-005 L77) and Original-Primitive Retirement

## Status

| Field | Value |
| --- | --- |
| Status | Proposed |
| Date | 2026-06-19 |
| Approved by | pending (Reza / CTO) |
| Supersedes | None (status/governance ADR; does not supersede ADR-005, it closes an un-ADR'd promise inside it) |
| Superseded by | None |
| Driving artifact | [Team-of-Agents North-Star Lock](../product/team-of-agents-north-star-lock.md) (§8 item 8) |

## Context

[ADR-005](adr-005-workflow-concept-retirement-harness-as-replacement.md) retired the v0 "workflow" concept and collapsed all orchestration into "a harness whose entrypoint capability orchestrates other capabilities." In doing so its implementation notes (**ADR-005 line 77**) made a concrete promise:

> *"The platform ships a small set of baseline orchestrator capabilities in `core` (sequential, parallel, conditional)."*

The team-of-agents architecture audit (run **`wf_693afa65-500`**, the 20-agent cross-corpus review behind `team-of-agents-capability-design.md`) found that this promise was **never given an ADR, never tracked as a deliverable, and never built.** The only multi-actor primitive that runs today is a degenerate sequential round-table (`roundtable_service.drive` — `actor = actors[turn % n]`, synchronous per-turn await, no `asyncio.gather`, "fan-in" = `transcript.append`, "merge" = `final = transcript[-1]`). `sequential` exists only in this degenerate form; `parallel` and `conditional` do not exist at all. The promise sat as an untracked aside for the platform's most load-bearing missing primitive.

The same audit found a deeper, **three-way silent divergence** between (a) the *original vision* (`ORACLOUS_AGENT_PLATFORM_ARCHITECTURE.md` — a graph-resident `:Agent` team ontology, a team permission model, cascading per-agent budgets), (b) the *current docs* (ADR-005's "one harness = one governance/budget surface"), and (c) the *shipped code* (neither the team ontology nor a real budget envelope exists). Because no ADR ever recorded which original team-substrate primitives were **retired** versus **deferred**, every later reader had to re-derive the answer, and the design kept re-litigating decisions that were in fact already made (e.g. ADR-029 reversed the graph-resident team ontology; ADR-005 ruled out cascading per-agent budgets — but neither retirement was recorded *as such* against the original vision).

This is a **status + governance ADR**: it does not introduce a new technical mechanism. It (1) converts the ADR-005 L77 promise from an untracked aside into a **tracked, committed deliverable**, and (2) records, once and authoritatively, the **retired-vs-deferred ledger** of the original team-substrate primitives — to end the divergence the audit named at nearly every pillar.

## Decision

### Part 1 — The three baseline orchestrator capabilities are TRACKED, committed deliverables

The three orchestrator primitives promised in ADR-005 L77 — `sequential`, `parallel`, `conditional` — are **committed deliverables of the R7 "the product loop closes" release, epic E3 (the runtime spine)**, corresponding to design item **B1** in `team-of-agents-capability-design.md`. They are no longer an untracked implementation aside; they are scoped, owned, and gated.

Concretely, the contract for each (the shape an implementing PR must satisfy):

* They ship as **`core`-registry capabilities** (ADR-002/ADR-003 — orchestration behaviour is a *capability*, never platform code baked into a service), addressed as `orchestrate.sequential`, `orchestrate.parallel`, `orchestrate.conditional`.
* Each receives the **Team Manifest (OHM v1.1) + current run state**, dispatches the next member set, awaits per its kind, and returns a **structured stage result** (not a flattened transcript string).
* **`orchestrate.parallel`** runs members concurrently (`asyncio.gather`) and **blocks on a real fan-in barrier** until all branches complete (or a quorum / termination rule fires) — replacing the current `transcript.append` pseudo-fan-in. Its merge is a first-class reducer (design B3 `aggregate.reduce` / `aggregate.synthesize`), not last-writer-wins.
* **`orchestrate.conditional`** routes on a predicate evaluated over prior members' typed results.
* **`orchestrate.sequential`** is the structured, typed-hand-off successor to the degenerate round-table (design B5 envelope `{from_role, to_role, objective_slice, payload, provenance_ref, cursor}`), not the `transcript[-1]` round-robin.
* All three are governed under the **one-harness-one-governance-unit** invariant (ADR-005 / design §2.1): one budget surface, one audit/provenance stream, one ReBAC envelope for the whole team run. The orchestrator dispatches sub-runs; it does not create independent governance units.
* They are constrained by the **R4 T3-M1 guardrail**: an orchestrator may route only to members/capabilities **declared in the manifest** — never escalate a capability the manifest did not grant (consistent with the North-Star Lock's capability-absence gate).

`sequential/parallel/conditional` are the *mechanics*; the prose-interpreting **Orchestration Agent** that *chooses* among them (design B2) is a separate deliverable under a separate ADR (the coordination-control ADR, lock §8 item 2 / design §11 item 2). This ADR commits only the three mechanical primitives.

### Part 2 — The retired-vs-deferred ledger of original team-substrate primitives

The following is now the **authoritative record** of what the original vision's team substrate became. No later design, doc, or PR may silently re-introduce a RETIRED primitive or treat a DEFERRED one as shipped.

**RETIRED** — explicitly removed from the platform model; do not re-introduce without a new superseding ADR:

| Original primitive | Retired by | Why retired |
| --- | --- | --- |
| **Graph-resident `:Agent` team ontology** — agents and team structure modelled as first-class nodes/edges in the Neo4j tenant graph | **[ADR-029](adr-029-workspace-harness-binding.md)** (reversed it: a harness is a `kind:harness` capability in the capability registry; the workspace↔harness relation is a **curation edge in the registry**, not a graph-substrate association) | The graph substrate holds *tenant knowledge content*; a control-plane team/agent ontology does not belong there. Modelling the team in the graph splits harness ownership away from the registry that owns harnesses and risks the control-plane edge becoming a backdoor data-access path. A team is a **Team Harness (OHM v1.1)** — a descriptor in the registry — not a subgraph. |
| **Cascading per-agent inherited budgets** — each agent/sub-agent carrying its own independently-accounted budget that the parent's budget cascades into | **[ADR-005](adr-005-workflow-concept-retirement-harness-as-replacement.md)** ("one harness = **one budget surface**" — the anti-decision against two/N budget surfaces) | Per-agent cascading budgets are exactly the duplicated-governance-surface cost ADR-005 retired: N budget surfaces that disagree on what counts, with no canonical arbiter. **Re-opened narrowly, and only as a different shape:** a single **team-POOLED budget envelope** (`max_tokens_total`, `max_usd_total`, `max_sub_runs`, `ttl_seconds`) over a fan-out's sub-runs — *one* pooled ceiling on the Team Harness, **not** per-agent inherited budgets. That re-opening is **single-tenant-opt-in** and is decided in **ADR-031 (Team budget envelope)** (design item D3 / lock §8 item 5). This ADR records only that the *original cascading-per-agent* shape stays retired; the pooled-envelope shape is ADR-031's to grant. |

**DEFERRED** — not retired, not yet committed; out of scope for R7 E3, revisitable by a future ADR when a binding use case demands it:

| Deferred primitive | Status | Why deferred |
| --- | --- | --- |
| **Cross-harness / workspace-spanning task boards** — a shared task board spanning multiple Team Harnesses or workspaces | DEFERRED | No north-star case (`team-of-agents-north-star-lock.md` §2) binds it. The R7 task board is **per-Team-Harness** (`task_board.columns`); a board that spans harnesses re-introduces the multi-governance-unit problem ADR-005 retired and is not needed by EURail / bitcoin / book. Revisit only when a cross-team product case appears. |
| **Consciousness drift-detection** — the original vision's autonomous self-monitoring of agent "consciousness" drift over long-lived runs | DEFERRED | The original consciousness-skills surface is a harness, not platform code (ADR-003 / ADR-005); R7 ships the *team* runtime (plan→coordinate→evaluate→re-plan), not autonomous drift-detection. Closed-loop re-planning (design C5) is bounded by **explicit `success_criteria` + convergence/termination rules**, not by a consciousness-drift signal. Deferred until the evaluator (C1) and closed loop (C5) are shipped and a concrete drift use case is on the table. |

## Alternatives considered

### A. Leave ADR-005 L77 as an implementation aside (no status ADR)

The do-nothing option: the three orchestrators remain a sentence in another ADR's implementation notes, picked up "whenever someone builds the team layer." Rejected because that is precisely the failure the audit found — an un-tracked promise for the platform's most load-bearing missing primitive, invisible to the release plan and ungated. The North-Star Lock §8 item 8 explicitly calls for this status note; an aside cannot be gated, owned, or pointed at from a release epic.

### B. Re-litigate the orchestrator design here (fold B1/B2 design into this ADR)

Make this ADR the full coordination-control decision — the three primitives *and* the Orchestration Agent, media taxonomy, and hand-off envelope. Rejected: that is a separate, larger decision (lock §8 item 2 / design §11 item 2) with its own contested surface (controller posture, prose-vs-coded routing). Bundling them would make this status ADR contested and slow, and would violate the ADR convention "one decision per ADR." This ADR commits the *mechanics as tracked deliverables* and the *retirement ledger*; the controller design stays in its own ADR.

### C. Record only the orchestrator-tracking, skip the retirement ledger

Convert L77 to a deliverable but leave the retired-vs-deferred question to each future reader. Rejected: the audit's central finding was a **three-way silent divergence** between vision, docs, and code — and the most expensive symptom was decisions (graph-resident team ontology; cascading budgets) being re-litigated because no ADR recorded they were already settled. Tracking the orchestrators without recording the ledger fixes one symptom and leaves the root cause. The two halves are the same governance gap and belong in one status ADR.

### D. Mark the deferred primitives as retired (close them permanently)

Treat cross-harness boards and consciousness drift-detection as RETIRED rather than DEFERRED, for a cleaner ledger. Rejected: neither has been decided against on the merits — they are simply out of scope for R7 with no binding north-star case. Marking them retired would force a future superseding ADR to revive a legitimately-open idea and overstates the decision actually made. "No silent supersession" (ADR index conventions) cuts both ways: do not record a retirement that was not decided.

## Consequences

### Positive

* The ADR-005 L77 promise becomes a **gated, owned, release-scheduled deliverable** (R7 epic E3 / design B1), not an aside. It can be tracked red→green like every other acceptance item.
* The **retired-vs-deferred ledger is canonical and singular** — the graph-resident team ontology and cascading per-agent budgets are recorded as RETIRED with the ADR that retired each; cross-harness boards and consciousness drift-detection as DEFERRED with the reason. The three-way vision/docs/code divergence the audit found has one authoritative resolution to point at.
* Future designs and PRs have a **bright line**: re-introducing a RETIRED primitive (e.g. modelling the team in the Neo4j graph, or per-agent inherited budgets) requires a new superseding ADR and will be caught at review; treating a DEFERRED primitive as shipped is likewise a flagged divergence.
* It **clarifies the boundary with ADR-031**: cascading-per-agent budgets stay retired; only the *pooled team envelope* is re-opened, and that is ADR-031's grant, single-tenant-opt-in — so the two ADRs cannot be read as conflicting.

### Negative

* This ADR commits the three orchestrators as deliverables but **does not itself design them** — a reader wanting the full orchestration contract must also read the forthcoming coordination-control ADR (lock §8 item 2). The split is deliberate (one decision per ADR) but means two ADRs to assemble the full picture.
* The retirement ledger **constrains future flexibility**: a future need for a graph-resident team view, per-agent budgets, a cross-harness board, or drift-detection now costs an explicit (super)seding ADR rather than a quiet design change. This is the intended cost — it is what ends the silent divergence — but it is friction for genuinely new requirements.
* Forward dependency on **ADR-031** (team budget envelope): until ADR-031 is accepted, the pooled-envelope half of the budget story is referenced but not yet granted. This ADR is intentionally narrow (it only records that the *original cascading* shape stays retired), so it does not block on ADR-031, but the two should be read together.

## Implementation notes

* No code ships from *this* ADR — it is status + governance. The orchestrator *build* lands under R7 epic E3 / design B1, as `core` capabilities (`orchestrate.sequential|parallel|conditional`) extending `execution-engine .../services/roundtable_service.drive` (the turn-sequencer skeleton) and `job_service` (durable dispatch/retry/CAS), with the real `asyncio.gather` fan-in barrier and the B3 reducer.
* The three orchestrators are prerequisites for the Orchestration Agent (B2) and for almost everything in Phases C/D — they are gated as such in the R7 build sequence (`team-of-agents-capability-design.md` §10).
* **Enforcement of the ledger:** the `use-case-guardian` persona checks every ADR/design/PR against the North-Star Lock; this ledger is the reference for "did this change silently re-introduce a RETIRED primitive or treat a DEFERRED one as shipped." A PR that models the team in the Neo4j graph, or attaches a per-agent inherited budget, fails review against this ADR.
* The ADR registry (`adr/index.md`) gains an ADR-033 row (Proposed, 2026-06-19); the "next NEW number" note advances to ADR-034 once ADR-031/032/033 are filed.
* `team-of-agents-capability-design.md` §11 item 7 and the North-Star Lock §8 item 8 (the two "status/retirement note on ADR-005 L77" pointers) are satisfied by this ADR; update both to link it on acceptance.

## References

* [ADR-005 — Workflow Concept Retirement; Harness as Replacement](adr-005-workflow-concept-retirement-harness-as-replacement.md) — the source of the L77 orchestrator promise and of the "one budget surface" anti-decision this ADR's ledger records.
* [ADR-029 — Workspace↔Harness Binding](adr-029-workspace-harness-binding.md) — the ADR that retired the graph-resident `:Agent` team ontology (harness = registry capability; binding = registry curation edge, not a graph association).
* [ADR-002 — OHM as Canonical Manifest Format](adr-002-ohm-as-canonical-manifest-format.md) — orchestration is expressed in OHM (v1.1 Team extension), not a service-local format.
* [ADR-003 — Platform-as-Code, Actors-as-Harnesses](adr-003-platform-as-code-actors-as-harnesses.md) — orchestrators are `core` capabilities, never platform code; a team is a descriptor interpreted by the runtime.
* **ADR-031 — Team budget envelope** *(forthcoming; lock §8 item 5 / design item D3)* — re-opens the per-harness budget anti-decision *only* as a single team-POOLED envelope (single-tenant-opt-in); the cascading-per-agent shape stays retired here.
* [Team-of-Agents North-Star Lock](../product/team-of-agents-north-star-lock.md) — §8 item 8 (this ADR's driving artifact); the retired-vs-deferred ledger realizes its §12 item 4 / design §12 item 4.
* [Team-of-Agents Capability Design](../../oraclous-backend/docs/team-of-agents-capability-design.md) — §5 B1 (the three orchestrators + fan-in barrier), §11 item 7 (the status/retirement note), §12 item 4 (retire-vs-defer open decision), §10 (R7 build sequence / epic E3).
* Team-of-agents architecture audit, run `wf_693afa65-500` — the cross-corpus review that surfaced the un-ADR'd L77 promise and the three-way vision/docs/code divergence.

## Revision history

| Date | Change |
| --- | --- |
| 2026-06-19 | Initial draft. Tracks ADR-005 L77 orchestrators (sequential/parallel/conditional) as R7 E3 deliverables; records the retired (graph-resident `:Agent` ontology · cascading per-agent budgets) vs deferred (cross-harness boards · consciousness drift-detection) ledger. Status Proposed, pending Reza/CTO. |
