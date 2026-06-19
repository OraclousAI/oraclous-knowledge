---
title: "ADR-034 — Adoption-First: import an existing agent setup to a runnable OHM v1.1 Team Harness without re-authoring"
---

# ADR-034 — Adoption-First: import an existing agent setup to a runnable OHM v1.1 Team Harness without re-authoring

## Status

| Field | Value |
| --- | --- |
| Status | Accepted |
| Date | 2026-06-20 |
| Approved by | Reza Jahankohan |
| Supersedes | None |
| Superseded by | None |
| Driving artifact | [Team-of-Agents — North-Star Lock & Acceptance Test](../product/team-of-agents-north-star-lock.md) — §2 **R1** (Import, don't re-author) + **R4** (import-driven assembly), §6 acceptance items 1 / 2 / 3 + O8, §7 delta **A-NEW-1**, §8 ADR list **#1 ("the keystone — highest priority")** |

## Context

The North-Star Lock states the **one requirement** in §0: *"Bring the team you already have, press GO, and it runs — no re-authoring, no 'but first you must…', no extra requirements."* The three north-star use cases are the acceptance test, not examples — and **all three already exist** as Claude Code agent setups: a 14→3→4→2 single-skill orchestrator (EURail), 17 `.claude/agents` across standing teams + ~30 skills (bitcoin-gpt / doefin-gpt), and 31 `.claude/agents` + 7 coordinator skills + 6 team charters + 7 author gates (book studio).

§1 of the Lock is unambiguous about why every prior iteration failed: each treated the import as a footnote — *"the prompts port almost verbatim," "register it as a tool," "the bible becomes the blackboard"* — and **every one of those phrases hides days-to-weeks of the user's real, working engineering.** The wall is not the runtime that runs a team; it is **getting the team you already have into the product**. Lock acceptance item 1 makes the wall falsifiable: an existing `.claude/agents/` directory (or a single skill-orchestrator) must import to a runnable Team Harness with **zero manual OHM authoring** (17/30/23-artifact teams included), item 2 requires `skills:` references to be auto-resolved and inlined (no skill re-authored by hand), and item 3 requires the inter-member DAG (`depends_on`, conditional dispatch, schedules) to be **derived from the source**.

[ADR-031](adr-031-ohm-v1.1-team-manifest.md) decided the **target schema** — the OHM v1.1 Team Harness (`metadata.kind: team`, `members[]` with `manifest_ref`/`tools`/`subgoal`/`depends_on`/`fan_out`/`outputs_schema`, `orchestration`, `task_board`, pooled `budget`, `precedence`, `schemas`) — and explicitly held the *importer that populates it* **out of scope**, deferring it to "a separate ADR" and warning (its Consequences, Negative) that *"until that importer lands, the only ergonomic way to produce a Team Harness is absent."* [ADR-032](adr-032-capability-absence-structural-gate.md) decided that a member's imported `tools[]` set is an **authoritative capability ceiling** enforced at the dispatch seam, and noted (its Negative consequences) that *"import fidelity becomes load-bearing… an importer bug that widens the set silently weakens the gate."* This ADR closes both gaps: it decides the **importer** — the first-class product capability that reads an existing agent setup and emits the ADR-031 Team Harness, populates the ADR-032 ceiling faithfully, and derives the DAG from the source (Lock R4).

The team-of-agents capability design names this **A-NEW-1 (the Importer)** and ranks it *"the top-priority deliverable; if step one fails, nothing else matters."* This ADR is the keystone of the Lock's §8 ADR list. The non-negotiable framing carried from the Lock §2 correction (adversary #7): **the user brings agent *definitions*; the platform is the runtime.** A user's partially-built harness (bitcoin's AgentSpec parser, tool-group YAML, Postgres schema, Modal target) is *not* reused as a runtime — the importer lifts the *definitions*, the platform supplies execution. "Bring my harness" never implies runtime reuse.

The real source formats the importer must read (grounded, not invented):

- **`.claude/agents/*.md`** — YAML frontmatter (`name`, `description`, `model`, `tools` as a list or comma string, optional `skills` list) + a markdown body that is the agent's system prompt (mission, write-scope, process, guardrails). Real examples: `book/.claude/agents/diagram-generator.md` (`tools: Read, Grep, Glob, Write`, `model: sonnet`, body with explicit *"No publish/upload/send tools"* guardrail) and `bitcoin-gpt/.claude/agents/intelligence-publisher.md` (`model: opus`, `tools:` list, `skills:` list of five named skills, body with a `## Handoff` convention naming the **next agent + next task**).
- **`.claude/skills/<name>/`** — a coordinator skill (SKILL.md + module-prompt files + schemas), named in an agent's `skills:` frontmatter, to be **resolved and inlined**.
- **`teams/<n>/charter.md`** — team metadata: a roster table (Agent | Type | Model | Verdict | Job), owns/writes scope, and `## Hard gates` (book Gate D / Gate E) + `## Handoff`.
- **A single skill-as-orchestrator** — EURail's `eurail-report` SKILL.md: a hardcoded wave pipeline (`Wave 1 — 14 research subagents → Wave 3 — 3 analysis → Wave 4 — 4 synthesis → Wave 5 — 2 quality gates`), each wave fan-out-then-barrier, plus a `--refresh-from` seeded-refresh mode.
- **A schedule manifest** — bitcoin's `harness/config/cron.yaml`: `{ id, cron, agent, entrypoint, prompt, expected_artifact }` per job (e.g. `morning_brief: "0 7 * * *"` → `analyst`), and the `## Handoff` `Next agent` convention as the inter-member edge source.

## Decision

**Import is a first-class product capability — a tool/command the product runs, never hand-authoring.** "Port almost verbatim" is the product's job. The import path produces a runnable OHM v1.1 Team Harness (ADR-031) and its member sub-harnesses with **zero manual OHM authoring**; the user edits the result, but never starts from a blank manifest.

### 1. Import is a product action, not a migration script (zero manual OHM authoring)

The importer is invoked as a **product command** — `oraclous import <path>` and the equivalent product/gateway action — pointed at an existing setup directory (a `.claude/` tree, a `teams/` tree, or a single skill-orchestrator path). It **emits** OHM v1.1: it parses every source artifact, maps it to the ADR-031 schema, derives the DAG, resolves and inlines skills, and writes a Team Harness + one sub-harness per member. No step requires the user to write OHM. The output is a set of OHM documents the user can inspect, dry-run (O8), edit, and run. This is the realization of Lock acceptance item 1.

### 2. The frontmatter → OHM v1.1 member mapping (field by field)

A `.claude/agents/<name>.md` agent becomes one OHM v1.1 **Role-Agent** — an `OHMMember` (ADR-031) whose `manifest_ref` points at a generated sub-harness OHM. The mapping is exact:

| Source (`.claude/agents/*.md`) | OHM v1.1 target | Rule |
| --- | --- | --- |
| frontmatter `name` | `member.role` | The agent name (slugified, unique within the team) is the member's addressable role — the identity used by `depends_on`, hand-offs, and board assignment. |
| frontmatter `model` (`opus` / `sonnet` / `haiku`) | the generated sub-harness's `models[]` binding (`role: primary`) **and** the member's model tier | The shorthand tier resolves to a concrete `<provider>/<model-id>` binding in the sub-harness `models[]`; the tier is also surfaced for the O2/§14 cost pre-flight (cheaper default for routine scheduled scans). |
| frontmatter `tools` (list or comma string) | `member.tools` — **the capability CEILING (ADR-032)** | Parsed to a normalized list and written as the member's `tools[]`. This is the *structural gate*: the union of these tool ids is the complete, closed set the member may ever dispatch. The importer **never widens** it; absence of `publish`/`upload`/`send`/`spend` is the mechanism (diagram-generator's `Read,Grep,Glob,Write` ⇒ structurally cannot ship). Import fidelity here is load-bearing (ADR-032). |
| frontmatter `skills` (list) | resolved + **inlined** into the sub-harness `prompts[]` / capabilities | Each named skill is resolved from `.claude/skills/<name>/` and inlined (§3); no skill is re-authored by hand (Lock item 2). |
| frontmatter `description` + markdown **body** | the sub-harness **system prompt** (`prompts[]`, `role: primary`, `source: inline`) + `member.subgoal` | The body (mission, write-scope, process, guardrails) becomes the sub-harness's inline system prompt verbatim; `description` (and the body's mission line) distills the `member.subgoal` — the objective slice the evaluator scores the member against. |
| (default) / a human-gate marker in body or charter | `member.kind: agent` / `member.kind: human` (+ `human_role`) | `kind: agent` by default. When the source marks a **human gate** (a charter `## Hard gates` entry like book Gate E "*the author* uploads", or a verdict column reading `human-or-outsource`), the importer emits `kind: human` with `human_role` and **no** `manifest_ref` — a blocking DAG node (ADR-032 §2). |

**`manifest_ref` (generated sub-harness) vs inline.** Each agent member references a **generated sub-harness OHM by `manifest_ref`** (the default), because ADR-031/ADR-032 require the member's capability ceiling and prompt to resolve through a real OHM document (atomic, fail-closed, ADR-002) — a `manifest_ref` makes the sub-harness independently versionable, signable, editable (O5), and re-usable across teams. The importer generates `org:<id>/<agent-slug>@1` for each agent and writes the body→prompt, tools→ceiling, model→binding into it. An **inline** member form (no `manifest_ref`, prompt/tools carried on the member) is reserved for the degenerate single-context / head-switching case and is not the import default.

### 3. The skill-resolution / inlining adapter

Each skill named in an agent's `skills:` frontmatter is **resolved** from `.claude/skills/<name>/` (SKILL.md + its module-prompt files + schemas) and **inlined** into the generating sub-harness — as additional system-prompt material (the skill's instructions) and, where the skill declares callable sub-capabilities (a tool group, a schema-validated output), as resolved capabilities on the sub-harness. **No skill is re-authored by hand** (Lock item 2). A skill referenced by multiple agents is resolved once and inlined into each referencing sub-harness; a skill that is itself a coordinator/orchestrator (it spawns subagents) is handled by the §5 adapter, not flattened into a single prompt.

### 4. The charter adapter (`teams/<n>/charter.md` → team metadata + member grouping)

A `teams/<n>/charter.md` is read for: (a) the **roster table** (Agent | Type | Model | Verdict | Job) → the set of members in that team group and their model tiers/verdicts (the verdict column distinguishes `AI` agents from `human-or-outsource` human gates); (b) **owns/writes** scope → the member sub-harnesses' write-scope and the team's `precedence`/substrate fidelity (book's file-native `production/`, `bible/`, `rules/`); (c) **`## Hard gates`** → `kind: human` blocking nodes (Gate D = a barrier before production; Gate E = the author's upload gate, never an agent capability); (d) **`## Handoff`** → an inter-team edge (the producing team's output feeds the next team — the DAG edge source for multi-team setups). Multiple charters compose into one Team Harness whose `members[]` span the teams, with cross-team `depends_on` edges from the handoff lines.

### 5. The single-skill-orchestrator adapter

A lone skill that spawns subagents via the Task tool (EURail's `eurail-report`: a wave pipeline 14 research → 3 analysis → 4 synthesis → 2 QA) maps to an `orchestration` block + a `members[]` list carrying the fan-out/fan-in **topology**:

- Each **wave** becomes a dependency stage: the members of wave *N* carry `depends_on: [<members of wave N-1>]` — a fan-in barrier (ADR-031 `execution_stages()` topological stages).
- A wave that runs *M* parallel instances of one role over a list (the 14 research subagents over 14 modules) becomes a member with `fan_out: { over: "$.<list>", max_parallel: M }` — one instance per item, barrier at the next stage.
- The skill's module-prompt files become the per-member sub-harness prompts (§2 body→prompt rule); the skill's shared instruction files (EURail's `shared/*` evidence-protocol, source-credibility) inline into every member (§3).
- The orchestrator's prose (the wave description, the success/quality criteria) populates `orchestration.style` + `orchestration.success_criteria`; the skill's seeded-refresh mode (`--refresh-from`) maps to the seeded-refresh lifecycle, not the importer (out of scope here — separate lifecycle ADR).
- The skill's deterministic Python spine (EURail's `merge_delta.py` merge/dedupe) is adopted as a **library-as-tool-group** verifiable function (the tool/data-adoption ADR), referenced as an aggregation member — not re-authored as prose.

### 6. DAG-from-source (Lock R4 — `depends_on` + conditional dispatch + schedules derived, never hand-wired)

The importer **derives** the inter-member/inter-team DAG from the source's own structure — the user edits, never starts from a blank manifest:

- **Skill-orchestrator spawn graph** (EURail) → wave-ordered `depends_on` stages + `fan_out` (§5).
- **`## Handoff` convention** (bitcoin's `Next agent` / `Next task`; book charters' `## Handoff`) → a directed `depends_on` edge from the named-next member to the producer; the `Next task` prose seeds the consumer's `subgoal` / hand-off envelope.
- **`cron.yaml`** (bitcoin) → per-job **schedules** on the corresponding members (`morning_brief "0 7 * * *"` → `analyst`), feeding the standing-team lifecycle; `expected_artifact` seeds the member's `outputs_schema` intent.
- **Showrunner routing + the 7-gate sequence** (book) → the gate sequence A–G becomes an ordered chain of `kind: human` blocking nodes interleaved with the agent members (ADR-032 §2), and the showrunner/coordinator-skill routing becomes the `orchestration.style` prose + `depends_on` edges.
- **Conditional dispatch** (a charter's verdict-conditional routing, an orchestrator's `--quick` skip-a-wave branch) → conditional edges expressed in `orchestration` for the coordinator to reason over (choice is prose; mechanics are coded).

### 7. The import dry-run (O8) — a pre-GO validation report

Before any cost-incurring or side-effecting run, the importer emits a **dry-run report** (Lock O8, acceptance check: "a 30-agent import yields a validation report before any live run"): the **parsed team** (every member, its kind, its resolved model tier), the **generated DAG** (stages, fan-out widths, schedules, human blocking nodes), and **which tools/skills resolved vs. failed** — each member's resolved **capability ceiling** surfaced for confirmation (ADR-032's required dry-run surfacing, so an importer widening bug is caught before it weakens the gate), and each unresolved skill / unmapped tool flagged. The dry-run is **read-only and free**: no member dispatches, no schedule arms, no side effect fires. GO is gated on the user reviewing it.

### 8. Where the importer lives

**The importer is a library in `packages/ohm` (`oraclous_ohm.import_`), wrapped by a thin product action.** Rationale:

- It **emits OHM v1.1**, so it depends on `packages/ohm` (the schema, the `OHMManifest`/`OHMMember` types, the DAG topological-stage resolver, the validators). Co-locating the emitter with the schema keeps the mapping and the schema in lockstep — the same place ADR-031 put the v1.1 types and ADR-032's ceiling field. It is **pure** (filesystem-in, OHM-documents-out): no DB, no org-context, no side effects — exactly a `packages/` shared-library shape, consumable by any service.
- It must be **reachable as a product action**, so a thin, stateful caller wraps the library where product invocation lives: a **capability in the `capability-registry`** (`core/import-agent-setup`) is the canonical product surface — registering the importer as a `core` capability makes it dispatchable from the runtime and, post-R6, from the gateway, with the import *run itself* governed (org-scoped persistence of the emitted sub-harnesses, dry-run provenance). The library does the parsing/mapping/emission; the capability does org-scoped persistence and product reachability.

A standalone import *service* is rejected (§ Alternatives B-bis below): the heavy lifting is pure transformation that belongs beside the schema, and a new service would duplicate the registry's existing capability-dispatch and persistence seams for no gain.

## Alternatives considered

### A. Ask users to hand-author the OHM Team Harness (with docs/templates)

Ship the ADR-031 schema + a good template and let users write the Team Harness themselves. **Rejected** — this is precisely the failure the Lock §0/§1 forbids: *"port almost verbatim" is a tool the product runs, never hand-work.* ADR-031 itself flags (Consequences, Negative) that hand-authoring a Team Harness — a DAG, sub-goals, schemas, a pooled budget, per-member ceilings — is *demanding* and only acceptable *because the importer is the intended populator*. A 31-agent book team or a 14-way EURail swarm is days of error-prone OHM transcription that re-creates the user's existing engineering by hand and discards the zero-manual-authoring guarantee (acceptance item 1). It also makes ADR-032's ceiling fidelity a hand-transcription risk on every member.

### B. A one-off migration script (run once, throw away)

Write a throwaway script that converts one user's `.claude/` tree, not a first-class product capability. **Rejected** — the Lock makes import a **recurring, first-class** capability (every new customer brings a team; O5 requires re-import-merge when the upstream dir changes; O8 requires a dry-run on every import). A one-off script has no dry-run, no ceiling-surfacing, no re-import-merge semantics, no product reachability, and no governance — it cannot satisfy acceptance items 1/2/3/O8 or the edit-a-running-team loop. Import is product, not a one-time chore.

### B-bis. A standalone import microservice

Stand up a new `import-service` under `services/`. **Rejected** — the mapping/emission is **pure transformation** that belongs in `packages/ohm` beside the schema it emits (keeping mapping and schema in lockstep), and product reachability is already solved by registering a `core` capability in the existing capability-registry (dispatch + org-scoped persistence seams already exist). A new service duplicates those seams, adds a deployment/ownership surface, and splits the importer from the schema it must track — net cost, no benefit.

### C. A visual / drag-and-drop team-builder editor

Provide a GUI where the user assembles members, edges, and ceilings visually instead of importing. **Rejected as the import path** — it is still **re-authoring**, just with a mouse: the user re-specifies a team they already have working in `.claude/`. The Lock requires *adoption* of the existing setup, not re-construction in a new tool. A visual editor is a reasonable *post-import edit* surface (O5, editing the imported result) but must never be the front door; the front door is `import <path>` → runnable.

### D. Adopt the user's partially-built harness as the runtime (reuse their engine)

For users who shipped a half-built harness (bitcoin's AgentSpec parser, tool-group YAML, Modal target), reuse *their* runtime rather than importing definitions into ours. **Rejected** — the Lock §2 adversary-#7 correction resolves this explicitly: *the user brings agent **definitions**; the platform is the runtime.* Reusing a user's partial harness as the execution engine forks the runtime per customer, voids the single governance/budget/provenance surface (ADR-031 keystone), and re-imports every gap the platform exists to fill. The importer lifts the **definitions**; the platform supplies execution.

## Consequences

### Positive

- **Step one stops failing.** The Lock's #1 wall — getting the team you already have *into* the product — is now a one-command product action. Acceptance items 1 (zero-manual-authoring import), 2 (skills resolved + inlined), and 3 (DAG derived from source) move from red to green for all three north-star cases, and O8 (dry-run) lands with them.
- **ADR-031's "absent ergonomic path" is filled.** The importer is the intended Team-Harness populator ADR-031 deferred; hand-authoring stays the exception, not the path.
- **ADR-032's ceiling becomes trustworthy.** The `tools:` → `member.tools` mapping populates the authoritative ceiling faithfully, and the O8 dry-run surfaces each member's resolved ceiling for confirmation — closing the "importer widening bug silently weakens the gate" risk ADR-032 named.
- **The user's engineering is adopted, not rebuilt.** Bodies → prompts verbatim, skills inlined, charters → groups, the spawn-graph/handoff/cron → the DAG. The user keeps the team they built; the product runs it.
- **Clean residency.** A pure `packages/ohm` library (schema-adjacent, side-effect-free) wrapped by a `core` registry capability (product-reachable, governed) — no new service, no schema drift.

### Negative

- **Import fidelity is load-bearing and adversarial.** Every mapping rule is a place a bug can silently corrupt the result — a widened ceiling weakens ADR-032; a missed human-gate marker turns a blocking author gate into an agent member; a misread `## Handoff` produces a wrong edge. The dry-run (O8) is the mandatory backstop, and the `use-case-guardian` must check imported teams against acceptance items 1–4 on every importer change.
- **Source formats are heterogeneous and will drift.** `.claude/agents` frontmatter is loosely specified (tools as a list *or* a comma string; skills optional; human gates marked in prose/charter, not a field). The importer must be tolerant and must **flag-not-guess** ambiguous cases in the dry-run rather than silently picking a default — a wrong silent default is worse than a surfaced flag.
- **Human-gate detection is heuristic.** Deriving `kind: human` from a charter `## Hard gates` line or a `human-or-outsource` verdict is inference; a missed gate is a safety regression (an agent crosses a step the author must own). Conservative bias: when a step is ambiguous between agent and human gate, surface it for confirmation rather than defaulting to agent.
- **The library/capability split adds an indirection.** The pure emitter and the governed product action are two pieces; the boundary (parse+map+emit in the library; org-scoped persist + dispatch in the capability) must be kept clean so persistence/governance never leaks into the pure transform.

## Implementation notes

The importer is R7 epic **E2** (oraclous-backend #383 / #404), decomposed into child issues:

- **#405** — `packages/ohm` importer library skeleton (`oraclous_ohm.import_`): source-tree discovery + frontmatter/body parser for `.claude/agents/*.md` (tolerant `tools` list-or-string, optional `skills`).
- **#406** — the frontmatter → OHM v1.1 member mapping (§2): `name`→role, `model`→tier/binding, `tools`→ceiling, `description`/body→sub-harness prompt + `subgoal`; generated `manifest_ref` sub-harness emission; human-gate detection → `kind: human`.
- **#407** — the skill-resolution/inlining adapter (§3) + the charter adapter (§4).
- **#408** — the single-skill-orchestrator adapter (§5) + DAG-from-source (§6): wave→stages/`fan_out`, `## Handoff`→edges, `cron.yaml`→schedules, the 7-gate sequence→human blocking chain.
- **#409** — the import dry-run report (§7, O8): parsed team + generated DAG + tools/skills resolved-vs-failed + per-member ceiling surfacing; the `core/import-agent-setup` capability-registry wrapper (§8) with org-scoped persistence.

Validation reuses the shipped v1.1 checks: `oraclous_ohm.parse.load_ohm` (version gate, team-entrypoint cross-check, and member-DAG validation via `topological_stages` — acyclicity, unknown-depends_on, duplicate-role, fail-closed) and the `OHMMember` model validator (`kind: human ⇒ human_role`). `manifest_ref` / schema-`$ref` resolution is the existing reference-resolution path (a later slice). The emitted documents are standard OHM v1.1, so they sign/version/govern through the existing ADR-002 path. The seeded-refresh lifecycle (EURail `--refresh-from`), the batteries-included web-research battery (without which EURail's live-web researchers are inert), and the tool/data-adoption primitives (library-as-tool-group for EURail's merge spine and bitcoin's loaders) are **separate ADRs** (Lock §8 #3/#5/#7); this ADR decides only the **import front door** and the mapping it emits.

## References

- [Team-of-Agents — North-Star Lock & Acceptance Test](../product/team-of-agents-north-star-lock.md) — the driving artifact: §0 the one requirement, §1 why prior iterations failed, §2 R1/R4 + capability-absence framing + adversary-#7 ("definitions, not runtime"), §6 acceptance items 1/2/3 + O8, §7 delta A-NEW-1, §8 ADR list #1 (the keystone)
- [Team-of-Agents Capability Design](../../oraclous-backend/docs/team-of-agents-capability-design.md) — §5/§7 A-NEW-1 (the Importer), the frontmatter→member mapping deltas, the skill-orchestrator + charter adapters
- [ADR-031 — OHM v1.1 Team Manifest (Team Harness)](adr-031-ohm-v1.1-team-manifest.md) — the **target schema** this importer emits (`members[]`, `manifest_ref`, `tools` ceiling, `orchestration`, `depends_on`, `fan_out`, `task_board`, pooled `budget`, `precedence`, `schemas`); ADR-031 deferred *this* importer as "a separate ADR"
- [ADR-032 — Capability-Absence as a Structural Gate](adr-032-capability-absence-structural-gate.md) — the `tools:`→ceiling fidelity this importer must preserve; the human blocking-gate-node it emits; the O8 ceiling-surfacing it must provide
- [ADR-002 — OHM as Canonical Manifest Format](adr-002-ohm-as-canonical-manifest-format.md) — the resolution/signing/versioning semantics the emitted sub-harnesses and Team Harness obey
- Use-case sources (read, not invented): `book/.claude/agents/diagram-generator.md` (`tools: Read,Grep,Glob,Write` ⇒ structural no-publish), `bitcoin-gpt/.claude/agents/intelligence-publisher.md` (`model`, `tools`, `skills`, `## Handoff` `Next agent`), `book/teams/<n>/charter.md` (roster + `## Hard gates` Gate D/E + `## Handoff`), `eurail-report` SKILL.md (14→3→4→2 wave fan-out/fan-in orchestrator + `--refresh-from`), `bitcoin-gpt/harness/config/cron.yaml` (`{id, cron, agent, entrypoint, expected_artifact}` schedules)
- [ADR index](index.md)

## Revision history

| Date | Change |
| --- | --- |
| 2026-06-20 | Initial draft (Proposed). Decides Adoption-First import as a first-class product capability emitting OHM v1.1 (ADR-031): the field-by-field frontmatter→member mapping (`name`→role, `model`→tier, `tools`→ceiling per ADR-032, `skills`→inlined, body→sub-harness prompt+`subgoal`, human-gate→`kind: human`), generated `manifest_ref` sub-harnesses, the skill-inlining / charter / single-skill-orchestrator adapters, DAG-from-source (spawn-graph / `## Handoff` / `cron.yaml` / 7-gate sequence), the O8 dry-run, and the importer's residency (a `packages/ohm` library wrapped by a `core/import-agent-setup` capability-registry capability — no standalone service). R7 epic E2, child issues #405–#409. |
