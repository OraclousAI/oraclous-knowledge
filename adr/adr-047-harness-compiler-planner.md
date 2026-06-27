---
title: "ADR-047 — Harness Compiler / Planner: the prose on-ramp — an English objective compiles to a runnable OHM v1.1 Team Harness (planner / capability-surveyor / manifest-drafter / reviewer), passing the SAME dry-run validation as the importer, capability-absence-bounded, NL-refine as a structural delta"
---

# ADR-047 — Harness Compiler / Planner (the prose on-ramp)

## Status

| Field | Value |
| --- | --- |
| Status | Proposed |
| Date | 2026-06-27 |
| Approved by | Pending Reza/CTO |
| Supersedes | None — fills the un-ADR'd **P1 (upfront planning / decomposition)** pillar that [ADR-005](adr-005-workflow-concept-retirement.md) promised and never ratified |
| Superseded by | None |
| Driving artifact | The platform's **co-equal prose on-ramp** is missing: today the only planned front door is *import an existing `.claude/agents` team* (E2). A user who states an objective in English and has nothing to import has **no path**. Epic: [oraclous-backend #391](https://github.com/OraclousAI/oraclous-backend/issues/391) (E10 — Compiler harness `describe→team` + seed defaults + eval-set). Design: [Team-of-Agents Capability Design](../../oraclous-backend/docs/team-of-agents-capability-design.md) §3 (the stack, PLANNER at top), §7 (lifecycle starting at OBJECTIVE), §11 (ADR list item #3 "Harness Compiler / Planner"), §12 (open founder decisions, esp. #2 planner autonomy). |

## Context

The Goal promises **two on-ramps**: *import an existing team* **and** *"describe in English → it builds the team → refine in NL"*. Only the first is even planned (E2). The second — the **Harness Compiler / Planner** — was marked "superseded by R3.5" and then **never rebuilt**: the R3.5 pivot jumped straight to the security pass and skipped the compiler entirely. Against the five pillars of a working team, **P1 (upfront planning / decomposition) is the Harness Compiler, and it has zero ADR, is spec-inexpressible, and is `Built? = None`** (capability-design §1). The prose front door — *the platform's co-equal on-ramp for the user who does not already have a `.claude/agents` directory* — does not exist.

This is **NOT the importer.** The importer ([ADR-034](adr-034-adoption-first-import.md) / [ADR-045](adr-045-prose-showrunner-dag-import-adapter.md)) is the other co-equal on-ramp that reads an existing agent setup and lowers it to OHM. The Planner is its co-equal on-ramp: it **synthesizes** a team from nothing but a prose objective. They converge on **one gate** — *run it, does it achieve the objective?* — and, critically, on **one validator**.

**The foundation the Planner builds on is 100% shipped (verified by reading this repo).** The Planner is greenfield on a complete base; every runtime primitive it needs already exists:

- **OHM v1.1 Team Manifest + DAG resolver (the output contract).** `OHMManifest` (`packages/ohm/src/oraclous_ohm/manifest.py:260`) with the v1.1 team blocks `OHMMember` (`:122`), `OHMOrchestration` (`:207`), `OHMTaskBoard` (`:219`), `OHMBudget` (`:236`), `OHMFanOut` (`:88`), `OHMRunIf` (`:106`), `OHMGateBattery` (`:191`). A `kind:"human"` member with no `human_role` fails closed at the validator (`manifest.py:144-148`). `manifest.execution_stages()` (`:296`) → `topological_stages()` (`dag.py:16`) raises `OHMDagError` fail-closed on a cycle, a duplicate role, or a `depends_on` to an unknown member.
- **The importer's dry-run validator (the Planner reuses it verbatim — there is no second validator to write).** `ImportReport` + `_build_report()` + `would_block()` + `render_report()` (`packages/ohm/src/oraclous_ohm/import_/setup.py:30,50,72,274`), and the convergent assembler `assemble_team()` (`import_/assemble.py:46`) whose closing step round-trips the assembled manifest through `load_ohm()` and emits `F-ASSEMBLY-INVALID` (blocking) on failure (`assemble.py:151-153`). Blocking flags fold into `would_block` → `render_report()` prints `GO: BLOCKED`.
- **Capability-absence as a structural compile-time ceiling ([ADR-032]).** `member.tools` (`manifest.py:134`) is deny-by-default, never widened; the dispatch guard is `assert_capability_allowed()` (`capabilities.py:27`), cross-member it is `assert_subharness_within_ceiling()` (`capabilities.py:43`), and the coordinator route guard fail-closes on a route to an undeclared member (`orchestrate.py:277-279`).
- **The team runtime that runs a compiled team ([ADR-035] / [ADR-043]).** `run_team()` (`orchestrate.py:96`: DAG + fan-in barrier + `fan_out` + human-gate pause + typed `HandoffEnvelope`), the opt-in reasoning coordinator `run_team_coordinated()` (`:228`), and the ADR-043 bounded conductor.
- **The KRS `EvalJudge` (the eval seam).** `EvalJudge` Protocol + `OpenAIEvalJudge` (`services/knowledge-retriever-service/.../services/eval_judge.py:28,40`); endpoint `POST /internal/v1/evaluate` → `Verdict` ([ADR-037], #469). Named gate batteries via `OHMGateBattery` for the EURail 10-gate.
- **The deployed-stack entry point.** `POST /v1/engine/team-runs` (`services/execution-engine-service/.../routes/team_run_routes.py`), **gateway-reachable today** via the route-table entry `("/v1/engine", "EXECUTION_ENGINE_URL")` — so the compiler-team runs through the gateway (`:8006`) with **no new gateway routing**. The capability-survey surfaces `/api/v1/tools` and `/api/v1/capabilities` are gateway-reachable too.

**The one wiring gap to note:** the importer's `import_setup`/dry-run is **not yet exposed by any service** (no `services/` file imports `oraclous_ohm.import_`), and no planner/compiler code exists. So the Planner is greenfield only at the **prose-in front door + the four compiler member prompts/sub-harnesses + seed defaults + eval-set**, on top of a complete package-layer foundation.

**Best-practice survey (what the field does, and what to borrow vs. do differently).** The one near-exact precedent is **AutoGen / AG2 AutoBuild** (`AgentBuilder.build` / `build_from_library`): a build-manager LLM reads a task string and *generates the team*, selecting from an agent library via embedding similarity. Everything else clusters into (a) *decompose-a-plan-not-a-team* (CrewAI `AgentPlanner` plans over a fixed human-authored crew; MetaGPT fixes roles by a hard-coded SOP; BabyAGI/AutoGPT produce a flat task queue with no real DAG) or (b) *author-by-hand-with-assist* (LangGraph supervisor, OpenAI Agent Builder — the human draws the graph). Two cross-system signals are load-bearing here: (1) the dominant *failure* mode is **hallucinated tools** — planners that plan against the open world reference functions that don't exist; this is precisely **why Microsoft deprecated and removed the Semantic-Kernel Handlebars/Stepwise planners** in favor of native function-calling ("a separate up-front rigid plan reduces speed, cost, and accuracy"); and (2) the field is **retreating from mandatory up-front approval gates** (OpenAI is winding down Agent Builder; CrewAI's planning is an opt-in flag). The Planner's foundation lets it be *ahead* of every surveyed system on the three things they get wrong: a **first-class validated DAG** (none emit one — AutoBuild ships a flat GroupChat, MetaGPT a fixed pipeline), a **capability-absence compile-time ceiling** (every other system whitelists at *call* time, if at all), and a **single validator shared with the import on-ramp**.

## Decision

**Build the Harness Compiler / Planner as a Team Harness itself — not platform code ([ADR-003]: actors are descriptors, the platform interprets them) — that takes a prose objective and emits a runnable OHM v1.1 Team Harness whose output passes the EXACT SAME dry-run validation as the importer's output.** Six sub-decisions.

### 1. The goal→manifest contract (the describe→team seam)

**Input:** a prose `objective`, plus optional `inputs`, `constraints`, and `success_criteria`.

**Output:** a single schema-valid `OHMManifest` with `ohm_version:"1.1"`, `metadata.kind:"team"`, populated `members[]` (each `role`/`kind`/`manifest_ref`/`subgoal`/`depends_on`/`fan_out`/`inputs`/`outputs_schema`), an `orchestration` block (`medium`/`style`/`success_criteria`/`termination`), a `task_board`, a `budget` envelope, and `governance` — **plus** the per-role `sub_harnesses` dict (role → generated single-agent OHM) without which a team *loads but cannot run* (its `manifest_ref`s resolve to nothing registered).

**The output must pass the importer's validator unchanged.** The Planner's reviewer feeds the drafted manifest through the **same** `assemble_team()` + `ImportReport`/`would_block`/`render_report()` path the importer uses (`import_/assemble.py:46`, `import_/setup.py:30`), asserting:
- schema-validates as OHM v1.1 (round-trips through `load_ohm()`);
- the DAG is acyclic / runnable (`topological_stages()`, `dag.py:16` — fail-closed on cycle / duplicate role / unknown `depends_on`);
- every member's `tools[]` resolve to surveyed capabilities;
- **capability-absence holds** ([ADR-032]) — each `member.tools` is the immutable hard ceiling;
- a missing capability **fails closed with a gap report** — a blocking `ImportFlag` (the importer's `F-*` vocabulary; e.g. an `F-CAPABILITY-MISSING` analog) folded into `would_block` → `GO: BLOCKED` — **never a hallucinated tool**.

This is the load-bearing reuse discipline (#391 "Build on, don't rebuild"): **one validator, two on-ramps.** The contract seam is `assemble_team()`/`ImportReport` *extended with a prose-in path* (today `import_setup` is filesystem-in; the Planner produces the same `members[]`/`orchestration` inputs from prose and calls the *same* assembler + builds the *same* report). It is **not** a second validator.

### 2. The compiler AS a Team Harness (planner / capability-surveyor / manifest-drafter / reviewer)

The compiler is itself an OHM v1.1 `kind:team` manifest, built and run by the *exact same* shipped runtime — no new platform code. Four `OHMMember`s in a linear `depends_on` chain, resolving to four sequential `execution_stages()`:

| Member | Role | Tools (its ceiling) | Output |
| --- | --- | --- | --- |
| **planner** | Decompose the prose objective into sub-goals, roles, and a dependency DAG (the spine). | reasoning-only | a sub-goal/role/edge sketch |
| **capability-surveyor** | Survey the **live** registry + the **seed capability inventory** to know which tools and member archetypes are actually available to plan against — the **single source the drafter may draw from**. | `/api/v1/tools` (list), `/api/v1/capabilities` (list + `/match`) | a **typed catalog** of available tool groups + member archetypes + reference topologies |
| **manifest-drafter** | Emit the OHM v1.1 team manifest, drawing `members[].tools` **exclusively from the surveyor's catalog**. | reasoning-only | the user's draft Team Harness (a *second*, distinct OHM manifest) |
| **reviewer** | Run the draft through the **importer's dry-run validator** (decision 1). Blocking flag → bounded re-draft; clean → hand back / run. | reasoning-only | the validated Team Harness, or a gap report |

Each member's reasoning is the shipped single-agent `run_tool_use_loop`; `run_team()` (`orchestrate.py:96`) drives them with the typed `HandoffEnvelope` threading each member's output forward. **The compiler-team runs through the deployed gateway path** (`POST /v1/engine/team-runs` with `manifest` = the compiler-team OHM + `sub_harnesses` = the four member bodies) — gateway-reachable today, satisfying the deployed-stack/gateway e2e law with no new routing.

**Borrowed from AutoBuild:** the build-manager-as-an-agent pattern and the **library + embedding-similarity capability survey** — for a large registry the surveyor retrieves the top-k relevant tools/archetypes per sub-goal by embedding similarity rather than dumping the whole registry into the prompt. **Done differently:** the surveyor's catalog is not a convenience to shrink the prompt — under capability-absence ([ADR-032]) it is the **structural source of the allowed set** enforced at *compile* time; the drafter may emit `member.tools` *only* from it, and a sub-goal needing an unsurveyed capability must fail closed with a gap report. This is strictly stronger than the field's call-time whitelisting.

### 3. The deterministic plan guardrails + a bounded generate→validate→repair loop

Validation is a **deterministic, rule-based gate run pre-execution** (the field consensus; catches ~95% of hallucinated calls before any run), and it is the importer's validator (decision 1) — not an ad-hoc one. The reviewer runs **generate → validate → repair → re-validate → escalate**: a blocking flag drives a **bounded** re-draft (N tries, default 2, max 3) by feeding the validator's structured `ImportFlag` errors back to the drafter; after the cap, it **fails closed with the gap report** rather than shipping or looping. Validation failure drives a *repair*, not a bare rejection.

### 4. NL refine as a structural delta — never a blank re-draft

The "refine in NL" half of the on-ramp. A natural-language edit ("add a fact-checker", "make research parallel", "the editor is human") is parsed into a **typed structural operation** over the *existing* manifest — `add_member` / `set_fan_out` / `change_kind(agent→human)` / `add_depends_on` — and applied as a patch, then re-run through the **same** dry-run validator (decision 1). The model emits the *patch*, not the whole manifest (a function-calling-shaped problem — the small typed edit surface is exactly what the SK deprecation says LLMs are now reliable at). The testable contract is the **preserve-the-rest invariant**: assert the structural delta *and* that every untouched member/edge is byte-identical. A delta that cycles the DAG, breaks capability-absence, or references an unsurveyed tool is repaired/rejected before acceptance — "add a fact-checker" must give the new member a *surveyed* tool set and a `depends_on` that keeps the DAG acyclic. (No surveyed competitor ships validated NL-delta editing of a team spec; the manifest-as-data + single-validator substrate makes Oraclous first.)

### 5. Seed defaults (what a from-scratch user plans against)

A from-scratch user has nothing to survey, so E10 seeds the org with:
- **capability inventory** — the catalog of available member archetypes + tool groups the surveyor plans against (its embedding-similarity library);
- **policy template** — a default `governance.policy_set_ref` / redact patterns so a compiled team is **governed by default**;
- **reference catalog** — reference topology shapes (fan-out/fan-in pipeline, standing-team, gated-pipeline) the planner composes from;
- **bootstrap / diff-accept** — first-run bootstrap of these defaults into an org, and a **diff-accept** flow so re-seeding does not clobber a user's edits (the same re-import merge-vs-clobber discipline E2/O5 use).

### 6. Autonomy posture — compile-and-run by default, plan-approval opt-in

**The posture is settled — compile-and-run by default; plan-approval is an opt-in *setting*, not a precondition.** This is **already decided by the authoritative north-star lock** (which wins on divergence): §4 ("Mandatory propose-then-human-approve Planner gate — **opt-in**; experienced conductors import-and-run; plan-approval is a setting") + item 15 ("mandatory plan-approval … **all opt-in** — a single-owner autonomous team is never taxed by machinery it doesn't use"), corroborated by the R7 release doc ("describes an objective in plain English, **presses GO, and it runs**") and already cited by ADR-037 ("mandatory plan-approval = opt-in (Lock item 15)"). The capability-design §12.2 recommendation (propose-then-approve default) was **overridden** by the lock. This is **not an open decision** — it is recorded here as the lock's settled posture: "an experienced conductor compiles-and-runs; do not build a required approval gate into the compile flow."

This is **safe by construction** in a way AutoBuild's ungated auto-generate is not: the team is **fully validated + capability-absence-bounded + budget-capped before it runs**. The autonomy choice is anchored on the **SK-deprecation evidence**: the industry retired rigid, pre-baked planners *because the runtime had to follow them slavishly*. Oraclous escapes that trap for a specific reason — its plan output is a **declarative OHM manifest interpreted by a reasoning conductor ([ADR-043]), not a frozen step script** ("governance in code, flexibility in prose"). So it gets an up-front *structural* plan (the DAG/roster/budget — the things you *want* fixed for governance/audit) **plus** runtime adaptivity inside it. The opt-in approval gate, when enabled (per org/policy), should surface when (a) the plan touches send/publish/spend capabilities, or (b) the surveyor returned a gap report and the drafter defaulted around it — "approval where it earns its cost," never a blanket precondition.

### 7. Evaluating a non-deterministic generator (the three-layer eval-set)

NL→team is non-deterministic generation, so the eval is a three-tier stack (matching the field consensus and #391's `How it's tested`):

1. **Deterministic plan guardrails** (every generation, exact pass/fail) — decision 1's checks. Cheap, run on every generation.
2. **End-result equivalence against a known-good oracle** — the **EURail-ledger equivalence test**: give the compiler EURail's objective *in prose*, run the generated team, and check it reproduces the shipped **909-record ledger** about as well as the *imported* EURail team does, passing the **10-gate** report-editor battery (`OHMGateBattery`). EURail is the only case with a known-good output to diff against — a *real oracle* most systems lack.
3. **Reference-objective eval-set + LLM-judge** (quality, the ship-bar) — ~15–30 prose objectives, each with a runnable acceptance check + a rubric the KRS `EvalJudge` (`POST /internal/v1/evaluate` → `Verdict`) scores. **Split the rubric** into **plan-adequacy** (judged on the *manifest* — sub-goal coverage, right roles, no missing capability, sane DAG — cheap, no run needed) vs. **run-outcome** (judged on the *executed* deliverable). Judging the plan directly catches a structurally-wrong team early and cheaply, before a costly team run. **Sample N times per objective and report variance** (one run of a non-deterministic generator is statistically meaningless); **de-bias the judge** by randomizing rubric-dimension order and calibrating against a few human-graded plans. **Ship-bar = passes K-of-N** ("useful for early adopters", not "perfect for arbitrary prose"). The compiler is a harness, iterated without architecture change.

## Founder decisions (for Reza)

> **Autonomy (#1) is NOT open — it was already decided by the authoritative north-star lock** (compile-and-run by default; mandatory plan-approval opt-in). It is listed below only for traceability. The genuine open items are the two minor tunables (#2 repair bound, #3 ship-bar), both with sensible proposed defaults.

| # | Decision | Recommendation | Status |
| --- | --- | --- | --- |
| **1 — Planner autonomy** | **Already settled by the authoritative north-star lock** (recorded for traceability, not re-opened). | Lock §4 + item 15 make mandatory plan-approval **opt-in** → **compile-and-run is the default** (corroborated by the R7 release doc + ADR-037; the capability-design §12.2 propose-then-approve recommendation is overridden — "the lock wins"). Implemented as decision 6. | **SETTLED by the lock — not open.** |
| **2 — Repair-loop bound** | N re-draft tries before fail-closed. | Default **2**, hard max **3**, then fail-closed gap report. | Proposed default; Reza may tune. |
| **3 — Ship-bar K-of-N** | The K and N for the reference-objective eval-set. | Pick K-of-N to mean "useful for early adopters" (not "perfect for all prose"); e.g. ≥80% of ~20 objectives over N≥3 samples each. | Proposed; final K/N is a product call. |
| **Out of scope (noted, not decided here)** | **Re-planning / closed-loop autonomy** (capability-design §12 #3) is owned by **E8**, not E10. Controller posture (#1) and retire-vs-defer (#4) are already ratified in ADR-035/ADR-033. | — | Owned elsewhere. |

## Consequences

### Positive

- **The platform gains its co-equal prose on-ramp.** A user states an objective in English and Oraclous builds the team — the missing half of the Goal. P1 (planning) moves from `Built? = None` to shipped, ADR'd.
- **One validator, two on-ramps.** Import and compile converge on the *identical* `assemble_team()`/`ImportReport` gate — the prose front door cannot drift from the import front door, and there is no second validator to maintain.
- **Capability-absence makes hallucinated tools structurally impossible.** The field's #1 failure mode (hallucinated tools → the SK deprecation) cannot occur: the drafter emits `tools[]` only from the surveyor's catalog, the reviewer enforces it via the shared validator, and the only alternative to a real capability is a fail-closed gap report. Provably stronger than every surveyed system.
- **No new platform code, no new gateway routing.** The compiler is *itself* a team harness on the shipped runtime, reachable through the gateway today — small blast radius, e2e-law-compliant by construction.
- **A first-class validated DAG + validated NL-delta refine** — two things no surveyed competitor ships, enabled by the manifest-as-data + single-validator substrate.
- **The autonomy posture is grounded in evidence**, not preference: the declarative-manifest-over-a-reasoning-conductor design is precisely the one that escapes the rigid-planner failure SK retired.

### Negative

- **Generation is non-deterministic and adversarial.** A prose objective can be underspecified, ambiguous, or hostile. Mitigation: underspecified → asks/defaults (never hallucinate); the three-layer eval samples N and reports variance; the K-of-N ship-bar is explicitly "early adopters", not "all prose"; the `use-case-guardian` checks every PR for a regressed acceptance item or a new "but first you must…".
- **The prose-in front door + the four member prompts are net-new surface.** They must be exercised on the deployed stack through the gateway (the M4 acceptance run), not on CI-green alone.
- **The repair loop and N-sample eval add (capped) model-call cost.** The bound (decision 3) and the cheap plan-adequacy-first judge tier (decision 7) contain it — most bad teams are caught on the manifest-only tier before a costly run.
- **A wrong-but-valid team is possible** — a manifest that passes every deterministic guardrail yet doesn't achieve the objective. This is exactly what eval layers 2–3 (the EURail oracle + the LLM-judge) exist to catch; the deterministic gate alone is necessary, not sufficient.

## Alternatives considered

### A. A single up-front LLM that turns the prose into the full team in one shot (the SK Handlebars/Stepwise shape)

Prompt one LLM to convert the objective into `members[] + depends_on + tools` in a single call, with no survey, no staged members, no repair loop. **Rejected** — this is the exact path Microsoft *deprecated and removed*: a brittle, hallucination-prone one-shot planner over a hand-rolled plan DSL lost to native tool-calling + a bounded dynamic manager. For Oraclous it would put the ceiling-fidelity-critical `tools[]` derivation ([ADR-032]) inside an ungrounded LLM with no surveyed catalog to draw from and no validator-driven repair — the precise hallucinated-tool failure capability-absence exists to prevent. The staged survey→draft→review chain with a bounded repair loop (decisions 2–3) dominates.

### B. Plan a task list over a fixed, human-authored crew (the CrewAI `AgentPlanner` / BabyAGI shape)

Generate a *plan* over a team the human composed, not the team itself. **Rejected** — it does not build the team, which is the entire point of the prose on-ramp; it presupposes the very thing the user doesn't have. BabyAGI's flat task queue additionally has no real DAG (the cited weak point), and Oraclous's whole differentiator is a first-class validated `depends_on`/`fan_out`/barrier DAG.

### C. A fixed-SOP role template (the MetaGPT shape)

Hard-code the roles and the pipeline (PM → Architect → Engineer → QA) and let the objective only fill each role's content. **Rejected** — it cannot decompose an arbitrary objective into the *right* team; it solves one domain by fiat. The planner must derive roles and edges from the objective, not stamp a template — the reference catalog (decision 5) offers topology shapes to *compose* from, never a frozen pipeline.

### D. Write a second validator for the compiler's output

Give the compiler its own validation pass independent of the importer's. **Rejected** — it violates the "build on, don't rebuild" discipline (#391) and creates two drifting definitions of "runnable team". The compiler's output *must* pass the *same* `assemble_team()`/`ImportReport` gate as an imported team — one validator, two on-ramps. The seam is the importer's assembler *extended* with a prose-in path, not duplicated.

### E. A mandatory propose-then-human-approve gate on every compile

Require human plan-approval before any compiled team runs (capability-design §12.2's default recommendation). **Rejected as the default** per the #391 lock §4 CUT — the field is retreating from mandatory up-front gates (OpenAI winding down Agent Builder; CrewAI's planning opt-in), and the team is *safe by construction* (validated + capability-absence-bounded + budget-capped before it runs). Kept as an **opt-in setting** that surfaces on send/publish/spend or gap-report-defaults (decision 6). *(Settled by the authoritative north-star lock §4/item-15 — recorded, not open.)*

### F. NL refine by blank re-draft (the AutoBuild / conversational-generator shape)

Re-run the generator on a modified prompt for every NL edit. **Rejected** — it loses the rest of the manifest, is non-deterministic turn-to-turn, and cannot satisfy the preserve-the-rest invariant. The structured-output discipline applied to *edit ops* (decision 4) keeps every untouched member byte-identical and re-validates the patch through the same gate.

### G. A standalone compiler/planner service

Stand up a service to plan and emit OHM. **Rejected** for the same reason ADR-034/045 rejected an import microservice: the compiler is a **Team Harness** ([ADR-003]) run by the shipped runtime and reached through the existing `/v1/engine/team-runs` gateway route — a new service is new platform code where a descriptor suffices, and splits the planner from the runtime + validator it must track.

## Implementation notes — the E10 child issues this implies

E10 (#391) is **Greenfield** at the design level (it lifts the *design* from the original R7 "Flow-1 Compile", not reusable code) but composes almost entirely from shipped seams. Each ships as a `[tests]`→`[impl]` pair (ADR-010, TDD), bundled per the PR-bundling law (one PR / multiple commits), guardian-checked, proven on the deployed stack through the gateway on real BYOM — never CI-green alone. The child issues:

1. **`[adr]` Compiler Harness / Planner (this ADR-047)** — the goal→manifest contract, the compiler-as-a-Team-Harness posture, compile-and-run-by-default / approval-opt-in. **Gates all other E10 issues.** Authored by `solution-architect`, CTO-accepted.
2. **The compiler AS a Team Harness** — author planner + capability-surveyor + manifest-drafter + reviewer as an OHM v1.1 `kind:team`; prose in → schema-valid Team Harness out, passing the **same E2 dry-run validation** (capability-absence + acyclic DAG + tools-resolve + fail-closed gap report) via the importer's `assemble_team()`/`ImportReport` extended with a prose-in path. Net-new: the prose front door + the four member sub-harnesses; reuse: the validator, the runtime, the registry survey surfaces. *(Serves acceptance item 1 complement + the deterministic plan guardrails.)*
3. **NL review/edit refine loop** — apply a NL edit as a typed structural delta (`add_member` / `set_fan_out` / `change_kind` / `add_depends_on`) on the existing manifest, re-validated through the same gate, preserving the rest. *(Serves the "refine in NL" half.)*
4. **Seed defaults** — capability inventory (the surveyor's catalog) + policy template (`governance.policy_set_ref`/redact) + reference topology catalog + bootstrap/diff-accept (re-seed without clobbering user edits). *(Serves a from-scratch user + governed-by-default.)*
5. **Compiler eval-set** — reference objectives + the split plan-adequacy/run-outcome LLM-judge rubric (KRS `EvalJudge` / `core/evaluate`) + the **EURail-ledger equivalence test**, wired to a **K-of-N** ship-bar, sampling N per objective with rubric-order de-bias. *(Serves the EURail equivalence acceptance + the M4 ship-gate.)*

**Explicitly OUT (lock §4 CUT):** the mandatory approval gate (→ opt-in), re-planning/closed-loop autonomy (→ E8), the importer/DAG-from-source/batteries/dual-substrate/single-tenant GO (→ E2/E5/E6/E7 — E10 *consumes* their seams), and "perfect generation for all prose".

**Validation reuses the shipped v1.1 checks unchanged:** `dag.topological_stages` (acyclicity / unknown-`depends_on` / duplicate-role, fail-closed), the `OHMMember` validator (`kind:human ⇒ human_role`), `assemble_team` + `ImportReport`/`would_block`/`render_report`, and `assert_capability_allowed` / `assert_subharness_within_ceiling`. The emitted documents are standard OHM v1.1, so they sign/version/govern through the existing ADR-002 path and run on the unchanged ADR-035/043 runtime via `POST /v1/engine/team-runs` through the gateway.

## References

- **Epic** [oraclous-backend #391](https://github.com/OraclousAI/oraclous-backend/issues/391) — E10 (the prose on-ramp; build-on-don't-rebuild table; the 3-layer eval; the lock §4 CUT list).
- **Design** [Team-of-Agents Capability Design](../../oraclous-backend/docs/team-of-agents-capability-design.md) — §3 (the stack, PLANNER at top), §7 (lifecycle from OBJECTIVE), §10 (build sequence), §11 (ADR #3 Harness Compiler / Planner), §12 (open founder decisions, #2 planner autonomy).
- [ADR-031 — OHM v1.1 Team Manifest](adr-031-ohm-v1.1-team-manifest.md) — the `members[] / depends_on / fan_out / subgoal / orchestration / pooled-budget` schema the drafter emits and the refine-edits mutate; the DAG/topo resolver.
- [ADR-032 — Capability-Absence as a Structural Gate](adr-032-capability-absence-structural-gate.md) — the immutable `tools[]` compile-time ceiling; the drafter draws only from the surveyor's catalog, missing capability → fail-closed gap report, never an auto-grant.
- [ADR-035 — Coordination Control & Media](adr-035-coordination-control-and-media.md) — the team runtime the compiler-team and the compiled team both run on (`run_team` / `run_team_coordinated`, the `HandoffEnvelope`, the dispatch-time ceiling, "choice is prose, mechanics are coded").
- [ADR-037 — Flow-Level Evaluation (BYOM judge / `core/evaluate`)](adr-037-flow-evaluation-byom-judge.md) — the `EvalJudge` / `POST /internal/v1/evaluate` → `Verdict` seam the eval-set reuses for plan-adequacy + run-outcome scoring.
- [ADR-043 — the conductor](adr-043-conductor.md) — the reasoning conductor that interprets the declarative manifest at run time; the basis for "up-front structure + runtime adaptivity" that anchors the compile-and-run-by-default posture.
- [ADR-034 — Adoption-First Import](adr-034-adoption-first-import.md) / [ADR-045 — Prose-showrunner → DAG import adapter](adr-045-prose-showrunner-dag-import-adapter.md) — the co-equal (import) on-ramp; the shared `assemble_team()`/`ImportReport` dry-run validator (one validator, two on-ramps); the O8 dry-run + flag-not-guess discipline.
- [ADR-003 — Platform-as-Code, Actors-as-Harnesses](adr-003-platform-as-code-actors-as-harnesses.md) — the compiler is a descriptor, not platform code. [ADR-005 — Workflow Concept Retirement](adr-005-workflow-concept-retirement.md) — the un-ratified P1 (planning) pillar this ADR fills.
- **Frameworks surveyed:** AutoGen/AG2 **AutoBuild** (`AgentBuilder.build` / `build_from_library` — the near-exact precedent; the library + embedding-similarity survey borrowed); CrewAI `AgentPlanner` / hierarchical process (plan-over-a-fixed-crew, opt-in planning); MetaGPT (fixed-SOP roles); BabyAGI / AutoGPT (flat task queue, no DAG); LangGraph supervisor & OpenAI Agent Builder (human authors the graph); **Semantic Kernel — the deprecation of the Handlebars/Stepwise planners** (the autonomy-posture evidence — rigid up-front planners retired for native function-calling).
- **Shipped code anchors (read in this repo):** `packages/ohm/src/oraclous_ohm/manifest.py:260` (`OHMManifest`), `:122` (`OHMMember`), `:144-148` (`kind:human ⇒ human_role`), `:207` (`OHMOrchestration`), `:219` (`OHMTaskBoard`), `:236` (`OHMBudget`), `:88` (`OHMFanOut`), `:106` (`OHMRunIf`), `:191` (`OHMGateBattery`), `:296` (`execution_stages`); `dag.py:16` (`topological_stages`); `capabilities.py:27` (`assert_capability_allowed`), `:43` (`assert_subharness_within_ceiling`); `import_/setup.py:30` (`ImportReport`), `:50` (`would_block`), `:72` (`_build_report`), `:146` (`import_setup`), `:274` (`render_report`); `import_/assemble.py:46` (`assemble_team`), `:151-153` (`load_ohm` round-trip + `F-ASSEMBLY-INVALID`); `orchestrate.py:96` (`run_team`), `:228` (`run_team_coordinated`), `:277-279` (undeclared-member fail-close); `services/execution-engine-service/.../routes/team_run_routes.py` (`POST /v1/engine/team-runs`); `services/application-gateway-service/.../domain/route_table.py` (`/v1/engine`, `/api/v1/tools`, `/api/v1/capabilities`); `services/knowledge-retriever-service/.../services/eval_judge.py:28,40` (`EvalJudge` / `OpenAIEvalJudge`).
- [ADR index](index.md)

## Revision history

| Date | Change |
| --- | --- |
| 2026-06-27 | Initial draft (Proposed). Decides the **Harness Compiler / Planner** — the platform's co-equal prose on-ramp. (1) The goal→manifest contract: prose objective → schema-valid OHM v1.1 Team Harness + `sub_harnesses`, passing the SAME `assemble_team()`/`ImportReport` dry-run validator as the importer (one validator, two on-ramps). (2) The compiler AS a Team Harness — planner / capability-surveyor / manifest-drafter / reviewer as a `kind:team` on the shipped runtime, reachable through the gateway today; the surveyor's catalog is the single source the drafter may draw `tools[]` from (capability-absence, ADR-032). (3) Deterministic plan guardrails + a bounded generate→validate→repair→escalate loop. (4) NL refine as a typed structural delta (add_member / set_fan_out / change_kind / add_depends_on), re-validated, preserve-the-rest invariant. (5) Seed defaults (capability inventory / policy template / reference catalog / bootstrap-diff-accept). (6) Autonomy posture: **compile-and-run by default, plan-approval opt-in** per the #391 lock §4 CUT (overriding capability-design §12.2; settled by the authoritative lock §4 + item 15), anchored on the SK-deprecation evidence + the ADR-043 declarative-manifest-over-a-reasoning-conductor design. (7) Three-layer eval for a non-deterministic generator: deterministic guardrails → EURail-ledger equivalence oracle → reference-objective LLM-judge (split plan-adequacy / run-outcome, sample-N, K-of-N ship-bar). Greenfield only at the prose front door + four member prompts + seed defaults + eval-set; all runtime primitives shipped. E10 epic #391. Pending Reza/CTO. |
