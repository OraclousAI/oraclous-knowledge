---
title: "ADR-045 — Prose-showrunner → DAG import adapter: derive depends_on + scoped objective_slice + skill-driver staging from a prose coordinator skill"
---

# ADR-045 — Prose-showrunner → DAG import adapter

## Status

| Field | Value |
| --- | --- |
| Status | Accepted |
| Date | 2026-06-27 |
| Approved by | Reza Jahankohan |
| Supersedes | None |
| Superseded by | None |
| Driving artifact | The #440 book-GO end-to-end (the third north-star use case — book studio — pressed GO). [Team-of-Agents — North-Star Lock](../product/team-of-agents-north-star-lock.md) §6 acceptance item 3 ("the inter-member DAG is derived from the source"); [ADR-034](adr-034-adoption-first-import.md) §6 (DAG-from-source) — its stated-but-unshipped prose-showrunner branch. Parent issue: oraclous-backend #407 (skill-resolution / charter / single-skill-orchestrator adapter). |

## Context

[ADR-034](adr-034-adoption-first-import.md) decided the import front door: read an existing agent setup, emit a runnable OHM v1.1 Team Harness (ADR-031), and **derive the inter-member DAG from the source** (its §6, Lock acceptance item 3). ADR-034 §6 explicitly wrote the intent for a *prose* coordinator: *"Showrunner routing + the 7-gate sequence (book) → the gate sequence A–G becomes an ordered chain of `kind: human` blocking nodes interleaved with the agent members, and the showrunner/coordinator-skill routing becomes the `orchestration.style` prose + `depends_on` edges."* [ADR-035](adr-035-coordination-control-and-media.md) then built the runtime that **runs** that DAG (`run_team` / `run_team_coordinated`, the typed `HandoffEnvelope`, the dispatch-time ceiling, the blocking-gate-node).

**The #440 book-GO e2e exposed the gap precisely.** The book case's per-chapter pipeline lives in `book/.claude/skills/book-studio/SKILL.md` as a `chapter <CH-NN>` block (read, lines 43–59): a numbered `1.→10.` sequence, `∥` parallel markers (`7. fact-checker ∥ prose-lint`), `──▶ GATE A/B/C` human-gate interleaving (lines 48/51/55), a `── BLOCK on CRITICAL` conditional halt (line 53), an `(optional)` conditional step (line 48), and an arrow notation (`research-scout → research/raw/ + research/briefs/CH-NN.md`) where each step *produces* an artifact the next step *consumes*. There is **no `modules/<wave>/` directory** — the DAG lives entirely in prose. So today the whole book pipeline imports to **zero members**, blocked.

The current state, grounded in the shipped code (read in this repo):

- **The importer derives a DAG only from a *structured* layout, and fail-closes on prose.** `adapt_orchestrator_skill` (`packages/ohm/src/oraclous_ohm/import_/orchestrator.py`) requires a `modules/<wave>/*.md` directory layout; absent it, it emits **`F-ORCH-UNSTRUCTURED` (severity `blocking`)** and returns **`members=[]`**. Wave order is read purely syntactically from the `NN-` filename prefix (`_module_number` / `wave_min`), and `depends_on` is set mechanically to *all roles of the previous wave* (`depends_on=list(prev_roles)`). The per-member objective is just the module file's first heading (`subgoal=_first_heading(text) or role`). The coordination medium it emits is a hard-coded `["blackboard"]` with an `F-MEDIUM-INFERRED` flag.
- **The per-member objective is the agent's own self-description, never a coordinator-derived scope.** For a single agent, `map_agent` (`packages/ohm/src/oraclous_ohm/import_/mapping.py`) sets `subgoal = agent.description.strip() or None`, falling back to the body's first non-empty line (flagged `F-SUBGOAL-FROMBODY`). There is **no derivation of a *scoped* objective from where the member sits in the coordinator's flow** — the agent describes itself; the showrunner's "Draft Chapter 04" framing is lost.
- **That static objective is threaded into the run unchanged.** At runtime `run_team` and `run_team_coordinated` call `build_handoff(by_role[dep], member, payload, objective_slice=member.subgoal or "")` (`orchestrate.py:154`, `:265`), so `HandoffEnvelope.objective_slice` (`packages/ohm/src/oraclous_ohm/envelope.py:28`) is fixed at import time, never derived from the producer's output or the member's flow position.
- **A prose coordinator already exists at *run* time, but it does not help *import* time.** `run_team_coordinated` (`orchestrate.py:228`) routes among **already-declared** members, bounded by a coded `max_rounds` cap (`:255`) and fail-closing on a route to an undeclared member (`raise OHMError(f"coordinator routed to undeclared member {role!r}")`, `:277-279`). That is ADR-035's "choice is prose, mechanics are coded" governing **routing**. It does **not** turn a prose showrunner into the `members[] + depends_on` DAG in the first place — that is import-time work.
- **Skill agents that are *driven programs* have no staging.** `build_subharness` (`mapping.py:99`) emits `OHMRuntime(entrypoint="primary")` over an inline prompt — fine for a reasoning agent, but the book's `reader-panel` is a real Python package (`book/reader-panel/`, `pyproject.toml` + `uv.lock` + a `reader_panel` CLI) whose own `SKILL.md` says *"it shells out to the CLI and relays the report"* and needs a one-time `cd reader-panel && uv venv --python 3.12 && uv pip install -e .` plus `export ANTHROPIC_API_KEY=…`. There is no OHM field that captures *how to stage and drive a skill that is a program*, so such a member imports as a prompt-only agent that cannot actually run.

This ADR closes the ADR-034 §6 prose gap. It is the **import-time DAG derivation for a prose coordinator** — the part of #407 that the structured `eurail-report` wave adapter (ADR-034 §5, already shipped for `modules/<wave>/`) did not cover.

## Decision

**A two-tier prose-showrunner import adapter — deterministic-first, bounded-LLM-fallback, and it surfaces flags rather than committing silently.** When the importer detects a *prose-coordinator* skill (a coordinator/orchestrator `ResolvedSkill` with no `modules/<wave>/` layout), it derives (a) the dependency DAG (`depends_on`, producer→consumer ordering), (b) a per-invocation **scoped `objective_slice`**, and (c) **skill-driver staging** for members that are driven programs — all lowering into the existing OHM v1.1 schema and the ADR-035 runtime. This changes only `packages/ohm/.../import_/orchestrator.py` + the subgoal derivation in `mapping.py` + one new OHM staging field; **the runtime (`run_team` / `run_team_coordinated`) is untouched.**

### 1. Detect a prose-coordinator skill (replace the fail-closed floor)

`adapt_orchestrator_skill` keeps the structured `modules/<wave>/*.md` path it has today (preferred when present — deterministic, cheap, inspectable). When that layout is **absent**, it no longer returns `members=[]` with a `blocking` `F-ORCH-UNSTRUCTURED`. Instead it routes the skill body into the **prose-pipeline parser** (decision 2). `F-ORCH-UNSTRUCTURED` is **demoted from `blocking` to a `confirm`-severity `F-PROSE-PIPELINE` flag** when Tier-1 extracts an orderable structure; it stays `blocking` only when **even Tier 1 finds no orderable structure** (no numbered steps, no producer arrows, no gate markers) — the fail-closed floor is preserved exactly where there is genuinely nothing to order.

### 2. Tier 1 — deterministic prose-pipeline extraction (no LLM)

A `book-studio`-style pipeline is *semi-structured prose* with strong syntactic anchors. Tier 1 parses the coordinator's pipeline block the way the structured adapter parses a wave directory — but over the prose, deterministically:

| Prose anchor (book-studio `chapter` block) | OHM v1.1 target | Rule |
| --- | --- | --- |
| **Numbered step `N.`** (`1.`→`10.`) | one ordered `OHMMember` per step | Step order is the spine. The role is slugified from the step's named agent (`research-scout`, `narrative-drafter`). |
| **Arrow `→ <artifact>`** (`research-scout → research/raw/ …`) | producer→consumer `depends_on` edge | The artifact a step *produces* is consumed by the next step that references it (or, absent a reference, by the next ordered step). This generalizes ADR-034 §6's `## Handoff: Next agent` named-edge anchor to the showrunner's arrow notation. The named producer is the edge anchor — **never** an inferred semantic ordering. |
| **`∥` parallel marker** (`fact-checker ∥ prose-lint`) | two members in the **same stage**, no edge between them | The prose equivalent of a wave: both `depends_on` the prior step, neither depends on the other. Drives `orchestrate.parallel` (ADR-035 decision 2). |
| **`──▶ GATE A/B/C`** (lines 48/51/55) | a `kind: human` blocking node (no `manifest_ref`) interleaved in order | Exactly ADR-034 §6 / ADR-035 decision 6: the gate becomes a first-class blocking DAG node whose advance is the sole satisfier of its downstream `depends_on`. Realizes the stated-but-unshipped prose branch. |
| **`(optional)` step** (line 48) / **`── BLOCK on CRITICAL`** (line 53) | a conditional edge via `OHMMember.run_if` (`manifest.py:106`) | Mechanics are coded: `run_if` is the declarative skip predicate `run_team` already evaluates (`_eval_run_if`, `orchestrate.py:54`/`:143`). `(optional)` and `BLOCK on CRITICAL` lower to a `run_if` the runtime honors — choice is prose, mechanics are coded. Ambiguous predicates are flagged, not guessed. |

Everything ambiguous becomes an **`ImportFlag`** extending the existing `F-*` vocabulary (`F-PROSE-EDGE-INFERRED`, `F-GATE-FROM-PROSE`, `F-PROSE-COND-INFERRED`), surfaced in the **O8 dry-run** (ADR-034 §7) for human confirmation — **never silently committed**. This is the importer's own flag-not-guess rule (ADR-034 Consequences/Negative): a wrong silent default is worse than a surfaced flag.

### 3. The per-invocation scoped `objective_slice` (the highest-value fix)

The member's objective is **derived from the coordinator's line describing that step**, not from the agent's self-description. In the book pipeline, `4. chapter-architect → outline/chapters/CH-NN.outline.md (carries target_state)` makes the `chapter-architect` member's `subgoal` the *showrunner-scoped* objective ("produce the chapter outline carrying target_state"), parameterized over the run's chapter — so the hand-off says **"Draft Chapter 04"**, not a static blurb.

Concretely:

- The **import-time** change is in the orchestrator adapter and `mapping.py`: when a member is created from a prose-pipeline step, its `subgoal` is set from the **coordinator's step description** (the text after the step's agent name / the arrow target), superseding the `agent.description` default. A member that came from the coordinator carries `F-SUBGOAL-FROM-COORDINATOR` (info) so the dry-run shows the derivation provenance; a member with *no* coordinator line falls back to the existing `agent.description` / first-body-line path (`F-SUBGOAL-FROMBODY`), unchanged.
- The **run-time** path is **unchanged**: `build_handoff(..., objective_slice=member.subgoal or "")` (`orchestrate.py:154`, `:265`) already threads `member.subgoal` into `HandoffEnvelope.objective_slice` (`envelope.py:28`). Because the importer now writes a *derived* per-step objective into `member.subgoal`, the existing threading delivers the scoped slice with **zero runtime change**. The conductor (ADR-043) may further specialize the slice per invocation at route time (decision 6); the importer supplies the static, edited, dry-run-confirmed default.

The derived objective is **subordinate to the `tools[]` ceiling** (ADR-032). A coordinator step description that *implies* a capability the member does not declare (e.g. "publish the chapter") **raises an `F-OBJECTIVE-EXCEEDS-CEILING` (confirm) flag** — it is **never** an auto-grant of a tool. This diverges deliberately from frameworks where a manager's prose can hand a worker any tool: the scoped objective may narrow, never widen, the ceiling.

### 4. Tier 2 — bounded, roster-grounded LLM derivation for unanchored prose (O8-flagged, single pass)

Where Tier 1 cannot anchor an edge — free narrative routing with no numbered step, no producer arrow, no gate marker — the importer falls back to a **single bounded LLM derivation**, borrowing the *shape* of AutoGen Magentic-One's Task-Ledger (prose-in, structured-plan-out) but constrained to Oraclous's invariants:

- The LLM is prompted with **(the coordinator prose + the already-parsed declared member roster)** — the roster is Magentic's "team description" — and must emit a structured plan ledger: `{ ordered_steps, per_step: { member, scoped_objective, depends_on } }`.
- It **may only name declared members** — the same fail-closed guardrail the run-time coordinator already enforces (`orchestrate.py:277-279`); a plan naming an undeclared member is rejected at import, not silently invented.
- It is **bounded**: a single planning pass, no auto-replan at import (unlike Magentic's per-round replanning, which is a *run*-time pattern). It does **not** dispatch any member or fire any side effect.
- Its entire output is **flagged `F-DAG-LLM-DERIVED` (confirm)** and lowered into the **same** `members[] / depends_on / run_if` schema — no new runtime path. The user reviews and edits it in the O8 dry-run before any live run.

Tier 2 is the **residue handler**, not the primary path: Tier 1 runs first and the LLM is reserved for the prose Tier 1 cannot anchor. This is the framework consensus (edge = named producer, LLM only for the unanchored remainder) and it keeps the import deterministic wherever the prose has structure.

### 5. Skill-driver staging (venv / cli / env for driven-program skill agents)

For a member whose source skill is a **driven program** (a CLI it shells out to — `reader-panel`'s `reader_panel` package), the importer captures *how to stage and drive it* in a new optional OHM field on `OHMRuntime`:

```
OHMRuntime {
  entrypoint: str                 # unchanged — the capability binding / actor role
  driver: {                       # NEW, optional — present only for a driven-program skill
    kind:   "cli"                 # the staging shape (cli today; reserved for others)
    setup:  [<command>, …]        # one-time staging (e.g. "uv venv --python 3.12", "uv pip install -e .")
    invoke: <argv template>       # how the runtime drives it per call (the CLI subcommand + args)
    env:    [<required secret-ref>, …]   # named secret REFERENCES the broker resolves (never values)
    workdir: <relative path>      # the package root (reader-panel/)
  } | null
}
```

- The staging is **read off the source skill's `SKILL.md` setup block** (the `cd reader-panel && uv venv … && uv pip install -e .` line, the `export ANTHROPIC_API_KEY=…` line). `env` holds **secret references** the credential broker resolves at run time (ADR-020), **never** literal keys — keys are never copied into a manifest (operator separation, ADR-008). A skill that declares an env secret with no resolvable broker credential is an O8 flag (`F-DRIVER-SECRET-UNRESOLVED`), not a silent failure.
- Staging is **least-privilege and org-scoped**: the driven program inherits the member's `tools[]` ceiling and the team's pooled budget (ADR-031), and runs under the same governance as any other member dispatch. The `driver` block describes *staging*, not new authority.
- When a skill is a driven program but no setup is detectable, the importer emits `F-DRIVER-STAGING-ABSENT` (confirm) — surfaced in the dry-run, never guessed.
- A reasoning-only skill agent (the common case) has `driver: null` and is **unchanged** — `build_subharness` keeps emitting `OHMRuntime(entrypoint="primary")` as today.

### 6. Composition with the conductor (ADR-043) and the EURail structured adapter (#407)

- **With the conductor (ADR-043).** This adapter is **import-time**; the conductor is **run-time**. The importer materializes a static, inspectable, dry-run-confirmed DAG (the Lock's "press GO and it runs reproducibly" posture). On the minimal path that static DAG drives `run_team` directly, no conductor needed. When a team opts into the conductor (`run_team_coordinated` / ADR-043), the conductor routes over the **same** members the importer declared, and may specialize each invocation's `objective_slice` at route time — but it is **mechanically bounded** by the importer's output: it can only route to declared members (`orchestrate.py:277-279`) and only within each member's imported `tools[]` ceiling (ADR-035 decision 5). The importer's derived `subgoal` (decision 3) is the conductor's **default** scope; the conductor narrows, never widens. The `(optional)`/`BLOCK on CRITICAL` conditionals (decision 2) lower to `run_if`, which both `run_team` and the conductor honor.
- **With the EURail structured adapter (#407 / ADR-034 §5).** EURail's `eurail-report` has a `modules/<wave>/` layout (or a hard-coded wave list), so it stays on the **structured** path of `adapt_orchestrator_skill` — Tier 1's prose parser is **only** reached when that layout is absent. The two adapters are mutually exclusive per skill and emit the **same** `members[] + depends_on + fan_out + run_if` schema, so a mixed import (a structured wave skill *and* a prose showrunner in one setup) composes into one Team Harness with consistent edges. The `∥` parallel marker (decision 2) and the wave layout both lower to a same-stage member set driving `orchestrate.parallel` — one fan-in barrier semantics, two front doors.

## Consequences

### Positive

- **The book case imports for the first time.** The `book-studio` `chapter` pipeline — the #440 trigger — goes from `F-ORCH-UNSTRUCTURED` / zero members to a real `members[] + depends_on + kind:human gates + run_if` DAG with coordinator-derived objectives. Lock acceptance item 3 ("DAG derived from source") moves red→green for the prose case, completing the structured-only coverage ADR-034 §5 shipped.
- **ADR-034 §6's stated intent is finally shipped for prose.** The exact sentence ADR-034 §6 wrote ("the showrunner/coordinator-skill routing becomes the `orchestration.style` prose + `depends_on` edges; the gate sequence A–G becomes an ordered chain of `kind: human` blocking nodes") is now implemented, not just aspired.
- **Per-member scope becomes a real objective, not a self-blurb.** "Draft Chapter 04" replaces the static `agent.description`; the existing `objective_slice` threading delivers it with **zero runtime change** — the single highest-value, lowest-risk fix.
- **Driven-program skill agents actually run.** `reader-panel` and its kind import with their staging captured, so a skill that *is* a program is runnable instead of importing as an inert prompt.
- **Deterministic where structure exists, bounded where it does not.** Tier 1 keeps the import cheap, deterministic, and inspectable for the common semi-structured pipeline; Tier 2 is a single bounded, roster-grounded, flagged pass for the residue — no heavyweight prose→DAG planner DSL.
- **Runtime untouched.** Only the importer and one optional OHM field change; `run_team` / `run_team_coordinated` / `HandoffEnvelope` / the dispatch ceiling are unchanged — small PRs, low blast radius.

### Negative

- **Prose extraction is heuristic and adversarial (ADR-034's load-bearing-fidelity risk, extended).** A misread arrow produces a wrong edge; a missed `──▶ GATE` turns a blocking author gate into an agent step (a safety regression). The O8 dry-run + `use-case-guardian` check on every importer change is the mandatory backstop, and the conservative bias holds: when a step is ambiguous between agent and human gate, surface it for confirmation, never default to agent.
- **Tier 2 introduces non-determinism at import (bounded, flagged).** The LLM fallback can produce different plans run-to-run for the same unanchored prose. It is contained to the *residue* Tier 1 can't anchor, is a single bounded pass, names only declared members, and is fully flagged for human edit before any live run — but it is a non-deterministic step in an otherwise deterministic import, and a Tier-2-heavy import is a signal the source prose is under-structured.
- **A new OHM field is a schema surface.** `OHMRuntime.driver` adds a staging concept to the manifest; it must stay optional (reasoning agents unaffected) and must never carry secret *values* — only broker references — or it voids operator separation (ADR-008). The validator must reject a `driver.env` literal.
- **Two derivation tiers + the structured adapter = three front doors to one schema.** A reader must understand which path produced a given member (structured wave / prose Tier 1 / LLM Tier 2). The `F-*` provenance flags on each member mitigate this, but the import report is busier.

## Alternatives considered

### A. Keep the fail-closed floor — leave prose coordinators as `F-ORCH-UNSTRUCTURED`, zero members

Do nothing; require the user to restructure their prose pipeline into a `modules/<wave>/` directory before import. **Rejected** — this is precisely the "but first you must…" the North-Star Lock §0 forbids: it makes the user re-author the working pipeline they already have (book studio's `chapter` block is real, shipped engineering). It fails Lock acceptance item 3 for the entire book case and leaves the #440 trigger unaddressed. The structured layout is a *preferred* input, never a *precondition*.

### B. A single up-front LLM that turns the whole prose into the full DAG in one shot

Skip Tier 1; prompt one LLM to convert the entire showrunner prose into `members[] + depends_on` in a single call (the Semantic-Kernel Handlebars/Stepwise-planner shape). **Rejected** — this is the path Microsoft *deprecated and removed*: a brittle, hallucination-prone one-shot planner over a hand-rolled plan DSL lost to native tool-calling + a bounded dynamic manager. For Oraclous it would discard the deterministic, inspectable extraction available wherever the prose has anchors (numbered steps, arrows, gate markers — which book studio has in abundance), make every import non-deterministic, and put the ceiling-fidelity-critical edge derivation (ADR-032) inside an LLM with no syntactic floor. Deterministic-first with a *bounded residue* fallback (decision 2+4) dominates.

### C. A run-time-only prose coordinator (no import-time DAG at all)

Don't materialize a DAG at import; let the run-time conductor (`run_team_coordinated` / ADR-043) read the prose showrunner live and route every round, Magentic/CrewAI-hierarchical style. **Rejected as the import path** — the Lock requires a *bootstrappable, inspectable, reproducible* team: a from-scratch team must materialize correctly so "press GO and it runs the same way" holds, and the O8 dry-run (ADR-034 §7) must show the parsed DAG *before* any cost-incurring run. A purely dynamic per-round plan has no static artifact to dry-run, edit, sign, or version, and re-derives the routing (and its cost/non-determinism) on every run. The conductor is a valuable *opt-in run-time* layer **over** the materialized DAG (decision 6), not a replacement for materializing it. (This is also why CrewAI's known hierarchical-manager failure mode — inconsistent run-to-run subtask scoping — is one Oraclous avoids by materializing first.)

### D. Borrow CrewAI/LangGraph scope-injection verbatim — let the derived objective grant tools

Adopt the framework convention where the manager's prose scope can effectively hand a worker whatever capability the task implies (CrewAI hierarchical delegation, LangGraph supervisor `task_description`). **Rejected** — it violates ADR-032's capability-absence-as-a-structural-gate invariant: a member's `tools[]` is an immutable ceiling, and a coordinator-derived objective must be *subordinate* to it. Decision 3 keeps the borrowed idea (a freshly-written, per-step scoped objective replaces the self-description) but **inverts the authority**: the derived scope may narrow the member, an objective that implies an undeclared capability is a *flag*, never an auto-grant. Frameworks without a structural ceiling can afford the looser convention; Oraclous cannot.

### E. A standalone prose-parsing service

Stand up a service to parse showrunner prose into a DAG. **Rejected** for the same reason ADR-034 §8/B-bis rejected an import microservice: the parsing/derivation is **pure transformation** that belongs in `packages/ohm` beside the OHM v1.1 schema it emits (keeping mapping and schema in lockstep), and product reachability is already solved by the `core/import-agent-setup` capability (ADR-034 §8). A new service duplicates those seams for no gain and splits the parser from the schema it must track.

## Implementation notes

This is part of R7 epic **E2 (the importer)**, under the parent issue **oraclous-backend #407** (skill-resolution / charter / single-skill-orchestrator adapter), extending the DAG-from-source slice **#408** that shipped the structured wave adapter. It is decomposable as:

- **Tier 1 prose-pipeline parser** in `packages/ohm/src/oraclous_ohm/import_/orchestrator.py`: when `adapt_orchestrator_skill` finds no `modules/<wave>/` layout, parse the coordinator body's numbered/`→`/`∥`/`──▶ GATE`/`(optional)`/`BLOCK` anchors into `members[]` + `depends_on` + `kind:human` nodes + `run_if`; demote `F-ORCH-UNSTRUCTURED` to a `confirm` `F-PROSE-PIPELINE` when an orderable structure is found, keep it `blocking` only when nothing is orderable. New flags `F-PROSE-EDGE-INFERRED`, `F-GATE-FROM-PROSE`, `F-PROSE-COND-INFERRED`.
- **Coordinator-derived `subgoal`** in `mapping.py` / the orchestrator adapter: set `member.subgoal` from the coordinator step description (superseding `agent.description` for coordinator-sourced members); flag `F-SUBGOAL-FROM-COORDINATOR`; raise `F-OBJECTIVE-EXCEEDS-CEILING` when the derived objective implies an undeclared capability. **No runtime change** — `build_handoff(..., objective_slice=member.subgoal or "")` (`orchestrate.py:154`, `:265`) already threads it into `HandoffEnvelope.objective_slice` (`envelope.py:28`).
- **`OHMRuntime.driver`** field (`packages/ohm/src/oraclous_ohm/manifest.py` `OHMRuntime`, currently `entrypoint`-only at `manifest.py:79`): optional staging block (`kind/setup/invoke/env/workdir`); `build_subharness` (`mapping.py:99`) populates it from a driven-program skill's setup block, leaving it `null` for reasoning agents. Validator rejects a literal value in `driver.env` (broker references only — ADR-008/020). New flags `F-DRIVER-SECRET-UNRESOLVED`, `F-DRIVER-STAGING-ABSENT`.
- **Tier 2 bounded LLM fallback**: a single, roster-grounded, declared-members-only planning pass for prose with no Tier-1 anchor; output flagged `F-DAG-LLM-DERIVED` and lowered into the same `members[]/depends_on/run_if` schema. Bounded (one pass, no auto-replan, no dispatch).
- **O8 dry-run surfacing**: every new flag renders in the ADR-034 §7 dry-run report (parsed DAG + per-member ceiling + driver staging + which tier produced each member); the import is read-only and free; GO is gated on the user reviewing it.

Validation reuses the shipped v1.1 checks unchanged: `dag.topological_stages` (acyclicity / unknown-`depends_on` / duplicate-role, fail-closed), the `OHMMember` validator (`kind: human ⇒ human_role`), and `_eval_run_if` (`orchestrate.py:54`). The emitted documents are standard OHM v1.1, so they sign/version/govern through the existing ADR-002 path and run on the unchanged ADR-035 runtime.

## References

- The #440 book-GO end-to-end (the trigger) and the example prose showrunner: `book/.claude/skills/book-studio/SKILL.md:43–59` (the `chapter <CH-NN>` numbered pipeline, `∥` line 52, `──▶ GATE A/B/C` lines 48/51/55, `(optional)` 48, `── BLOCK on CRITICAL` 53); the driven-program skill `book/.claude/skills/reader-panel/SKILL.md` (`cd reader-panel && uv venv … && uv pip install -e .`, `export ANTHROPIC_API_KEY`, "shells out to the CLI") + the package `book/reader-panel/` (`pyproject.toml`, `reader_panel` CLI).
- [ADR-034 — Adoption-First Import](adr-034-adoption-first-import.md) — §6 DAG-from-source (the stated-but-unshipped prose-showrunner branch this ADR ships), §5 the structured wave adapter (the complementary path), §7 the O8 dry-run, §8 the importer's `packages/ohm` + `core` capability residency, the flag-not-guess rule.
- [ADR-035 — Coordination Control & Media](adr-035-coordination-control-and-media.md) — the runtime this derived DAG runs on, unchanged: `run_team` / `run_team_coordinated`, the `HandoffEnvelope`, the dispatch-time `assert_capability_allowed`, the blocking-gate-node, "choice is prose, mechanics are coded".
- [ADR-031 — OHM v1.1 Team Manifest](adr-031-ohm-v1.1-team-manifest.md) — the `members[] / depends_on / fan_out / subgoal / orchestration / pooled budget` schema this adapter emits into; the one-budget-surface invariant the staged driver inherits.
- [ADR-032 — Capability-Absence as a Structural Gate](adr-032-capability-absence-structural-gate.md) — the immutable `tools[]` ceiling the derived `objective_slice` is subordinate to (the `F-OBJECTIVE-EXCEEDS-CEILING` flag, never an auto-grant).
- [ADR-043 — the conductor (#553)](adr-043-conductor.md) — the opt-in run-time routing layer this import-time DAG composes with (decision 6): the conductor routes over the declared members and may specialize `objective_slice` per invocation, bounded by the importer's ceiling/declared-member output.
- [ADR-008 — Cloud-Hosted Mode with Equivalent Data Sovereignty](adr-008-cloud-hosted-mode-with-equivalent-data-sovereignty.md) / [ADR-020 — Per-Org Envelope Encryption](adr-020-per-org-envelope-encryption-kms-held-kek.md) — the `driver.env` secret-reference rule (broker-resolved at run time, never a literal in the manifest).
- [Team-of-Agents — North-Star Lock](../product/team-of-agents-north-star-lock.md) — §6 acceptance item 3 (DAG derived from source) this ADR turns green for the prose case; the `use-case-guardian` enforcement basis.
- Shipped code anchors (read in this repo): `packages/ohm/src/oraclous_ohm/import_/orchestrator.py` (`adapt_orchestrator_skill`, `F-ORCH-UNSTRUCTURED` blocking + `members=[]` on prose, `_first_heading` subgoal, `depends_on=list(prev_roles)`, `["blackboard"]` medium); `packages/ohm/src/oraclous_ohm/import_/mapping.py:99` (`build_subharness` → `OHMRuntime(entrypoint="primary")`), `:167-171` (`subgoal = agent.description …` / `F-SUBGOAL-FROMBODY`); `packages/ohm/src/oraclous_ohm/orchestrate.py:54,143` (`_eval_run_if` / `run_if`), `:154,265` (`build_handoff(..., objective_slice=member.subgoal or "")`), `:228,255,277-279` (`run_team_coordinated`, `max_rounds` cap, undeclared-member fail-close); `packages/ohm/src/oraclous_ohm/envelope.py:28` (`HandoffEnvelope.objective_slice`); `packages/ohm/src/oraclous_ohm/manifest.py:79` (`OHMRuntime`), `:106` (`OHMRunIf`), `:207` (`OHMOrchestration`); `packages/ohm/src/oraclous_ohm/dag.py` (`topological_stages`).
- [ADR index](index.md)

## Revision history

| Date | Change |
| --- | --- |
| 2026-06-27 | Initial draft (Proposed). Decides the prose-showrunner → DAG import adapter extending ADR-034: (1) detect a prose-coordinator skill, demoting `F-ORCH-UNSTRUCTURED` from blocking to a confirm flag when an orderable structure exists; (2) Tier-1 deterministic prose-pipeline extraction (numbered steps → ordered members, `→` arrows → producer→consumer `depends_on`, `∥` → same-stage parallel, `──▶ GATE` → `kind:human` blocking nodes, `(optional)`/`BLOCK` → `run_if`); (3) coordinator-derived per-invocation `objective_slice` superseding the self-description, threaded by the existing `build_handoff` with zero runtime change, subordinate to the ADR-032 ceiling; (4) Tier-2 bounded, roster-grounded, declared-members-only single-pass LLM fallback for unanchored prose, fully O8-flagged; (5) skill-driver staging via a new optional `OHMRuntime.driver` block (setup/invoke/env-as-broker-refs/workdir) for driven-program skills like `reader-panel`; (6) composition with the ADR-043 conductor (import-time DAG vs run-time routing) and the #407 EURail structured adapter (mutually-exclusive front doors, same schema). Changes only `import_/orchestrator.py` + `mapping.py` + one optional OHM field; the runtime is untouched. R7 epic E2, parent issue #407 (extends #408). Triggered by the #440 book-GO e2e. Pending Reza/CTO. |
