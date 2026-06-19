# Oraclous — Team-of-Agents Capability: Comprehensive Design

> **Status:** proposed design · **Author basis:** the team-of-agents architecture audit (run `wf_693afa65-500`, 20-agent cross-corpus review of original vision docs, current ADRs/architecture, OHM v1.0 spec, and shipped code) · **Audience:** founder + the coordinator personas (solution-architect, product-planner, devops-implementer) and the repo implementer fleet.
>
> This document turns the audit's gap findings into an **executable design** for the capability Oraclous was always meant to have and does not yet: a **governed team of agents that plans, coordinates, executes, evaluates, and refines itself toward an objective**. It is the canonical reference the three use-case playbooks (`team-of-agents-use-case-playbooks.md`) build on.
>
> **⚠️ Read with the LOCK.** `oraclous-knowledge/product/team-of-agents-north-star-lock.md` is the authoritative overlay on this spec — it adds the six headache-elimination requirements (R1–R6: importer, tool/data adoption, batteries, import-driven DAG, substrate fidelity, turnkey GO), the capability-absence gate, the operational requirements (O1–O8), the CUT list (gold-plating → opt-in), and the 16-item North-Star Acceptance Test. **Where this design and the lock diverge, the lock wins.** The §5 capability set below is sound but, as originally written, *insufficient on its own* (it fails all three use cases on step one — import); apply the lock's §7 design deltas. The `use-case-guardian` enforces the lock against every change.

---

## 0. How to read this

The platform today ships a **real, governed _single_-agent runtime** (R4/R5/R6/R7-SEC signed off). What it does **not** ship is the team layer on top of it. The gaps are *scoping omissions* — the team-coordination capability was never scoped into the build — not unbuilt-layer artifacts. Crucially, the impressive multi-agent "team" you can point at today is the **dev-time fleet that builds Oraclous**, not a **product runtime capability** Oraclous offers a customer. This document specifies the product runtime capability.

Each capability below carries: **What** (the primitive), **Why** (the gap it closes), **Shape** (the contract/interface), **Lives in** (which service/layer), **Builds on** (the existing seam to extend). Capabilities are grouped into four build phases (A→D); the ordering is a hard dependency chain — **the evaluator and the orchestrator are prerequisites for almost everything else** (a planner is meaningless without multi-actor execution; re-planning is impossible without evaluation).

---

## 1. Problem statement (the gap, in one screen)

The original `ORACLOUS_AGENT_PLATFORM_ARCHITECTURE.md` designed a rich team substrate — agent-to-agent communication (§5.3), a Coordination Protocol (§7), a team permission model (§8), orchestrator/worker example agents (§9), sub-agent definitions (§11), a Monitor (§12.5). **ADR-005 ("workflow retirement")** then collapsed all of that into "it's just a harness with an orchestrator capability," **promised** three baseline orchestrator capabilities (sequential/parallel/conditional, `ADR-005 L77`) — and **none were built, tracked, or given an ADR**. The shipped **OHM v1.0 spec literally cannot express a team** (`OHMManifest` has no `plan`/`subgoals`/`dependencies`/`task_board`/`orchestration` fields; `OHMActor` is a flat `{role, kind, human_role}`). The only multi-actor primitive that runs is a **degenerate sequential round-table** that round-robins actors over a flattened 4000-char string transcript and returns the last turn's text as "the result."

Against the five pillars of "a working team of agents":

| Pillar | Designed? | Decided/Deferred? | Built? |
|---|---|---|---|
| **P1 Upfront planning / decomposition** | Yes (the *Harness Compiler*) | Zero ADR; spec-inexpressible | **None** |
| **P2 Coordination control** | Vision *disclaims* it; current docs decide a per-run "orchestration agent" | Narrative only; no ADR | **Partial** (single-loop + sequential round-robin; no router/fan-out/aggregator) |
| **P3 Coordination medium** | Vision: blackboard-primary | 5-medium taxonomy, un-ADR'd, absent from OHM spec | **Degenerate** (one string-transcript round-table) |
| **P4 Continuous evaluation & monitoring** | Output eval designed; team-coordination eval never | Monitoring coded; evaluation decided to be **prose** | **Partial** (monitoring-as-audit real; no judge/scorer/success-criteria) |
| **P5 Closed-loop re-planning** | Designed for data/model axis; agent-team re-plan never | Autonomous re-plan deferred/barred | **None** (retry re-runs identical input) |

Plus a **missing middle** absent at every tier: partial-failure recovery, result aggregation/merge, team termination/convergence, shared-state consistency, cross-team budget, durable replay of a team run, HITL-as-team-member, within-run tenant isolation.

---

## 2. Design principles (invariants we keep)

These survive from ADR-001/002/003/005 and are non-negotiable:

1. **One harness = one governance unit.** A team is *one root Team Harness* — one budget surface, one audit/provenance stream, one ReBAC envelope, one tenancy boundary. The "team vs one agent" dichotomy dissolves: **unit of governance = one; unit of execution = many** (the sub-agents). This is the keystone that lets us have a team *and* a single audit/budget surface.
2. **Actors are descriptors, not code.** A team is OHM, interpreted by the runtime — never compiled into platform code (ADR-003). New coordination behaviour is a *capability* in the registry, not a service.
3. **Governance lives in code; flexibility lives in prose; code wins.** Routing *choice* may be prose (an orchestration agent reasoning over an orchestration block); routing *mechanics, budgets, gates, isolation* are coded and unbypassable.
4. **Fail-closed everywhere.** Ambiguous authority denies; a member failure quarantines rather than corrupts; a missing org context yields zero rows.
5. **org_id on every operation; ReBAC on every cross-org traversal.** A team run inherits these per-member, and the shared medium must not become a covert channel across member scopes.
6. **Additive, versioned spec evolution.** OHM v1.1 *adds* team fields; a v1.0 single-entrypoint harness remains valid and runs unchanged.

---

## 3. Target architecture — the team-of-agents stack

```
                ┌──────────────────────────────────────────────────────────┐
   OBJECTIVE →  │  PLANNER (Harness Compiler)   — objective → Team Manifest │  Phase A/B
                └───────────────┬──────────────────────────────────────────┘
                                │ emits a Team Harness (OHM v1.1)
                ┌───────────────▼──────────────────────────────────────────┐
                │  COORDINATOR (Orchestration Agent)                        │  Phase B
                │   reads orchestration prose + board state; routes turns;  │
                │   fans out / fans in; declares completion vs criteria     │
                └───┬───────────────┬───────────────┬──────────────────────┘
                    │ sequential    │ parallel      │ conditional   (core orchestrators)
        ┌───────────▼────┐ ┌────────▼─────┐ ┌────────▼──────┐
        │ Role-Agent A   │ │ Role-Agent B │ │ Human member  │   sub-harnesses (own context,
        │ (sub-harness)  │ │ (sub-harness)│ │ (task board)  │   own model, own tools)
        └───────┬────────┘ └──────┬───────┘ └──────┬────────┘
                │  structured hand-off envelopes    │
        ┌───────▼───────────────────────────────────▼────────┐
        │  COORDINATION MEDIA                                 │  Phase B/C
        │  round-table · job/task board · BLACKBOARD          │
        │  (team-scope shared memory on the graph) · A2A      │
        └───────┬─────────────────────────────────────────────┘
                │ every action → provenance + run-tree
        ┌───────▼─────────────┐     ┌──────────────────────────┐
        │ EVALUATOR (judge)   │────▶│ CLOSED LOOP: monitor →    │  Phase C
        │ vs success_criteria │     │ evaluate → re-plan →      │
        │ + progress signal   │     │ re-dispatch               │
        └─────────────────────┘     └──────────────────────────┘
                │ MONITORING: correlated run-tree, per-member progress, budget
        ┌───────▼──────────────────────────────────────────────┐
        │  SUBSTRATE  — auth/ReBAC · credential broker · KGS    │  (exists)
        │  graph · KRS retrieval · capability registry · OTel   │
        └──────────────────────────────────────────────────────┘
```

Everything below the SUBSTRATE line ships today. Everything above it is this design.

---

## 4. Core vocabulary

- **Team Harness** — the root OHM v1.1 manifest describing a whole team: its members, their sub-goals, the orchestration, the success criteria, the budget envelope. One Team Harness = one governed run.
- **Role-Agent** — a member of the team: a sub-harness (own prompt, model, tools, own context window) bound by role. May be `kind: agent` or `kind: human`.
- **Orchestrator primitive** — a `core` capability that composes Role-Agents: `sequential`, `parallel` (fan-out + fan-in barrier), `conditional`. The mechanics.
- **Coordinator / Orchestration Agent** — the runtime component that reasons over the orchestration *prose* + live board state to decide who-acts-next and when the objective is met. The choice-maker, constrained to route only to declared members/capabilities.
- **Coordination medium** — how members exchange work: round-table, job/task board, blackboard (team-scope shared memory), structured hand-off, A2A invocation.
- **Blackboard** — the team's shared, accumulating working memory, realized on the graph substrate (team-scope `:Memory`/`:Finding` nodes), readable by traversal.
- **Evaluator** — a judge capability that scores a run (or a member's output) against `success_criteria` and emits a structured verdict.
- **Run-tree** — the correlated causal tree of a team run: the root Team Harness execution + every sub-harness execution + every board task, joined by `parent_execution_id`/`trace_id`.
- **Closed loop** — monitor → evaluate → (below threshold) re-plan/re-task/re-route → re-dispatch.

---

## 5. The capability set

### Phase A — The contract & the spine (unblocks everything)

#### A1 · OHM v1.1 — Team Extension (the spec that lets a team exist)
- **What:** Additive fields on the OHM manifest so a *team topology* is expressible: a member roster with dependency edges, a per-member sub-goal, a task board, an orchestration block, and success criteria.
- **Why:** OHM v1.0 cannot represent a team — this single change gates P1–P5 simultaneously.
- **Shape (new/extended blocks; v1.0 remains valid):**
  ```yaml
  ohm_version: "1.1"
  metadata: { id, name, owner_organization_id, kind: team }      # kind: agent|team
  members:                                                        # was actors[]; richer
    - role: researcher-onchain
      kind: agent                                                 # agent | human
      manifest_ref: org:<id>/onchain-research@1                   # the sub-harness OHM
      subgoal: "Characterise on-chain accumulation/distribution for the window"
      depends_on: []                                              # dependency edges (DAG)
      fan_out:                                                    # optional N-way fan-out
        over: "$.players"                                         #   one instance per item
        max_parallel: 8
      inputs: [ "$.objective", "$.window" ]
      outputs_schema: { $ref: "#/schemas/evidence_batch" }
    - role: synthesis
      kind: agent
      manifest_ref: org:<id>/synthesis@1
      depends_on: [ researcher-onchain, researcher-macro, ... ]   # fan-in
  orchestration:                                                  # the coordinator's brief
    medium: [ board, blackboard ]                                 # see §6
    style: "Fan out all researchers in parallel; barrier; then analysts; then synthesis."
    success_criteria: "Every claim cites a source; ≥N evidence records; conflicts resolved."
    termination: { max_wall_seconds, max_rounds, convergence: "evaluator>=0.8" }
  task_board:                                                     # first-class assignees
    columns: [ proposed, claimed, in_progress, blocked, done, escalated ]
  budget:                                                         # TEAM envelope (pooled)
    max_tokens_total, max_tool_calls_total, max_sub_runs, max_usd_total, ttl_seconds
  governance: { policy_set_ref, rebac_bindings, redact_patterns }
  schemas: { evidence_batch: { ... } }                           # typed hand-off payloads
  ```
- **Lives in:** `architecture/ohm-v1.1-team-extension` (spec) + `packages/ohm`.
- **Builds on:** `OHMManifest`/`OHMActor` (`harness-runtime .../domain/ohm/manifest.py:66-96`).
- **Size:** M.

#### A2 · Team Manifest data model
- **What:** Replace the flat actor list + single entrypoint with an in-code topology: dependency edges between members, a `subgoal`/`outputs_schema` per member, and a DAG representation with a topological-order resolver.
- **Why:** A planner's output must be representable and executable; today `runtime.entrypoint` resolves to exactly one capability/actor.
- **Lives in:** `harness-runtime .../domain/ohm/`.
- **Builds on:** the pure resolution helpers already in `manifest.py:98-122`.
- **Size:** M.

#### A3 · The decision-ratifying ADRs (see §11)
- The single largest *meta*-gap is that coordination is **un-ADR'd**. Phase A opens the ADRs that make every later build reviewable and amendable.

---

### Phase B — The runtime spine (the controller + the medium it needs)

#### B1 · The three orchestrator primitives + a real fan-in barrier  *(the load-bearing build)*
- **What:** `core` capabilities `orchestrate.sequential`, `orchestrate.parallel`, `orchestrate.conditional`. `parallel` runs members concurrently (`asyncio.gather`) and **blocks on a fan-in barrier** until all branches complete (or a quorum/termination rule fires). `conditional` routes on a predicate over prior results.
- **Why:** This is the missing `ADR-005 L77` promise and the root structural gap. Today the round-table is strictly sequential (`actor = actors[turn % n]`, synchronous per-turn await, no `asyncio.gather`) and its "fan-in" is `transcript.append`.
- **Shape:** an orchestrator capability receives the Team Manifest + current state, dispatches the next member set, awaits per its kind, returns a structured stage result.
- **Lives in:** `core` capability registry + execution-engine driver.
- **Builds on:** `execution-engine .../services/roundtable_service.drive` (the turn-sequencer skeleton) and `job_service` (durable dispatch/retry/CAS).
- **Size:** L.

#### B2 · The Orchestration Agent (prose-interpreting coordinator)
- **What:** The runtime component decided in `section-5-flows.md:95/:101/:105`: reads the manifest `orchestration` block + live `task_board` state, decides who-acts-first, mediates hand-offs, and **declares completion against the prose `success_criteria`** — constrained by the R4 T3-M1 guardrail (route only to declared members/capabilities).
- **Why:** P2 — there is no controller today; only mechanics. This is the "choice is prose, mechanics are coded" keystone.
- **Lives in:** `harness-runtime` (a built-in reasoning component) invoking B1 primitives.
- **Builds on:** the single-agent tool loop (`run_tool_use_loop`) for its own reasoning; the policy envelope (`policy.py:39-48`) for guardrails.
- **Size:** L.

#### B3 · Result aggregation / merge reducer
- **What:** A first-class merge step: a deterministic reducer (concat/dedupe/group by schema) plus an optional LLM-synthesis member, so fanned-out work is *merged*, not discarded.
- **Why:** Today the round-table "merges" by `final = transcript[-1]` — last-writer-wins throws away parallel work.
- **Lives in:** `core` capability (`aggregate.reduce`, `aggregate.synthesize`).
- **Size:** M.

#### B4 · A2A invoke-harness connector
- **What:** A capability-registry connector `core/invoke-harness` (a.k.a. `call-agent`) so a member can dispatch a sub-agent **under ReBAC + scope-inheritance** (child scope/tools/budget/ttl ⊆ parent). The missing "sub-agent-as-capability" primitive.
- **Why:** Today an agent can only call tools (`federated_search, find_similar, github, graph_ingest, knowledge_retriever, mcp, mysql, notion, postgresql, recall_memory`) — never another agent. This is also where the per-call A2A ACL is enforced.
- **Lives in:** capability-registry connector + harness-runtime dispatch.
- **Builds on:** the existing connector/executor framework + ReBAC seam (ADR-004).
- **Size:** M.

#### B5 · Structured hand-off envelope
- **What:** A typed payload `{ from_role, to_role, objective_slice, payload (schema-validated), provenance_ref, cursor }` that threads between members — replacing `_render_context()`'s flattened, 4000-char-truncated string concatenation.
- **Why:** P3 — inter-agent hand-off is currently prose-in-a-string, lossy and untyped.
- **Lives in:** `packages/ohm` (envelope type) + execution-engine round-table + board transitions.
- **Size:** M.

---

### Phase C — Evaluation, monitoring, and the closed loop

#### C1 · Flow-level Evaluator (the judge)
- **What:** An LLM-as-judge / rubric capability `core/evaluate` that grades a completed run, stage, or member output against the manifest `success_criteria`, returning a structured verdict `{ score, pass, dimension_scores, failures[], recommended_action }`.
- **Why:** P4 — there is no judge/scorer/success-criteria check anywhere; "SUCCEEDED" means "the loop returned text with no tool calls." **P5 cannot exist without this.**
- **Lives in:** a `core` capability; reuse the **KRS `EvalJudge` seam** (the RAGAS-style judge shipped in #331, currently retrieval-only) generalized to arbitrary rubrics.
- **Size:** M.

#### C2 · Cross-service run-tree / trace correlation
- **What:** Thread `parent_execution_id` + `trace_id` across engine→harness→sub-harness so a team's N child executions form one observable causal tree (today a round-table discards its child `result['id']`, orphaning rows in another service).
- **Why:** Unblocks durable replay, audit-as-one-unit, and the monitoring pane. P4/P6.
- **Lives in:** execution-engine + harness-runtime.
- **Builds on:** the existing single-job→execution link `engine_jobs.harness_execution_id` (the seam to extend).
- **Size:** M.

#### C3 · Progress-against-objective signal
- **What:** Replace the hardcoded `engine_jobs.progress` (`5` on RUNNING, `100` on terminal) with a goal-attainment signal readable mid-run by the orchestration agent and by humans (e.g. % sub-goals `done`, evidence-count vs target, evaluator partial score).
- **Why:** P4/P5 — there is nothing to monitor a team against today; the §12.5 `track_progress` design was dropped.
- **Size:** S–M.

#### C4 · Blackboard — team-scope shared memory (read + write)
- **What:** Wire the team's shared accumulating memory on the graph: members write `team`-scope `:Memory`/`:Finding` nodes; an automatic team-scope **read** each turn gives concurrent members visibility of each other's in-flight state; `CONTRADICTS` edges flag conflicts.
- **Why:** P3 + shared-grounding consistency. Today the `ADR-027` memory write is fire-and-forget, flag-gated **OFF** by default, and hardcodes `scope:"agent"` — the `team` scope it defines is **never even written**.
- **Lives in:** KGS (`:Memory` store, ADR-027) + harness-runtime memory hook + KRS read.
- **Builds on:** ADR-027 store + `memory_client.py` (flip `HARNESS_MEMORY_WRITES` on with safeguards; actually write `team` scope; add the read side).
- **Size:** M.

#### C5 · Closed-loop re-dispatch
- **What:** On an evaluator "below-threshold" verdict, **re-task / replace / re-route** members (not re-run the identical manifest): spawn a corrective member, hand the failures back to a redo, or escalate to a human gate. Plus the `can_propose_harness_changes` → HITL review path as a built control component.
- **Why:** P5 — today retry re-queues the *identical* manifest/input; HITL resume replays the *exact* checkpoint; nothing adapts on a quality signal.
- **Lives in:** orchestration agent + execution-engine.
- **Builds on:** `job_service._settle` retry (extend beyond identical re-run); HITL checkpoint/resume.
- **Size:** L.

---

### Phase D — Correctness, safety & team semantics (the missing middle)

#### D1 · Termination / convergence criteria
- **What:** Goal-satisfaction stop conditions distinct from per-agent caps: quorum, "good enough" (evaluator ≥ threshold), and deadlock/livelock detection (two members handing off forever).
- **Why:** Built reality terminates on "exhausted max_rounds" / "no tool calls" — mechanical, not goal-aware.
- **Size:** M.

#### D2 · Partial-failure recovery + idempotency
- **What:** When member C fails after A and B wrote side-effects, **quarantine/compensate** the siblings' dirty state rather than corrupting the shared board; dedupe keys for side-effecting connectors (github/notion/postgres) across re-dispatch so at-least-once delivery doesn't double-send.
- **Why:** The middle primitive that turns "N agents ran" into "a team produced one trustworthy result." Absent at every tier today.
- **Size:** L.

#### D3 · Cross-team budget envelope
- **What:** A pooled ceiling (`max_tokens_total`, `max_usd_total`, `max_sub_runs`, `ttl`) across a fan-out's sub-runs, enforced in the engine — re-opening the `ADR-005` per-harness "one budget surface" anti-decision for the *team* case.
- **Why:** Today a fan-out can spawn N sub-runs each individually under-budget while the aggregate is unbounded; `spend_service.estimate` is non-enforcing.
- **Size:** M.

#### D4 · HITL as a first-class team member
- **What:** A human is a *member* with capacity, routing (to the right human/role), an SLA/time-to-resolution that feeds team progress, and defined behaviour-while-blocked — not merely a safety gate.
- **Why:** Today HITL is only an escalation valve; behaviour while blocked on a human is undefined, and the human is the scarcest, slowest member and the likeliest stall point.
- **Builds on:** the engine task board (`task_service.py`) + HITL claim/complete/approve.
- **Size:** M.

#### D5 · Within-run tenant isolation + conflict arbitration
- **What:** Confused-deputy controls so that when members hold different delegated scopes (or a cross-org federated member), the shared transcript/blackboard cannot launder data across scope boundaries; and promote conflict *detection* to **arbitration-then-redirect** (assign a member to resolve a `CONTRADICTS`, not just record it).
- **Why:** The shared medium is otherwise a covert channel; detection without arbitration is inert.
- **Size:** S–M (isolation) + M (arbitration).

---

## 6. Coordination media — the decision guide

A team picks one or more media in its `orchestration.medium`. Use the right one per stage:

| Medium | Shape | Best for | Built on |
|---|---|---|---|
| **Parallel fan-out + barrier** | N members run concurrently, results merged | Independent gathering/analysis at scale (the 14-researcher stage) | B1 + B3 |
| **Job / task board** | First-class assignable tasks with a status lattice | Async, long-running, mixed human+agent work; durable backlog | engine `task_service` → board |
| **Round-table** | Members take turns over a shared transcript | Synchronous *deliberation*: debate, adversarial QA, consensus | `roundtable_service` (made structured) |
| **Blackboard** | Shared team-scope graph memory, read by traversal | Accumulating evidence many members read/extend concurrently | C4 (ADR-027 team scope) |
| **Structured hand-off** | Typed envelope passed member→member | Pipeline stages where stage N consumes stage N-1's typed output | B5 |
| **A2A invoke** | A member calls a sub-agent as a capability | Recursive decomposition, specialist delegation under scope-inheritance | B4 |
| **Head-switching** | One agent, one context, rotating role-prompt | Tiny/cheap jobs where parallelism & context-isolation don't matter | single tool loop (exists) |

**Rule of thumb:** *gathering* → parallel fan-out + blackboard; *deliberation* → round-table; *pipeline* → structured hand-off; *delegation* → A2A; *human-in-the-mix* → board. Head-switching is the degenerate single-context fallback, never the default for a real team (it sacrifices parallelism and context-independence).

---

## 7. End-to-end team-run lifecycle

```
1. OBJECTIVE          customer states an objective (+ inputs, constraints, success criteria)
2. PLAN               Planner (Harness Compiler) surveys substrate + emits a Team Harness
                      (OHM v1.1): members, sub-goals, dependency DAG, orchestration, budget
   └─ Gate (optional human review/approve of the plan)
3. DISPATCH           Coordinator reads orchestration; B1 primitives fan members out per the DAG
4. COORDINATE         members exchange work via the chosen media; every action → provenance
                      + run-tree; writes land on the blackboard; board tracks task state
5. MONITOR            progress signal + correlated run-tree; budget envelope enforced; HITL
                      members surfaced with SLA
6. EVALUATE           Evaluator scores stage/run vs success_criteria → structured verdict
7. REFINE (loop)      below threshold → re-task / replace / re-route / escalate → back to 3/4
                      (bounded by termination/convergence criteria)
8. AGGREGATE          reducer/synthesizer merges members' outputs into the deliverable
9. DELIVER / SERVE    output persisted (e.g. ingested to a graph); optionally a long-lived
                      inference Team Harness is published + exposed via gateway integration key
```

Steps 1–2 are Phase A/B; 3–4 Phase B; 5–7 Phase C; 8 Phase B; the safety/semantics of 4–7 are Phase D. Step 9 already works (KGS ingest + published-agent + gateway).

---

## 8. OHM v1.1 — a concrete team manifest (illustrative)

```yaml
ohm_version: "1.1"
metadata: { id: <uuid>, name: "market-intel-team", kind: team, owner_organization_id: <org> }
models:
  - { role: primary, binding: "anthropic/claude-opus-4-8", protocol_shape: openai-compatible,
      config: { credential_id: <byom-cred> } }
members:
  - role: researcher
    kind: agent
    manifest_ref: "org:<org>/research-agent@3"
    subgoal: "Gather cited evidence for the assigned sub-topic"
    fan_out: { over: "$.subtopics", max_parallel: 8 }     # → N concurrent researchers
    outputs_schema: { $ref: "#/schemas/evidence_batch" }
    depends_on: []
  - role: analyst
    kind: agent
    manifest_ref: "org:<org>/analysis-agent@2"
    subgoal: "Turn the merged evidence into scored findings"
    depends_on: [ researcher ]                            # fan-in barrier on researcher
  - role: reviewer
    kind: agent
    manifest_ref: "org:<org>/adversarial-reviewer@1"
    subgoal: "Refute weak findings; raise CONTRADICTS"
    depends_on: [ analyst ]
  - role: editor
    kind: human
    human_role: "domain-lead"
    subgoal: "Approve the final synthesis"
    depends_on: [ reviewer ]
orchestration:
  medium: [ blackboard, board ]
  style: >
    Fan out researchers in parallel over subtopics; barrier; run analysts;
    then an adversarial round-table for review; escalate the synthesis to the human editor.
  success_criteria: "Every finding cites ≥1 source; 0 unresolved CONTRADICTS; editor approves."
  termination: { max_wall_seconds: 7200, convergence: "evaluator>=0.8", max_rounds: 3 }
task_board: { columns: [ proposed, claimed, in_progress, blocked, done, escalated ] }
budget: { max_tokens_total: 8_000_000, max_sub_runs: 40, max_usd_total: 60, ttl_seconds: 10800 }
governance: { policy_set_ref: "org:<org>/team-default", redact_patterns: [ ... ] }
schemas:
  evidence_batch:
    type: object
    properties:
      records: { type: array, items: { $ref: "#/schemas/evidence_record" } }
  evidence_record:
    type: object
    properties:
      claim: { type: string }
      label: { enum: [ DIRECT, INFERRED, ASSUMPTION ] }
      source_url: { type: string }
      observed_at: { type: string }
```

A v1.0 single-entrypoint harness omits `members`/`orchestration`/`task_board` and runs exactly as today.

---

## 9. What we build on (do not rebuild)

| Existing asset | Reuse as |
|---|---|
| Single-harness plan-act-observe tool loop (`run_tool_use_loop`) | each Role-Agent's execution; the orchestration agent's own reasoning |
| Sequential round-table (`roundtable_service.drive`) | the deliberation medium (made structured + parallel-capable) |
| HITL task board + claim/complete/approve (`task_service.py`) | the board medium + HITL-as-member (D4) |
| Provenance + OTel + metering | per-member provenance; run-tree spine (C2) |
| `engine_jobs.harness_execution_id` link | the seam to extend into a full run-tree (C2) |
| KRS `EvalJudge` (#331) | the Evaluator seam, generalized to rubrics (C1) |
| ADR-027 `:Memory` store + `memory_client.py` | the blackboard (C4) |
| Neo4j graph + KRS retrieval | blackboard substrate + served inference |
| capability-registry connectors + executor framework | the A2A connector (B4) + any new tools |
| auth/ReBAC + credential broker + gateway integration keys | per-member scope-inheritance + external serving |

The foundations are real and non-trivial — this is an *extension*, not a rewrite.

---

## 10. Build sequence & sizing

| Phase | Items | Size | Unlocks |
|---|---|---|---|
| **A — contract & spine** | A1 OHM v1.1 · A2 team data model · A3 ADRs | M + M + S | makes a team *expressible*; gates everything |
| **B — runtime spine** | B1 orchestrators+barrier (L) · B2 orchestration agent (L) · B3 aggregator (M) · B4 A2A connector (M) · B5 hand-off envelope (M) | L | makes a team *run* |
| **C — eval, monitor, loop** | C1 evaluator (M) · C2 run-tree (M) · C3 progress (S–M) · C4 blackboard (M) · C5 closed loop (L) | L | makes a team *self-correcting & observable* |
| **D — correctness & safety** | D1 termination (M) · D2 failure recovery+idempotency (L) · D3 budget (M) · D4 HITL-member (M) · D5 isolation+arbitration (S–M + M) | L | makes a team *trustworthy* |

**Minimum viable team (MVT):** A1, A2, B1, B3, B5, C1, C2, C3, D1, D3 — expressible, runs a fan-out/fan-in pipeline, merges, is evaluated, observable as one tree, bounded by budget and convergence. B2/B4/C4/C5 and the rest of D raise it from "runs a pipeline" to "an adaptive, delegating, self-correcting team."

---

## 11. ADRs to open (the un-ADR'd coordination layer)

1. **ADR — Team Harness & OHM v1.1 team extension** (A1/A2): the manifest contract for a team.
2. **ADR — Coordination control & media** (B1/B2/B5/§6): the orchestration-agent contract, the three orchestrators, round-table/board/hand-off, and the medium taxonomy. *(closes the single largest meta-gap)*
3. **ADR — Harness Compiler / Planner** (Phase A/B): platform-baseline vs default-installed harness; the goal→manifest contract.
4. **ADR — A2A invocation & scope-inheritance** (B4/D5): how an agent dispatches an agent, and the per-call ACL.
5. **ADR — Flow-level evaluation & the closed loop** (C1/C5): the judge contract and the re-dispatch policy (and the autonomous-vs-HITL-gated boundary).
6. **ADR — Team budget envelope** (D3): re-open the `ADR-005` per-harness budget anti-decision for the team case.
7. **Status/retirement note on `ADR-005 L77`**: track sequential/parallel/conditional; record which original primitives (graph-resident team ontology, cascading per-agent budgets) are **retired** vs **deferred**.

---

## 12. Open decisions for the founder

1. **The controller posture.** The original vision deliberately disclaimed a central scheduler (`ARCH §15`); the current docs already chose a per-run **orchestration agent** but never ratified or built it. **Recommendation: ratify the orchestration agent** (ADR #2) — it is the minimal controller that preserves "choice is prose, mechanics are coded."
2. **Planner autonomy.** Does the Harness Compiler auto-emit a team plan from a bare objective, or always propose-then-human-approve (Gate)? **Recommendation: propose-then-approve by default**, with an opt-in autonomous mode per org/policy.
3. **Re-planning autonomy.** Is the closed loop allowed to re-task autonomously, or only HITL-gated? **Recommendation: autonomous re-task within budget/convergence bounds; HITL-gate any manifest mutation** (the `can_propose_harness_changes` path).
4. **Retire vs defer.** Explicitly record that the graph-resident `:Agent` team ontology (reversed by ADR-029) and cascading per-agent budgets (ADR-005) are **retired**, while cross-harness boards and consciousness drift-detection are **deferred** — to end the silent three-way divergence between vision, docs, and code that the audit found at nearly every pillar.

---

*This design is the product-runtime counterpart to the dev-time fleet that built Oraclous. Its three validation cases — the EURail assessment, bitcoin-gpt/doefin-gpt market intelligence, and the book studio — are worked end-to-end in `team-of-agents-use-case-playbooks.md`; each independently exercises every pillar above, which is the strongest evidence that this capability set is the right one.*
