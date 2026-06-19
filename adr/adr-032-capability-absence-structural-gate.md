---
title: "ADR-032 — Capability-Absence as a Structural Gate"
---

# ADR-032 — Capability-Absence as a Structural Gate (an imported `tools[]` set is an authoritative capability ceiling, enforced at the dispatch seam)

## Status

| Field | Value |
| --- | --- |
| Status | Accepted |
| Date | 2026-06-19 (accepted 2026-06-20) |
| Approved by | Reza Jahankohan |
| Supersedes | None |
| Superseded by | None |
| Driving artifact | [Team-of-Agents North-Star Lock](../product/team-of-agents-north-star-lock.md) — §2 "The CAPABILITY-ABSENCE GATE primitive" + §6 acceptance items 4 / 4b + §8 ADR #2 |

## Context

The North-Star Lock's acceptance test (§6) makes a falsifiable promise that the team-of-agents design must keep: a member imported from a `.claude/agents/*.md` file whose frontmatter reads `tools: Read,Grep,Glob,Write` **has no send/publish/upload/spend capability at runtime, and no orchestrator/A2A/coordinator path can grant one** (item 4), and a human author gate (A–G) is a **blocking DAG node** the run pauses on until the author advances it (item 4b). These two items together realize the book studio's seven structural author gates (A–G): the structural reason a drafting agent cannot publish a chapter, and the structural reason a chapter does not ship until the human author approves it.

The team-of-agents capability design (`product/team-of-agents-capability-design.md`) maps a frontmatter `tools` line to a member's **capability ceiling** (lock §7 delta A-NEW-2: "the `tools` line is an *authoritative ceiling*, not advisory") and models a human as a first-class member (`kind: human`, design §5 A1 `members[]`, design D4). But the design as written leaves two failure modes open:

1. **Capability escalation by routing.** Phase B adds an Orchestration Agent (B2), an A2A invoke-harness connector (B4), structured hand-off (B5), and a blackboard (C4). Every one of these is a path by which a member could come to *act through* a capability its own manifest never declared — an orchestrator hands a drafting agent a `publish` task; a coordinator routes a `send` through a sibling; an A2A call lets member A invoke a capability member A lacks via member B. If the ceiling is enforced anywhere other than the single point where a capability is actually dispatched, each of these paths is a hole.

2. **Confusing the ceiling with policy.** Oraclous already has a configurable governance layer — policy sets, ReBAC bindings, redact patterns (`governance` block, design §5 A1). Policy is *meant* to be set per org and can be **misset**: a too-permissive policy set, a ReBAC binding that grants more than intended. If "this agent cannot publish" lives in policy, it is one misconfiguration away from being false. The book author's guarantee — "the drafting team *structurally cannot* ship without me" — must not be a policy that someone can loosen.

The platform already places **fail-closed authority at the substrate ReBAC seam** ([ADR-013](adr-013-fail-closed-authority-placement-at-the-substrate-rebac-seam.md)) and mediates every cross-organisation traversal through ReBAC ([ADR-004](adr-004-federation-via-rebac-traversal.md)). ADR-013 answers "may this actor reach this resource *across orgs/under this policy*" — a configurable, contextual decision. It does **not** answer "does this member possess this capability *at all*". That second question is the one the book case needs answered structurally, and it is the gap this ADR fills. Capability-absence is upstream of policy: a capability the manifest never granted is never even a candidate for a policy decision.

## Decision

Two structural mechanisms, both interpreted by the harness runtime, neither configurable away.

### 1. The imported `tools[]` set is an authoritative capability ceiling, enforced at the dispatch seam

A member's resolved tool/capability set — sourced from its imported manifest (frontmatter `tools:` → OHM member capability ceiling, design A-NEW-2) — is the **complete, closed set of capabilities that member may ever dispatch at runtime**. It is a *ceiling*, not a default:

- **Enforced at the single dispatch seam.** Before the runtime dispatches any capability invocation *on behalf of a member*, it checks the requested capability id against **that member's** ceiling set. A capability not in the set is refused — fail-closed (deny), per ADR-013's posture — and the refusal is structural: there is no policy, flag, override, or context under which the check passes. The check binds to the **acting member**, resolved from the dispatch's `member`/`role` identity, never to the team or the orchestrator.
- **No routing path can escalate it.** The ceiling is checked at dispatch, *after* any routing decision, so it is path-independent:
  - The **Orchestration Agent** (design B2) may route a turn to a member, but the member still dispatches only within its own ceiling; routing a `publish` task to a `Read,Grep,Glob,Write` member yields a structural refusal, not a publish.
  - **A2A invoke** (design B4) is itself a capability (`core/invoke-harness`): a member can A2A-call a sub-agent **only if `invoke-harness` is in that member's ceiling**, and the child's ceiling is bound by scope-inheritance (child ⊆ parent). A member cannot launder a capability it lacks through a sibling it can reach.
  - **Structured hand-off** (design B5) and the **blackboard** (design C4) carry *data*, never capability — receiving a hand-off envelope or reading a blackboard finding never widens the receiver's ceiling.
- **Tool-omission is structural, not policy.** Omission of a tool from the imported `tools:` line is the *mechanism*, full stop. A member imported with `tools: Read,Grep,Glob,Write` literally cannot `send`/`publish`/`upload`/`spend` at runtime because those capability ids are not in its ceiling set — exactly as a drafting agent in the book studio cannot ship a chapter. This is **separate from and upstream of** the `governance` policy layer: policy decides *under what conditions* a possessed capability may be exercised (and can be misset); the ceiling decides *whether the capability is possessed at all* (and cannot be set looser than the source manifest declared). A capability absent from the ceiling never reaches a policy decision.
- **Closed by default; no implicit grants.** The ceiling is the imported set and nothing else. The runtime never adds a capability a member did not import — not for "convenience", not because a sibling has it, not because the orchestration `style` prose mentions it. Widening a member's ceiling is an explicit, audited edit to that member's manifest (the design's edit-a-running-team path, O5), never a runtime or routing side effect.

### 2. The companion HITL blocking-gate-node

A member with `kind: human` (design §5 A1, D4) that sits on the team DAG as a gate (the book's gates A–G) is a **blocking node**: when the run's execution reaches it, the run **pauses** at that node and **does not advance any dependent member** until the human **advances** it (approve / reject / edit-then-advance). Concretely:

- The blocking-gate-node is realized on the existing engine task board + HITL claim/complete/approve seam (design D4, `task_service`): reaching the node emits a HITL task; the node's `done`/`approved` transition is the *only* thing that satisfies the `depends_on` edge of downstream members; agents **cannot cross it** by any routing path.
- It is **non-opt-in for the book case.** Per the lock's §2 correction and §4 CUT list, the *blocking-gate-node itself* is mandatory; only the HITL **SLA / capacity / time-to-resolution apparatus** (design D4's scheduling half) is cut to opt-in. The gate blocks regardless of whether any SLA machinery is configured.

### The two are distinct and complementary

These are **two different gates** and the book studio needs both:

| | Capability-absence ceiling | HITL blocking-gate-node |
| --- | --- | --- |
| Question answered | "Can this member dispatch this capability *at all*?" | "Has the human advanced this step yet?" |
| Prevents | a **bad send** — an agent acting beyond its imported tools | a **premature advance** — work proceeding past the author's approval |
| Mechanism | closed ceiling checked at the dispatch seam | a blocking DAG node on the HITL task board |
| Realizes (book) | gates A–G's *"the drafting agent structurally cannot publish"* | gates A–G's *"nothing ships until the author approves"* |

Capability-absence stops the agent from doing the wrong thing; the blocking-gate-node makes the agent wait for the right person. Neither substitutes for the other.

## Alternatives considered

### A. Enforce the ceiling as a policy set in the `governance` block

Express "this member may not publish" as a deny rule in the member's policy set / ReBAC bindings, reusing the existing configurable governance layer. **Rejected:** policy is configurable and therefore mis-settable — a too-permissive policy set or an over-broad ReBAC binding silently voids the guarantee, and the book author's "my drafting team structurally cannot ship without me" degrades to "…unless someone loosens a policy." The lock (§2, item 4) requires the ceiling to be *structural*, not policy. Policy answers a different, downstream question (conditions of exercise of a *possessed* capability); the ceiling answers possession.

### B. Enforce the ceiling at import time only (validate the manifest, then trust the runtime)

Check that the imported member declares a coherent tool set at import, and assume the runtime only ever dispatches declared tools. **Rejected:** the Phase B routing paths (orchestrator, A2A, hand-off, coordinator) are exactly the surfaces that introduce *new* dispatch opportunities at runtime, after import. An import-time-only check cannot see an orchestrator routing a `publish` task to a drafting member at turn 40. The ceiling must be enforced at the **dispatch seam**, on every invocation, against the acting member — the one point all routing paths funnel through.

### C. A single combined "human-approval-with-capability-restriction" gate

Model the author gate as one mechanism that both blocks the run and restricts capabilities. **Rejected:** they are orthogonal and independently necessary. A member can be capability-restricted with no human in the loop (a pure research agent with `tools: Read,Grep` and no gate), and a human gate can sit over members that are otherwise fully capable (an approval step before an already-publish-capable member acts). Conflating them would force a human into every capability restriction and a capability restriction into every human gate — neither of which the book case wants. The lock's adversary-#6 correction explicitly keeps them distinct (item 4 vs item 4b).

### D. Treat the ceiling as advisory (warn-on-violation, do not block)

Log a warning when a member dispatches outside its imported tools but allow the call. **Rejected outright:** "advisory" is the exact failure the lock names — "the `tools` line is an *authoritative ceiling*, not advisory" (§7 A-NEW-2). An advisory ceiling provides no guarantee; the book author would have no structural assurance at all. Fail-closed (ADR-013) means the violation is *refused*, not noted.

## Consequences

### Positive

- **The book studio's seven author gates (A–G) become real and structural.** A drafting agent imported with `tools: Read,Grep,Glob,Write` cannot publish/upload/send/spend by any path, and a chapter cannot advance past an author gate until the human approves — exactly the guarantee the use case requires, realizing acceptance items 4 and 4b.
- **The guarantee survives misconfiguration.** Because the ceiling is upstream of policy and unconfigurable, no policy-set or ReBAC mis-setting can grant a member a capability its source manifest withheld. The book author's "my team structurally cannot ship without me" holds even under an operator error in the governance layer.
- **Routing surfaces stay safe by construction.** The orchestrator (B2), A2A (B4), hand-off (B5), and blackboard (C4) can be added without each one needing its own escalation guard — the single dispatch-seam check makes them all path-independent, so new routing capabilities don't reopen the hole.
- **Composes with the existing fail-closed substrate.** The mechanism reuses ADR-013's deny-on-ambiguous posture and sits cleanly beside ADR-004's cross-org ReBAC mediation: ReBAC still answers "may this possessed capability cross this org boundary"; the ceiling answers the prior "is this capability possessed".

### Negative

- **A new mandatory check on the dispatch hot path.** Every member capability dispatch now carries a ceiling lookup. The set is small and resolved at import, so the cost is a set-membership check, but it is non-skippable by design and must be implemented on the one true dispatch seam (not duplicated per routing path, which would reintroduce the drift this ADR closes).
- **A blocking human node can stall a run indefinitely.** By design the run waits on the human with no SLA on the minimal path (the SLA apparatus is opt-in). A team whose DAG funnels through a slow human gate will park there; the status surface (O4) must make a blocked-on-human run visible so the wait is observed, not silent.
- **Import fidelity becomes load-bearing.** The guarantee is only as good as the importer's mapping of frontmatter `tools:` → ceiling. An importer bug that *widens* the set silently weakens the gate, so the import dry-run (O8) must surface each member's resolved ceiling for the user to confirm before the first side-effecting run.
- **No runtime widening, even when convenient.** A member that genuinely needs a new capability mid-life requires an explicit manifest edit (O5), not a quick runtime grant. This is the intended cost of making the ceiling authoritative.

## Implementation notes

- **One dispatch seam.** The ceiling check lives at the single point in `harness-runtime` where a member's capability invocation is dispatched, keyed on the resolved acting-member identity — not in each orchestrator/connector. The orchestration agent (design B2), the A2A connector (design B4, `core/invoke-harness`), and the round-table/board drivers all flow through this seam; none gets its own copy of the check.
- **Ceiling provenance.** The ceiling set is populated by the importer from frontmatter `tools:` as the OHM v1.1 member capability ceiling (lock §7 A-NEW-1/A-NEW-2). `invoke-harness` is itself a capability subject to the ceiling, and child scope-inheritance (child ⊆ parent) on A2A is enforced as part of B4 — together these close the "launder a capability through a sibling" path.
- **Blocking-gate-node on the existing board.** Realize the HITL blocking node on the engine task board + claim/complete/approve seam (design D4 / `task_service`), with the node's approve/advance transition as the sole satisfier of downstream `depends_on` edges. Keep the gate mandatory; gate only the SLA/capacity/time-to-resolution apparatus behind the opt-in flag (lock §4 CUT — D4 SLA).
- **Structural vs policy boundary.** Keep the ceiling check strictly separate from the `governance` policy-set / ReBAC evaluation: the ceiling runs first and is unconfigurable; policy and ReBAC (ADR-013 / ADR-004) run only on capabilities that *pass* the ceiling. Do not collapse the two into one configurable decision.
- **Dry-run surfacing.** The import dry-run (O8) emits each member's resolved ceiling and each human blocking-gate node in the DAG, so the user confirms the structural guarantees before any live run.
- **Guardian-enforced.** Per the lock, the `use-case-guardian` checks this ADR's bound acceptance items (4, 4b) against every later PR/design change; a change that lets any path grant a member a capability outside its ceiling, or lets an agent cross a human gate, fails the guardian gate.

## References

- [Team-of-Agents North-Star Lock](../product/team-of-agents-north-star-lock.md) — the driving artifact: §2 capability-absence gate primitive + adversary-#6 blocking-gate-node correction, §6 acceptance items 4 / 4b, §7 delta A-NEW-2, §8 ADR #2
- [Team-of-Agents Capability Design](../product/team-of-agents-capability-design.md) — §5 A1 (`members[]`, capability ceiling), B2 (orchestration agent), B4 (A2A invoke), B5 (hand-off), C4 (blackboard), D4 (HITL-as-member)
- [ADR-013 — Fail-Closed Authority Placement at the Substrate ReBAC Seam](adr-013-fail-closed-authority-placement-at-the-substrate-rebac-seam.md) — the deny-on-ambiguous posture this ceiling adopts; the ceiling sits upstream of (and distinct from) ReBAC authority
- [ADR-004 — Federation via ReBAC Traversal](adr-004-federation-via-rebac-traversal.md) — cross-org mediation of a *possessed* capability; the ceiling answers the prior question of possession
- [ADR-003 — Platform-as-Code, Actors-as-Harnesses](adr-003-platform-as-code-actors-as-harnesses.md) — members are interpreted descriptors; the ceiling is a manifest-derived property the runtime interprets, never platform code
- [ADR-002 — OHM as Canonical Manifest Format](adr-002-ohm-as-canonical-manifest-format.md) — the `tools`/member capability ceiling is an OHM v1.1 field; additive, versioned spec evolution

## Revision history

| Date | Change |
| --- | --- |
| 2026-06-19 | Initial draft (Proposed). Capability-absence as a dispatch-seam ceiling + the companion HITL blocking-gate-node; realizes North-Star Lock acceptance items 4 / 4b (book studio gates A–G). |
