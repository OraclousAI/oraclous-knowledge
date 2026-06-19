---
title: "ADR-031 — OHM v1.1 Team Manifest (Team Harness)"
---

# ADR-031 — OHM v1.1 Team Manifest (Team Harness)

## Status

| Field | Value |
| --- | --- |
| Status | Proposed |
| Date | 2026-06-19 |
| Approved by | pending (Reza / CTO) |
| Supersedes | None |
| Superseded by | None |
| Driving artifact | [Team-of-Agents — North-Star Lock & Acceptance Test](../product/team-of-agents-north-star-lock.md) |

## Context

The platform ships a real, governed **single**-agent runtime (R4/R5/R6/R7-SEC signed off). It does not ship the team layer on top of it. The reason is structural, not incidental: **OHM v1.0 literally cannot express a team.** Its `OHMManifest` has a single `runtime.entrypoint` resolving to exactly one capability, and its actor model is a flat `OHMActor` of `{ role, kind, human_role }` with no dependency edges, no per-actor sub-goal, no per-actor sub-harness reference, no orchestration brief, no task board, no pooled budget, and no precedence/truth model. The only multi-actor primitive that runs today is a degenerate sequential round-table that round-robins actors over a flattened 4000-char transcript and returns the last turn's text as "the result."

ADR-003 declared actors are harnesses-as-descriptors and ADR-005 retired the workflow concept by promising that team behaviour would live *inside* a harness as a capability composition (sequential / parallel / conditional, ADR-005 L77). Neither ADR gave the manifest the fields needed to *write down* such a composition. The North-Star Lock makes the consequence first-class: all three north-star use cases (EURail assessment, bitcoin-gpt market intelligence, book studio) are **teams** the user already has, and every one of them is inexpressible in OHM v1.0. The Lock's design delta **A-NEW-2** requires that a member's imported `tools:` line become an *authoritative capability ceiling* (not advisory), and **A-NEW-3** requires that the user's precedence / Hierarchy-of-Truth become a manifest field — graph-as-truth becomes a *mode*, never the default. The capability design's §5 A1 / §8 give the concrete target shape.

This ADR decides the **additive, versioned** OHM v1.1 extension that lets a whole team be expressed as one manifest — a **Team Harness**. It is the keystone of Phase A in the capability design: this single change gates planning, coordination, execution, evaluation, and re-planning simultaneously. The **importer** that populates a Team Harness from an existing `.claude/agents/` directory (Lock R1, Adoption-First, design delta E2) is a *separate* ADR and is explicitly **out of scope** here — this ADR decides only the *target schema* the importer must emit and the runtime must interpret.

The non-negotiable design principles carried from ADR-001/002/003/005 (capability design §2) are kept in full:

1. **One harness = one governance unit.** A team is one root Team Harness — one budget surface, one audit/provenance stream, one ReBAC envelope, one tenancy boundary. **Unit of governance = one; unit of execution = many.**
2. **Actors are descriptors, not code** — a team is OHM, interpreted by the runtime, never compiled into platform code.
3. **Governance lives in code; flexibility lives in prose; code wins.** Routing *choice* may be prose; routing *mechanics, budgets, gates, isolation* are coded and unbypassable.
4. **Fail-closed everywhere.**
5. **`org_id` on every operation; ReBAC on every cross-org traversal** — inherited per-member.
6. **Additive, versioned spec evolution** — OHM v1.1 *adds* team fields; a v1.0 single-entrypoint harness remains valid and runs unchanged.

## Decision

OHM is extended to **version 1.1** with an **additive** set of blocks that make a team topology expressible as one manifest — the **Team Harness**. The extension is governed by one keystone invariant and one hard compatibility requirement.

**Keystone invariant — one Team Harness = one governed run.** A Team Harness has exactly **one** budget surface, **one** audit / provenance stream, **one** tenancy boundary, and **one** ReBAC envelope, regardless of how many members execute under it. The unit of *governance* is one; the unit of *execution* is many. The team-pooled `budget` block (below) is the single enforced ceiling for the whole fan-out; there is no per-member budget surface that escapes it.

**Hard compatibility requirement — additive & versioned.** Every block introduced below is optional. A manifest that omits `members` / `orchestration` / `task_board` / `precedence` and carries a single `runtime.entrypoint` is a valid v1.0 single-entrypoint harness and **runs unchanged**. `ohm_version: "1.0"` documents continue to load and execute exactly as today; the new blocks are only consulted when `metadata.kind: team` is present. A team form is never imposed on a single agent.

### The contract

```yaml
ohm_version: "1.1"

metadata:
  id: <uuid>
  name: "market-intel-team"
  owner_organization_id: <org>
  kind: team                       # agent | team   (default: agent → v1.0 behaviour)

members:                           # REPLACES the flat actors[]; richer, DAG-capable.
  - role: researcher               # unique member role within the team
    kind: agent                    # agent | human
    manifest_ref: "org:<org>/research-agent@3"   # the sub-harness OHM (for kind: agent)
    subgoal: "Gather cited evidence for the assigned sub-topic"
    depends_on: []                 # dependency-DAG edges (fan-in barrier on listed roles)
    fan_out:                       # OPTIONAL N-way fan-out (one instance per item)
      over: "$.subtopics"          #   JSONPath into team inputs/board state
      max_parallel: 8
    inputs: [ "$.objective", "$.window" ]        # what this member receives
    outputs_schema: { $ref: "#/schemas/evidence_batch" }   # typed output contract
    # human_role: "domain-lead"    # REQUIRED when kind: human; omitted for kind: agent

  - role: editor
    kind: human
    human_role: "domain-lead"      # the human's routing role; no manifest_ref
    subgoal: "Approve the final synthesis"
    depends_on: [ reviewer ]

orchestration:                     # the coordinator's brief (choice is prose)
  medium: [ blackboard, board ]    # round-table | board | blackboard | handoff | a2a
  style: >                         # prose the orchestration agent reasons over
    Fan out researchers in parallel over subtopics; barrier; run analysts;
    then an adversarial round-table; escalate the synthesis to the human editor.
  success_criteria: "Every finding cites ≥1 source; 0 unresolved CONTRADICTS; editor approves."
  termination:                     # goal-aware stop conditions (distinct from per-agent caps)
    max_wall_seconds: 7200
    max_rounds: 3
    convergence: "evaluator>=0.8"

task_board:                        # first-class assignable tasks
  columns: [ proposed, claimed, in_progress, blocked, done, escalated ]

budget:                            # TEAM-POOLED envelope — the single governed ceiling
  max_tokens_total:   8_000_000
  max_tool_calls_total: 5000
  max_sub_runs:         40
  max_usd_total:        60
  ttl_seconds:          10800

precedence:                        # Hierarchy-of-Truth — graph-as-truth is a MODE, not default
  order: [ rules, bible, toc, drafts ]   # source-defined truth ranking (highest first)
  graph: derived                   # authoritative | derived   (default: derived & disposable)

governance:
  policy_set_ref: "org:<org>/team-default"
  rebac_bindings: [ ... ]
  redact_patterns: [ ... ]

schemas:                           # typed hand-off payloads referenced by outputs_schema
  evidence_batch:
    type: object
    properties:
      records: { type: array, items: { $ref: "#/schemas/evidence_record" } }
  evidence_record:
    type: object
    properties:
      claim:       { type: string }
      label:       { enum: [ DIRECT, INFERRED, ASSUMPTION ] }
      source_url:  { type: string }
      observed_at: { type: string }
```

### Block-by-block commitments

- **`metadata.kind: agent | team`** — the discriminator. Absent or `agent` ⇒ pure v1.0 behaviour (single entrypoint; the team blocks are ignored even if present). `team` ⇒ the runtime interprets `members` + `orchestration` as the execution topology and `runtime.entrypoint` becomes optional.

- **`members[]`** replaces the flat `actors[]`. Each member carries:
  - `role` — unique within the team; the addressable identity for `depends_on`, hand-offs, and board assignment.
  - `kind: agent | human` — an `agent` member references a sub-harness via `manifest_ref` (own prompt, model, tools, own context window); a `human` member carries `human_role` and no `manifest_ref`, and is a blocking participant on the task board.
  - `manifest_ref` — the OHM reference to the member's sub-harness (resolved at load time, atomically, fail-closed, per ADR-002), for `kind: agent`. **The referenced sub-harness's `capabilities`/`tools` are the member's hard capability ceiling** (ADR-002 resolution semantics + Lock A-NEW-2); the team manifest cannot widen it, and the orchestration agent may route a member only to capabilities the member declares.
  - `subgoal` — the member's objective slice (free prose; the unit the evaluator scores a member against).
  - `depends_on: []` — the **dependency-DAG edges**. A member becomes dispatchable only when every role it lists has reached `done`; a non-empty list is a **fan-in barrier** over those roles. The graph must be acyclic (validated at load).
  - `fan_out: { over, max_parallel }` — optional. `over` is a JSONPath into the team inputs / board state; the runtime instantiates one member instance per resolved item, bounded by `max_parallel`. Absent ⇒ a single instance.
  - `inputs: []` — JSONPath expressions selecting what the member receives.
  - `outputs_schema` — a `$ref` into `schemas`; the member's output is validated against it before it lands on the board / blackboard (typed hand-off, not prose-in-a-string).
  - `human_role` — required when `kind: human`; names the routing role for the blocking human gate.

- **`orchestration`** — the coordinator's brief: `medium[]` (one or more of `round-table | board | blackboard | handoff | a2a`), `style` (prose the orchestration agent reasons over), `success_criteria` (prose the evaluator checks against), and `termination` (`max_wall_seconds`, `max_rounds`, `convergence` — goal-aware stop conditions distinct from per-agent caps). *Choice is prose; mechanics are coded.*

- **`task_board: { columns }`** — first-class assignable tasks with an explicit status lattice (`proposed, claimed, in_progress, blocked, done, escalated`), the medium for async + mixed human/agent work and the surface a blocking human gate lives on.

- **`budget`** (**team-POOLED**) — `max_tokens_total`, `max_tool_calls_total`, `max_sub_runs`, `max_usd_total`, `ttl_seconds`. This is the **single** enforced ceiling for the whole team run — the realization of the keystone invariant's one-budget-surface. It re-opens, for the team case, the per-harness budget framing of ADR-005: a fan-out's N sub-runs draw down one pooled total, not N independent budgets.

- **`precedence`** (the **Hierarchy-of-Truth** field) — `order[]` ranks the team's truth sources highest-first (e.g. book's `rules > bible > toc > drafts`); `graph: authoritative | derived` declares whether the graph blackboard *is* canonical truth or is a **derived, disposable index** over a file-native / external substrate. **Default `graph: derived`** — graph-as-truth is an explicit *mode*, never assumed. The runtime adopts the source's truth model; it never inverts canonical truth to graph-as-truth (Lock R5 / A-NEW-3).

- **`governance`** — `policy_set_ref`, `rebac_bindings`, `redact_patterns`: the single ReBAC/policy envelope inherited per-member.

- **`schemas`** — JSON-Schema fragments referenced by members' `outputs_schema` / `inputs`, giving **typed hand-off payloads** between members rather than a flattened string.

A v1.0 single-entrypoint harness omits `members` / `orchestration` / `task_board` / `precedence` / `budget` and runs exactly as today.

## Alternatives considered

### A. A separate Team-Manifest spec, parallel to OHM

Define a distinct document type (a "team manifest") that *references* OHM single-agent manifests, rather than extending OHM itself. **Rejected** — this re-creates exactly the two-concept duplication ADR-005 retired (two governance evaluations, two audit streams, two budget surfaces, two failure-mode catalogues). A team is a harness that uses other harnesses as members; it must be *one* OHM document so it signs, versions, governs, and audits as one unit (ADR-002/003/005). A parallel spec would also fork the portability story and double the spec-evolution cost ADR-002 already pays.

### B. Keep `actors[]` flat; express dependencies in an external orchestration file

Leave the actor list unchanged and put the DAG, sub-goals, and budget in a side document the orchestrator reads. **Rejected** — it splits "what this team *is*" across two locations, defeating ADR-002's single-document portability and atomic-signing guarantee, and it leaves the manifest still unable to answer "who are the members and how do they depend on each other?" The dependency DAG, per-member sub-goal, and pooled budget are intrinsic to the team's identity and must live in the manifest.

### C. Per-member budgets that sum to the team total (no pooled envelope)

Give each member its own budget and let the team total be their sum. **Rejected** — it violates the keystone invariant. A fan-out can spawn N sub-runs each individually under-budget while the aggregate is unbounded; "sum of per-member budgets" is unenforceable at the moment of a dynamic fan-out (`max_parallel` over a runtime-resolved list). One pooled `max_*_total` is the only ceiling that is both meaningful and enforceable for a team, and it is what makes "one governed run" true rather than aspirational.

### D. Make the graph blackboard the canonical truth for every team

Adopt the original design's "blackboard = Neo4j" assumption as the universal truth substrate, with no `precedence` field. **Rejected** by the North-Star Lock's adversarial pass: graph-as-truth is *wrong for two of the three* north-star cases (book is file-native git-markdown with `rules > bible > toc > drafts`; bitcoin adopts an *existing* graphify graph and must not be forced to a second). Forcing graph-as-truth inverts the user's own canonical truth model and breaks Lock acceptance items 8 and 9. `precedence` with `graph: derived` as the **default** makes graph-as-truth an opt-in *mode*, which is the only shape that adopts all three sources faithfully.

## Consequences

### Positive

- A team is finally *expressible*: members, a dependency DAG, per-member sub-goals and typed outputs, an orchestration brief, a task board, a pooled budget, and a truth model — all in one OHM document. This single additive change unblocks Phase A→D of the capability design (planning, coordination, execution, evaluation, re-planning) simultaneously.
- The keystone invariant is encoded, not just asserted: one Team Harness signs, versions, governs, audits, budgets, and is tenancy-bounded as **one** unit (ADR-002/003/005 preserved intact for the team case).
- Zero migration cost for existing harnesses: every shipped v1.0 manifest remains valid and runs unchanged. The team form is strictly opt-in via `metadata.kind: team`.
- The member's `tools` ceiling becomes structural (capability-absence as a hard ceiling, Lock A-NEW-2) — the foundation the separate capability-absence-gate ADR builds enforcement on.
- The user's truth model is adopted, not inverted: `precedence` makes graph-as-truth a mode, satisfying Lock acceptance items 8–9 and keeping file-native and graph-adopt substrates as peers.
- Typed `schemas` hand-offs replace the lossy 4000-char string transcript, making inter-member exchange validated and auditable.

### Negative

- The OHM spec now carries a meaningfully larger surface (seven new/changed blocks). Spec-evolution discipline (ADR-002's permanent cost) grows; `ohm-lint` / validation must cover DAG acyclicity, `manifest_ref` resolution, `kind: human ⇒ human_role`, schema `$ref` integrity, and `fan_out.over` JSONPath validity.
- `members[]` replacing `actors[]` is the one place the change is *not* a pure superset of field names. A reader must map the old flat `{ role, kind, human_role }` actor onto the richer member shape; the parser must accept a v1.0 `actors[]` (single-agent path) and a v1.1 `members[]` (team path) and never both. This is the sharpest validation edge.
- Authoring a Team Harness by hand is demanding (a DAG, sub-goals, schemas, a pooled budget). This is acceptable only because the **importer** (separate ADR) is the intended populator — hand-authoring is the exception, not the path. Until that importer lands, the only ergonomic way to produce a Team Harness is absent.
- A pooled budget shifts enforcement complexity into the engine: the team total must be drawn down atomically across concurrent fan-out sub-runs (a real concurrency concern deferred to the team-budget-envelope work, design D3).

## Implementation notes

- **Schema home:** the OHM v1.1 types and validators live in `packages/ohm`; the team data model (DAG with a topological-order resolver, per-member resolution) lives in `harness-runtime .../domain/ohm/`, extending the existing `OHMManifest` / `OHMActor` and the pure resolution helpers. This ADR decides the *contract*; A2 (team data model) and the importer are separate deliverables.
- **`actors[] → members[]`:** the parser accepts a v1.0 `actors[]` (loads as a single-agent harness) and a v1.1 `members[]` (loads as a team). A document carrying both is a load error. A v1.1 document with `metadata.kind: agent` and a single entrypoint behaves identically to v1.0.
- **Capability ceiling:** the member's ceiling is the union of its referenced sub-harness's declared capabilities, resolved at load time per ADR-002 (atomic, fail-closed). The *enforcement* that no orchestrator/A2A/coordinator path can widen it is the subject of the separate capability-absence-gate ADR; this ADR fixes only that the manifest expresses the ceiling and never a widening.
- **Pooled budget enforcement** is engine-side (design D3) and re-opens the ADR-005 per-harness budget framing for the team case; `spend_service.estimate` becomes enforcing against `budget.max_*_total`.
- **`precedence` default** is `graph: derived` — a manifest that omits the block is treated as derived-and-disposable graph, never graph-as-truth.
- **Out of scope (separate ADRs):** the importer (Adoption-First / Lock R1, design E2); the capability-absence structural gate; coordination control & media (orchestrators + the orchestration agent); A2A invocation & scope-inheritance; flow-level evaluation & the closed loop; the three lifecycles; single-tenant local GO; the batteries-included registry. This ADR decides only the **manifest schema** those builds read and write.

## References

- [Team-of-Agents — North-Star Lock & Acceptance Test](../product/team-of-agents-north-star-lock.md) — the driving artifact (§2 R1–R6, §5 sufficiency, §6 acceptance items 1–4/8–9, §7 deltas A-NEW-2/A-NEW-3, §8 ADR list item 1)
- [Team-of-Agents Capability Design](../../oraclous-backend/docs/team-of-agents-capability-design.md) — §2 design principles, §5 A1 (the shape this ADR ratifies), §8 the concrete v1.1 example
- [ADR-002 — OHM as Canonical Manifest Format](adr-002-ohm-as-canonical-manifest-format.md) — the canonical-manifest decision this ADR *extends* (resolution semantics, atomic signing, versioning rules)
- [ADR-003 — Platform-as-Code, Actors-as-Harnesses](adr-003-platform-as-code-actors-as-harnesses.md) — actors-as-descriptors; the team form realizes its composition path
- [ADR-005 — Workflow Concept Retirement; Harness as Replacement](adr-005-workflow-concept-retirement-harness-as-replacement.md) — the team is the harness-as-composition this ADR implied (L77 orchestrators); the pooled budget re-opens its per-harness budget framing for the team case
- [ADR-027 — Agent Memory: Ebbinghaus Store](adr-027-agent-memory-ebbinghaus-store.md) — the `:Memory` store the blackboard medium / `precedence.graph` build on
- [ADR index](index.md)

## Revision history

| Date | Change |
| --- | --- |
| 2026-06-19 | Initial draft. Status Proposed. Decides the additive OHM v1.1 Team Harness schema (`metadata.kind`, `members[]`, `orchestration`, `task_board`, team-pooled `budget`, `precedence`, `governance`, `schemas`); keystone invariant one-Team-Harness=one-governed-run; v1.0 remains valid and runs unchanged. Importer + capability-absence gate out of scope (separate ADRs). |
