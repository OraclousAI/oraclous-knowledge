---
title: "Journey spec v2 — the Team-of-Agents console (two on-ramps, one validator, GO)"
owner: experience-architect
status: signed
signed-by: experience-architect
date: 2026-07-03
grounds-in: >
  capability-surface-inventory.md §7 (teams/runs/schedules/artifacts — the 2026-07-03 refresh) ·
  team-of-agents-north-star-lock.md (authoritative; §0 two on-ramps, §3 O1–O8, §6 acceptance) ·
  ADR-047 (compiler on-ramp) · ADR-034/045 (import) · ADR-046 (gates) · ADR-042 (member status / rerun) ·
  the live gateway route table (verified against code 2026-07-03)
supersedes: >
  This spec is the new center of the FE roadmap. The June-18 journey set (tools.md, connections.md,
  recipes.md, navigation-ia.md, agents-harness.md) remains valid for its surfaces but is DEMOTED to
  supporting-surface status; where this spec and those diverge, this spec wins.
  It also supersedes oraclous-frontend/docs/handoff/frontend-catchup-roadmap.md as the product frame —
  that document builds the pre-team product and must not drive any new surface.
legacy-divergence: >
  The console as-built implements the previous product (graph-RAG workspaces + a single-agent OHM
  builder + chat). It has ZERO team concept: no import, no compiler, no team manifest, no run tree,
  no evaluation, no cost pre-flight (FE audit 2026-07-03: 0 hits for team/compiler/ImportReport/eval).
  This spec re-centers the console on the locked product. The graph surfaces survive as the team's
  knowledge substrate; the single-agent builder survives as a Library surface.
backend-gaps: >
  Reconciled against ADRs + the issue board 2026-07-03 (§8): C-1 re-scoped to on-ramp ergonomics +
  draft persistence + re-import merge (the compiler IS gateway-reachable by ADR-047 design; local
  bundle import is PARKED by the cloud-first decision ADR-040 D7 / #523); C-2 re-scoped to the
  USD-surfacing harness + optional run-level pre-flight (schedule pre-flight is BUILT, #603);
  C-5 unchanged (team-run list, genuinely untracked); C-6 WITHDRAWN as a backend gap —
  deliver-back is BUILT (ADR-041 sink-tool model, #515/#542/#544) and the residue is an FE
  "connect your sinks" story leaning on open #505.
---

# Journey spec v2 — the Team-of-Agents console

**The one requirement (locked):** *get a team that runs — either by DESCRIBING the objective in
English or by BRINGING the team you already have — then press GO and it runs. No re-authoring, no
"but first you must…".* Two co-equal on-ramps, one validator, one runtime
(north-star lock §0). Everything in this spec serves that loop:

```
DESCRIBE (prose objective)  ──┐
                              ├──►  REVIEW & REFINE (one validator: would_block report,
BRING (import what exists)  ──┘      NL refine as typed delta)
                                        │
                                        ▼
                              MAKE RUNNABLE (credentials/BYOM)
                                        │
                                        ▼
                              PRE-FLIGHT & GO (cost pre-flight → run)
                                        │
                                        ▼
                              WATCH (status, member grid, run tree, gates)
                                        │
                                        ▼
                              RESULTS (artifacts, verdicts, delivery) ──► REFINE / SCHEDULE / REFRESH
```

**How the frontend agent uses this document.** Each journey (§5) is a build brief: narrative →
steps→endpoints → surface design → states → increments. Build in the §9 order, one vertical
increment per issue, each testable on the live app through the gateway only (FE invariant §1.1).
Where a step depends on a gap Contract it is marked ⛔C-n and MUST NOT be worked around client-side.

**Scope note (lock R6a/O6).** This console is the **served / multi-tenant** surface. The lock's
single-tenant local GO (zero org/BYOM/gateway setup, item 11) is satisfied by the CLI/local
surface, not here — do not add local-mode UI. The console's O6 obligation is **promotion**: a
team validated locally imports here unchanged (J2), and promotion adds governance only, never
behavior. Plan-approval note: **compile-and-run is the default; a blocking plan-approval hold is
opt-in** (lock §4 / item 15) — landing in J3 review is the natural flow, never a required gate.

**Cloud-first sequencing (ADR-040 Decision 7, accepted 2026-06-24; #523).** The two on-ramps stay
co-equal in the *requirement* (the lock), but delivery is **cloud-first**: the DESCRIBE door leads;
the local-bundle IMPORT door is parked behind the cloud loop ("the first use case should be
cloud-based, no local things; work around local later" — #523). J2 remains the signed design for
that door; its build increments sequence after the Describe door and un-park with #523.

---

## 1. What changed in the backend (why the console is stale)

Since the June-18 spec set, the backend shipped the whole team loop through the gateway
(`:8006`, the only surface):

| New capability (inventory §7) | Endpoint |
| --- | --- |
| Start a team run (GO) | `POST /v1/engine/team-runs` (202) |
| Read a run / light status / run tree | `GET /v1/engine/team-runs/{id}` · `…/status` · `…/tree` |
| Advance a human gate (approve/revise/reject) | `POST /v1/engine/team-runs/{id}/advance` |
| Re-run only failed members | `POST /v1/engine/team-runs/{id}/rerun` |
| Validate a draft team (the shared validator) | `Manifest Validate` capability via `POST /api/v1/instances/{id}/execute` |
| NL refine as a typed structural delta | `Manifest Refine` capability via `POST /api/v1/instances/{id}/execute` |
| Standing teams: schedules + per-period budget | `POST/GET/DELETE /v1/engine/schedules` · `…/fire-now` · `…/runs` · `…/team-runs` |
| Cost pre-flight ("~$X/day at this cadence") | `POST /v1/engine/schedules/preflight` |
| Seeded refresh (re-verify a prior run, what-changed delta) | `seed_from_run_id` on GO → `refresh_delta` on the run |
| Fan-out seeding (user-provided or producer-emitted lists) | `inputs:{…}` on GO + `fan_out.over:"$.key"` |
| Degrade-not-crash (labeled-partial members) + budget halt (COST_BUDGET) | run `member_status` / `partial` / `state` |
| Run artifacts (deliverables, verbatim content) | `GET /v1/artifacts?graph_id=…` · `GET /v1/artifacts/{id}` |
| Batch ingest (folder/repo) | `POST /api/v1/graphs/{id}/batch-ingest` |

On-ramp reachability, reconciled (2026-07-03): the compiler is **gateway-reachable by design** —
it is itself a `kind:team` harness POSTed to `/v1/engine/team-runs` (ADR-047: "no new gateway
routing"), and the validator/refine gates are registry tools. What's genuinely missing is the
**ergonomics**: a discoverable/seeded compiler-team manifest (today only `packages/ohm` can build
it), draft persistence, and re-import merge — the re-scoped **C-1** (§8). Local bundle import is
**parked** by the cloud-first decision (ADR-040 D7 / #523). Everything after assembly is live.

---

## 2. Personas (who walks these journeys)

Grounded in `product/personas/` (still `speculative — pending validation`); this spec adds the
on-ramp distinction the lock makes:

- **The conductor (operator persona, primary).** Owns an outcome and a budget. Two sub-cases,
  one per on-ramp: the **from-scratch conductor** (has an objective in English, nothing to
  import — J1) and the **bringing conductor** (has a working local agent setup — EURail /
  bitcoin-gpt / book studio shapes — J2). After GO both are the same person watching the same run.
- **The org admin / governance owner.** Approves MCP imports, mints integration keys, manages
  members, watches spend (J6/J9 budget surfaces, Admin).
- **The human gate-keeper.** Any member of the run named as a human gate (book studio's author):
  lives in the Approvals inbox (J7).
- **The knowledge steward.** Curates graphs, recipes, ingest (J10 — reshaped, was the Recipes/
  Workspaces persona).

---

## 3. The user-visible object model v2

The IA derives from what the gateway actually models (inventory §7), not the legacy graph-chat:

| Object | What the user does with it | Backing |
| --- | --- | --- |
| **Team** | The center. A roster of members with dependencies, gates, budget, schedules — compiled from prose or imported. Review, refine, run. | OHM v1.1 `kind:team` manifest + `sub_harnesses` (draft persistence ⛔C-1) |
| **Run** | One governed execution of a team. Watch, advance gates, re-run failures, read verdicts. | `/v1/engine/team-runs/*` (+ legacy `/v1/engine/jobs` for single harnesses) |
| **Gate / Approval** | A blocking human decision inside a run. | `paused_at` + `…/advance`; `/v1/harnesses/assignments` |
| **Schedule** | A standing team: cron/event trigger, per-period budget, run history. | `/v1/engine/schedules/*` |
| **Agent** | A single role-agent (sub-harness). Built directly or as a team member. | `kind:harness` capabilities + `/v1/harnesses/*` |
| **Tool / Capability** | What members are allowed to do; instances carry credentials. | `/api/v1/{capabilities,tools,instances}` |
| **Connection (credential)** | BYOM model keys + tool credentials. | `/credentials/*`, `/oauth/*` |
| **Graph (knowledge)** | The team's substrate: sources in, artifacts out, memories, search. | `/api/v1/graphs/*`, `/v1/{search,graph,federated}/*`, `/v1/artifacts` |
| **Artifact** | A deliverable a run produced. | `/v1/artifacts*` |
| **Verdict / Battery** | Evaluation read-side on a run (named batteries run inside the run). | `TeamRunOut.verdict` (+ `/v1/graph/{id}/evaluate` for retrieval QA) |
| **Budget / Spend** | Pre-flight projection, caps, exhaustion behavior, retrospective spend. | `…/schedules/preflight`, manifest `budget`, `GET /v1/harnesses/spend` |

**Legacy divergence:** "Workspace = the product" dies; the graph becomes **the team's knowledge
substrate** (bound at GO via `graph_id`). Chat ("Explore") stays as the serving surface for
published agents, not the home.

**Vocabulary reservations (bind on all UI copy).** **member** = a team member only; the Admin
nav item for org humans becomes **People** (was "Members", redirect per §4). **workspace** = the
user-facing word for a knowledge graph (the container users see); "graph"/`graph_id` stay
technical/internal. **gate** = a human decision point inside a run; the inbox surface is
**Approvals**. Do not introduce synonyms (no "fleet", "crew", "sub-agent" in copy).

---

## 4. Information architecture v2 (nav restructure)

Builds on the shipped grouped nav (nav-IA journey, done). Changes are additive-then-promote so
the app stays navigable at every step:

```
Home                Dashboard (team health, recent runs, spend strip)
Teams        NEW    Team list → Team detail (roster, validation, refine, runs, schedules)
                    └─ New team → two equal doors: "Describe it" | "Import it"
Runs                Org-wide runs (team runs ⛔C-5 + jobs) → Run detail (member grid, tree, verdict)
Approvals    NEW    The gate inbox: paused runs + human-task assignments + admin approvals
Library             Agents · Tools · Recipes        (was "Build")
Knowledge           Workspaces → Workspace detail (ingest doors, documents, artifacts, resolution
                    inbox, memories) · Explore (search · graph map · time travel) · Chat (published agents)
Connections         (unchanged — already first-class)
Serve        NEW    Published agents + integration keys · Webhook triggers + MCP access
                    (promotes the built Developer pages out of Admin — the "agent as a product" story, J11)
Admin               People (was Members) · Usage & spend (was Billing — estimates of the org's own
                    provider costs; usage counts are never rendered as currency, ADR-009) · Settings
```

Rules: **Teams is the first item after Home** — it is the product. "Runs" remains the org-wide
operational view; a team's own runs also list inside its detail. Approvals aggregates every
human-blocking item (run gates J7, harness assignments, MCP tool approve/reject, entity-resolution
candidates) — one inbox, the LangGraph "Agent Inbox" pattern, so a blocked run is never a dead end.
Persona filtering as today (owner/member/standalone). All existing routes keep working (redirects
where relabeled).

---

## 5. The journeys

Legend for step tables: every endpoint is a gateway path; auth = member JWT unless noted;
⛔C-n = blocked on a §8 Contract. Async pattern: **202 + poll for run-producing operations**
(team-runs, advance, rerun, fire-now, ingest) — poll `status` at 2–5s, it is designed to be
light. The registry execute seam (validator/refine), harness execute, and schedule create are
**synchronous 201** with the result inline. No SSE/WebSocket anywhere; chat is synchronous.

---

### J1 — Describe a team (the compile on-ramp)

**Narrative.** The from-scratch conductor types an objective in English — *"Assess Eurail's AI
adoption; every claim cites a source; ≥600 evidence records"* — plus optional inputs, constraints,
success criteria. Oraclous plans the team, surveys what tools exist, drafts the roster, and
validates it. The user never authors OHM. (Lock R0/C1; ADR-047.)

**Preconditions.** Signed in; org selected. No credentials needed *to compile* (validation is
deterministic and keyless); credentials bind later (J4).

**Steps → capabilities.**

| # | Step | Endpoint |
| --- | --- | --- |
| 1 | Enter objective (+ optional inputs/constraints/success criteria) in the "Describe it" door | — (form) |
| 2 | Compile: run the compiler team (planner → capability-surveyor → drafter → reviewer) — the compiler is itself a team harness, `POST /v1/engine/team-runs` (202), no new route (ADR-047) | ⛔C-1(a) for the manifest source: the FE needs a discoverable/seeded compiler-team manifest (today only `packages/ohm build_compiler_team()` constructs it — nothing serves or seeds it) |
| 3 | Show compile progress (the compiler is itself a team run — reuse J6's status component) | `GET /v1/engine/team-runs/{id}/status` |
| 4 | Extract the drafted team (reviewer output carries `{members:[…]}`) into the Team review surface (J3) | `GET /v1/engine/team-runs/{id}` |
| 5 | Validate the draft — the SAME validator as import | `POST /api/v1/instances/{manifest-validate}/execute` (sync 201) → `{id, status:"SUCCESS", output_data:{would_block, blocking[], report}}` — the verdict lives under `output_data` |

**Surface.** One large prose field ("What should this team accomplish?"), three optional
collapsed fields (Inputs · Constraints · Success criteria), a single primary action
**"Draft the team"**. While compiling: a compact plan-progress view — completed stages get a
Lucide `check`, the active stage a Lucide `loader-2` (spinning, reduced-motion-aware), pending
stages stay dimmed (planner → surveyor → drafter → reviewer). On completion, land directly in
J3's roster review — never show raw OHM first.

**States.** *Empty:* the two doors side by side with one example objective each. *Loading:*
compile progress (member-by-member). *Error:* compile-run FAILED → show the failed member +
"Try again" (re-POST); never a stack trace. *Blocked:* validation `would_block=true` → J3's gap
report, with the blocking codes (e.g. `F-CAPABILITY-MISSING`) rendered as human sentences
("No surveyed tool can do live web search. This team cannot run until one exists.") — fail-closed,
**never a hallucinated tool** (lock C2). *Success:* the roster review.

**Benchmark note.** This is Devin's plan-with-confidence + CrewAI Studio's NL-to-crew, minus their
weakness: our plan is *validated against a typed catalog* before the user sees it, and OpenAI's
sunset of canvas-authoring (Agent Builder, deprecated ~8 months after launch) confirms
NL + files — not a canvas — is the durable pair of doors.

**Legacy precursor.** None. This surface has no precedent in the legacy app — do not clone.

---

### J2 — Bring a team (the import on-ramp)

**Narrative.** The bringing conductor has a working `.claude/agents/` directory (or a single
skill-orchestrator like EURail, with charters, skills, crons). Oraclous adopts it **as-is**: zero
re-authoring, DAG derived from the source, tool ceilings preserved. (Lock R1/R4, items 1–4;
ADR-034/045.)

**Preconditions.** Signed in. The user has the setup locally (a directory / archive).

**Steps → capabilities.**

| # | Step | Endpoint |
| --- | --- | --- |
| 1 | Choose the "Import it" door; upload the bundle (zip/tar of `.claude/agents/*`, `.claude/skills/*`, `teams/*/charter.md`) or point at a repo | ⛔ parked — cloud-first decision (ADR-040 D7 / #523); this door builds after the Describe door and un-parks with #523 (`import_setup()` exists library-side) |
| 2 | Render the **ImportReport** — the dry-run the lock demands (O8) before any cost/side-effect | ⛔C-1 returns `ImportReport`: `shape · member_count · human_gate_count · stages[][] · schedules{role:cron} · resolved_skills / unresolved_skills · precedence[] · blocking[] · would_block` + the substrate verdict (file-native / graph) derived from the source |
| 3 | Resolve what blocked: unresolved skills, missing tools (each blocking line links its fix) | J4/J10 surfaces |
| 4 | Accept → land in J3's roster review (same surface as J1 — one validator, one review) | — |
| 5 | **Re-import an updated upstream bundle onto an existing team** → a merge report: upstream changes listed, in-platform edits preserved, conflicts surfaced — never a silent clobber (lock O5) | ⛔C-1(d) |

**Surface — the ImportReport is the hero.** A one-screen verdict, not a log dump:
- Header: team name + shape chip (`agent-team` / `orchestrator`) + the verdict:
  **"Ready to run"** (Lucide `check`, ink — a validated draft is not a live signal; no mint) or
  **"N things block this team"**.
- **Members** (count + list with per-member `tools:` ceiling shown as chips — "what it can do,
  and nothing else"), **human gates** (count, called out — these become J7 approvals),
  **execution stages** (the derived DAG rendered as ordered stage rows — n8n-style clarity without
  a canvas editor), **schedules** (role → cron, "will become a Schedule on GO"),
  **skills** (resolved — Lucide `check` / unresolved — Lucide `x`, with the source path),
  **precedence** (the imported hierarchy-of-truth, displayed verbatim — the product adopts the
  user's truth model, never inverts it), **substrate** (file-native or graph, from the source).
- Blocking list at top when `would_block` — each row: what's missing → which member needs it →
  the action that fixes it.

**States.** *Empty:* drop-zone + "What you can import" (agent directories, skill-orchestrators,
charters, crons). *Loading:* parse progress. *Error:* unparseable bundle → say which file, keep
the rest. *Partial:* report with blocking rows (the normal first-run case). *Success:* "Ready to
run" → review.

**Adoption scope (honesty note, lock R2).** Today's importer covers agents / skills / charters /
crons / gates / precedence. The R2 tool-and-data adoption primitives (script-as-scheduled-
ingestion for stateful loaders, library-as-tool-group) are **not yet importable** — the
ImportReport must grow those sections under C-1, and until then the import-fidelity promise in
copy is scoped to what the importer actually adopts. Never imply loaders/libraries import today.

**Import-fidelity promise (microcopy anchor).** "What comes out runs the same as what went in."
Never imply the user must restructure their setup to import it (lock §1 — the walls the product
exists to remove).

**Legacy precursor.** None (MCP tool import is a different, admin-only supply-chain flow — keep
separate).

---

### J3 — Review & refine the team (one surface for both on-ramps)

**Narrative.** Compiled or imported, the user now sees **the team as a team** — roster, wiring,
gates, budget — verifies it, and refines it in English ("add a fact-checker", "make research
parallel", "the editor is human"). Refines are typed structural deltas that preserve everything
untouched (lock R0e; #595) — never a blank re-draft.

**Steps → capabilities.**

| # | Step | Endpoint |
| --- | --- | --- |
| 1 | Roster view: members, `depends_on` edges as stage rows, per-member model tier + tool chips, gates, budget envelope | rendered from the draft manifest (client state; persistence ⛔C-1) |
| 2 | Validation strip (always current): re-run the validator on every change | `POST /api/v1/instances/{manifest-validate}/execute` (sync 201; verdict under `output_data`) |
| 3 | NL refine: user types an edit → op-drafter turns it into ONE typed op (`add_member` / `set_fan_out` / `change_kind` / `add_depends_on`) → preview the op → apply | op-drafter via `POST /v1/engine/team-runs` (tiny run), apply via `POST /api/v1/instances/{manifest-refine}/execute` (sync 201) → `output_data:{would_block, applied, blocking[], manifest\|null}` |
| 4 | Rejected op (unsurveyed tool): show why, manifest untouched | same — `output_data.applied=false, output_data.manifest=null` |
| 5 | Inspect a member: opens the sub-harness read view (prompt, model, tools ceiling) — reuse the existing agent detail components | draft `sub_harnesses[role]` |

**Surface.** Left: the roster (stage-grouped member cards — role, kind chip `agent`/`human`,
model, tool chips, fan-out badge "×N over $.key"). Right: a refine rail — an input
("Change the team…"), the pending typed op rendered as a readable diff ("**Add member**
`fact-checker` · tools: web.search, web.fetch · after: synthesis"), Apply / Discard. Validation
strip pinned above: a neutral/ink "Valid — ready to run" confirmation (no mint — a valid draft
is not a live signal) or the blocking list. **Show the typed op before applying** — the AgentKit
lesson (typed edges/data contracts) applied to team editing; the user always sees the structural
change, never trusts a silent re-draft. Refine stays reachable from Team detail **after** GO
(lock O5): the edited manifest is what the next (scheduled) run picks up.

**States.** *Loading:* op-drafter running ("Turning your edit into a change…"). *Error:* op-drafter
FAILED → keep the text, offer retry. *Edge:* op valid but makes the DAG cyclic → validator strip
catches it; explain in stage terms. *Empty refine history* is fine — refining is optional; the
primary action stays **"Continue"** → J4/J5.

**DS deltas (reground-ds):** member-card, stage-rail, tool-ceiling chip, op-diff block. File as
one reground-ds delta before build; do not invent inline.

---

### J4 — Make it runnable (credentials & BYOM)

**Narrative.** "Paste your keys once, scoped and reused" (lock O1). The team declares model
bindings and tool needs; the user connects what's missing in one pass — never a per-tool auth
wall mid-run.

**Steps → capabilities.**

| # | Step | Endpoint |
| --- | --- | --- |
| 1 | Readiness panel on the team: every model binding + credential-requiring tool, each with a status (connected — Lucide `check` / needed — Lucide `x`) | derived from draft manifest + `POST /credentials/retrieve/`, `GET /credentials/providers` |
| 2 | Add a model key (OpenRouter etc.) | `POST /credentials/` → `{id}`; bind `config.credential_id` into `manifest.models[]` AND every `sub_harnesses[role].models[]` |
| 3 | Add a tool credential to an instance | `POST /api/v1/instances` → `required_credentials` → `POST /api/v1/instances/{id}/configure-credentials` |
| 4 | OAuth-connect a provider instead of pasting | `POST /oauth/{p}/connect` → `…/connect/complete` (built — Connections journey) |
| 5 | Late failure path: any 409 `CREDENTIALS_REQUIRED` anywhere in the app deep-links here with `needs_credential.{requirement_id, provider}` pre-selected | error envelope (gateway-wide) |

**Surface.** Reuse the built Connections page + `CredentialSlot`; new composition: a **readiness
checklist** on the team ("2 of 3 connections ready"). GO stays disabled with the reason listed —
fail-closed, and *visible* (Nielsen: system status).

**States.** *Loading:* checklist rows resolve individually (skeleton per row). *Error:* a
provider/credential lookup fails → the row shows "Could not check" + retry; GO stays disabled.
*Success/empty:* everything already connected → "3 of 3 connections ready", GO enabled. The
built Connections journey's states govern the underlying page; only the checklist deltas above
are new.

**Legacy precursor.** Connections journey (built, current). This journey only adds the
team-scoped readiness composition.

---

### J5 — Pre-flight & GO

**Narrative.** Before the first token is spent the user sees what the run will cost and what it
will touch — then presses GO. Cost pre-flight before run is **industry whitespace** (no surveyed
product does it: not n8n, Copilot, AgentKit, Lindy, Relevance, Devin) — this screen is a
differentiator; treat it as a first-class moment, not a confirm dialog.

**Steps → capabilities.**

| # | Step | Endpoint |
| --- | --- | --- |
| 1 | Cost pre-flight: `fleet_usd_per_day` + `cadence_fires_per_day` + `per_member[]` (each `priced`, `usd_per_fire`, `usd_per_day`) + `unpriced_members` called out honestly — never a fabricated $0 | `POST /v1/engine/schedules/preflight` (#603, BUILT). ⛔C-2(b) for a run-level (non-scheduled) projection — optional; token caps carry the one-shot case meanwhile |
| 2 | Bind the substrate **the source decided** (lock R5): a file-native team binds `workspace_root` (its git tree, read/written in place; the workspace graph is a derived index) — a graph team picks/creates a workspace, **adopting an existing one rather than forcing a second** (graph-adopt of an external graphify graph is C-1 scope) | `GET/POST /api/v1/graphs` + `workspace_root` on GO |
| 3 | Seed inputs (fan-out `over` lists) when the manifest declares them | `inputs:{…}` on GO (#599) |
| 4 | Optional: seed from a prior run (refresh mode) | `seed_from_run_id` on GO (#602) |
| 5 | Final gate check: validator green + credentials ready + budget envelope shown (`max_tokens_total`, `max_sub_runs`, per-member caps, `on_exhaustion`) | manifest `budget` |
| 6 | **GO** | `POST /v1/engine/team-runs {manifest, sub_harnesses, gate_decisions:{}, graph_id, workspace_root?, inputs?, seed_from_run_id?}` → 202 `{id}` → J6 |

**Surface.** A single pre-flight sheet: Budget (projected cost, honest "not yet priced" rows —
never fake a number), Substrate (graph picker), Inputs (schema-driven fields when `fan_out.over`
targets `$.inputs`), and the GO button. Microcopy for exhaustion: "If a member runs out of budget:
**degrade** — deliver best effort, marked" vs "**escalate** — stop and ask" (the manifest's
`on_exhaustion`, user-visible, plain words).

**States.** *Unpriced:* show token caps instead of USD; never block GO on missing pricing.
*Blocked:* GO disabled with the enumerated reasons (validator / credentials). *Error:* pre-flight
failure → fall back to token caps + retry, never block GO on it; GO failure → the sheet stays
with the server reason rendered (409 `CREDENTIALS_REQUIRED` deep-links per J4 s5; 422 surfaces
the validator report) — nothing submitted twice. *Submitted:* route to the run page immediately
(202).

---

### J6 — Watch the run

**Narrative.** "Is my team healthy, did last night run, what did it cost" (lock O4) — one glance,
then drill down. Failures degrade legibly: a partial result is **delivered and labeled**, never
silently worse (O3).

**Steps → capabilities.**

| # | Step | Endpoint |
| --- | --- | --- |
| 1 | Runs list (org-wide): team runs ⛔C-5 (no list endpoint yet) + existing jobs list | ⛔C-5; `GET /v1/engine/jobs` (built) |
| 2 | Light status header: healthy · state · progress 0–100 · last outcome · cost (tokens; usd when priced) | `GET /v1/engine/team-runs/{id}/status` (poll) |
| 3 | Member grid: per-member status chips — `succeeded / failed / blocked / skipped / budget_skipped / partial / re_task` (ADR-042 vocabulary + the transient `re_task` = queued to re-run after a re-dispatch/revise; render unknown values neutrally, never as an error) | `GET /v1/engine/team-runs/{id}` → `member_status` |
| 4 | Run tree: root + child executions, drill into any member's execution provenance | `…/tree` + `GET /v1/harnesses/executions/{id}` |
| 5 | Outcome banner per terminal state (table below) | `state`, `partial`, `verdict`, `error_message` |
| 6 | **Re-run failed members** (keeps everything that succeeded) | `POST …/rerun` (#551; 409 if nothing failed) |

**Team-run states (the complete machine — code-verified):**
`QUEUED · RUNNING · SUCCEEDED · PAUSED · REJECTED · FAILED · COST_BUDGET`.
There is **no** run-level PARTIAL/ESCALATED/TIMED_OUT/CANCELLED on a *team* run — those belong to
the single-harness job states (`/v1/engine/jobs`, the existing Runs page). Degrade-not-crash
surfaces as `SUCCEEDED` **plus** `partial` entries in `member_status`; a run needing a human —
including a verdict escalation (sentinel role `__verdict_escalation__` in `paused_at`) — is
`PAUSED`.

**Terminal-state banners (exact semantics — do not soften):**

| Condition | Banner | Action |
| --- | --- | --- |
| `SUCCEEDED`, all members `succeeded` | "Run complete." (+ verdict summary if present) | View results (J8) |
| `SUCCEEDED`, some members `partial` | "Complete — N members delivered best effort under budget; their output is marked. Nothing is silently dropped." | View results; marked rows flagged |
| `COST_BUDGET` (run `partial=true`) | "Halted by the team budget cap. Un-run members are marked `budget_skipped`." | Raise cap / rerun |
| `FAILED` | "Run failed at ⟨member⟩." + curated `error_message` | Re-run failed members |
| `PAUSED` (gate role in `paused_at`) | "Waiting on ⟨gate role⟩." | Go to Approvals (J7) |
| `PAUSED` (`__verdict_escalation__`) | "The evaluation flagged this run for review." | Approvals (J7) |
| `REJECTED` | "Rejected at ⟨gate⟩." / "Revision limit reached." | View the gate history |

(Single-harness jobs on the existing Runs page keep their own state set incl. `PARTIAL` /
`ESCALATED` / `TIMED_OUT` / `CANCELLED` — do not merge the two vocabularies in UI copy.)

**Surface.** Status header (mint dot ONLY while `RUNNING`/healthy — the live-signal rule) →
member grid (stage-ordered, same stage rows as J3 so the mental model carries) → collapsible tree.
Poll `status` while active; fetch the full run on state change. No streaming exists — design the
poll, don't fake a stream.

**States.** *Empty (runs list):* "No runs yet" + a route to Teams. *Loading:* poll skeletons on
the header; the grid renders progressively. *Error:* run not found → plain message + back to
Runs; poll failure → "Connection lost — retrying" with the last-known state kept visible, never
a blank.

**Benchmark note.** Member grid ≈ Copilot's activity map / LangSmith run-tree, but stage-shaped
(our DAG is stages, not a freeform canvas). `rerun` ≈ n8n's "retry from failed node" — a loved
pattern.

---

### J7 — Human gates & the Approvals inbox

**Narrative.** A human gate is a **blocking DAG node** (lock item 4b): the run pauses until the
named human advances it. The book studio's seven author gates are the binding case. Approvals is
one inbox for everything human-blocking, so nothing dead-ends.

**Steps → capabilities.**

| # | Step | Endpoint |
| --- | --- | --- |
| 1 | Inbox: paused team runs (⛔C-5 for the org-wide list; interim discovery: `GET /v1/harnesses/assignments` + per-schedule `GET /v1/engine/schedules/{id}/team-runs` + session-launched run ids), admin items (MCP approvals, entity-resolution) | ⛔C-5 · `GET /v1/harnesses/assignments` · `GET /api/v1/tools` filtered client-side on `status == "pending_approval"` (no server-side filter param) · resolution routes |
| 2 | Gate detail: what the producer emitted (the payload under review), which gate, which run | `GET /v1/engine/team-runs/{id}` → `results` + `paused_at` |
| 3 | Decide: **Approve** / **Revise** (with feedback and/or `edited_payload`) / **Reject** | `POST …/advance {gate_decisions:{role:{decision, feedback, edited_payload}}}` (#578, ADR-046) |
| 4 | Revise loop: producer sub-tree re-runs, gate re-pauses; `revision_rounds` counts; exceeding `max_revisions` fail-closes to REJECTED — surface the counter | run fields |
| 5 | Single-harness HITL: claim/complete an assignment | `POST /v1/harnesses/assignments/{id}/claim|complete`, resume via `POST /v1/harnesses/{id}/resume` |

**Surface.** Inbox rows: run · gate role · waiting-since · the ask. Detail: payload viewer
(markdown-aware), three actions. **Revise** is the power move — feedback text plus optional direct
payload edit (LangGraph Agent-Inbox "Edit/Response" pattern; approve-or-reject-only is the
industry weakness — Lindy). Never mint on "waiting" states (warning/neutral tone).

**States.** *Empty:* "Nothing waiting on you." — the inbox's success state, shown plainly.
*Loading/Error:* per-source rows degrade independently (an assignments fetch failure must not
blank the admin items); failed source shows "Could not check" + retry.

---

### J8 — Results, artifacts & delivery

**Narrative.** The run's output lands where the user keeps results: artifacts on the team's
workspace, and back into the user's own target in the source format (lock item 10/O7 — **built**:
#515/#542/#544, Reza-signed). Per ADR-041, deliver-back is not a separate feature: **a sink is a
member whose tools bind a sink connector** (`core/github-sink@1` today — clean-delta branch/PR,
idempotent NO_OP re-delivers; `send-to-drafts` for draft-only email), with the target (repo) on
the connector *instance configuration* and the credential (PAT) via the broker. The FE work is a
"connect your sinks" composition over existing endpoints, not a wait on backend. Verdicts explain
quality. Serving continues via published agents.

**Steps → capabilities.**

| # | Step | Endpoint |
| --- | --- | --- |
| 1 | Artifacts of this run/graph: list, filter, open verbatim content | `GET /v1/artifacts?graph_id=…&q=&source_type=` · `GET /v1/artifacts/{id}` (#543) |
| 2 | Verdict panel: the flow-eval / named-battery outcome (e.g. the 10-gate battery), pass/fail per criterion when present | `TeamRunOut.verdict` (read-side; batteries run inside the run — no separate trigger endpoint, by design) |
| 3 | Refresh delta (seeded-refresh runs): added / removed / changed / unchanged / re-confirmed (machine key: `re_confirmed`, underscore — hyphenate only in display copy) | `TeamRunOut.refresh_delta` (#602) |
| 4 | Graph results: documents, memories, search over what the team wrote | J10 surfaces |
| 5 | Serve it: publish an agent over the workspace, mint a scoped integration key, chat | `/v1/agents*`, `/v1/integration-keys*`, `/v1/chat/*` (all built) |
| 6 | **Connect your sinks**: bind a sink member (e.g. `core/github-sink@1`), configure its instance (`repo`, `base_branch`) and its credential (PAT via broker); re-delivers are idempotent (NO_OP), a recurring refresh writes a clean delta — never a clobbered tree (lock O7/R5, BUILT) | `POST /api/v1/instances` + `…/configure-credentials` + the roster (J3); missing credential surfaces as 409 `needs_credential` → J4 s5 (open FE story #505) |

**Surface.** A Results tab on the run: artifacts table (name · type · source · open), verdict
card, refresh-delta chips. Artifact viewer = read-only drawer with verbatim content. The delta
view is EURail's product moment ("what changed since the last assessment") — give it real design
weight.

**States.** *Empty:* the run delivered no artifacts → say so plainly and link the run tree (the
work still happened); verdict absent → omit the card entirely, never render an empty shell.
*Loading:* table skeleton. *Error:* an artifact fetch failure shows inline in the drawer with
retry.

---

### J9 — Standing teams & schedules

**Narrative.** Three lifecycles are first-class (lock R6b): bounded run (J5), **standing team**
(this journey — bitcoin-gpt's four teams, the book's marketing routines), and **seeded refresh**
(J5 step 4 / J8 step 3). A standing team runs on a cadence with a per-period budget and a
one-glance health surface.

**Steps → capabilities.**

| # | Step | Endpoint |
| --- | --- | --- |
| 1 | Create a schedule from a team: cron/event trigger, bound graph, per-period budget | `POST /v1/engine/schedules {type, target_kind:"team", …, graph_id, budget…}` (#601/#598) |
| 2 | Pre-flight the recurring bill BEFORE saving: "~$X/day at this cadence" (lock O2) | `POST /v1/engine/schedules/preflight` (#603) |
| 3 | Fire now (manual kick, deduped) | `POST /v1/engine/schedules/{id}/fire-now` (202) |
| 4 | History: schedule's runs; team-runs show the persistent bound graph | `GET …/{id}/runs` · `…/{id}/team-runs` |
| 5 | Remove | `DELETE /v1/engine/schedules/{id}` (204). No user-driven pause endpoint exists — the only pause today is the automatic `budget_paused` (per-period cap, resumes at the next window); if a manual pause is wanted, fold it into a Contract |
| 6 | Webhook/event triggers (inbound) | `/v1/webhook-subscriptions` (built, Developer) |

**Surface.** Schedules live inside Team detail (a team's cadence is a property of the team) plus
a column on Home ("did last night run" — derived from `last_fired_at` + `budget_paused` on the
schedule and the latest `GET …/{id}/team-runs` entry's state; there is no `last_outcome` field
on the schedule itself). Budget exhaustion on a standing team = the COST_BUDGET banner (J6) +
"the cap pauses this team's schedule; it never silently overruns" microcopy.

**States.** *Empty:* no schedules → "Create a schedule" as the empty-state action, with the
pre-flight shown before the first save. *Loading:* rows skeleton. *Error:* fire-now failure
surfaced inline on the schedule row; `budget_paused=true` renders as a warning chip ("Paused by
the period cap — resumes ⟨window⟩"), never mint.

---

### J10 — The knowledge substrate (reshaped, was Workspaces/Recipes)

**Narrative.** Graphs stop being "the product" and become **what teams read and write**. The
steward's flows survive intact; the framing and two additions change.

**What changes:**

| Change | Backing |
| --- | --- |
| Graph detail gains an **Artifacts** tab (what teams delivered here) | `/v1/artifacts?graph_id=…` |
| The existing "Agents for this workspace" bindings panel (already shipped on GraphDetailPage) is extended/relabeled **Agents using this workspace**; team-level attribution ("which teams ran here") is ⛔C-1 (teams have no persisted identity yet) | `GET /api/v1/agent-bindings` |
| **Batch ingest** (folder/repo) joins ingest/upload | `POST /api/v1/graphs/{id}/batch-ingest` (#522) |
| Memories surface (facts in/out, search, consolidate) — exists, unexposed | `/api/v1/graphs/{id}/memories*` |
| Copy re-frame: "the team's knowledge" not "your workspace" | copy only |

Everything else (ingest, ontology, communities, resolution HITL, recipes template→dry-run→promote,
search, explorer, federated) is built and stays — see the June-18 journeys for their increment
detail; they remain the reference for those surfaces. Exposure additions surfaced by the 2026-07-03
API sweep: the communities/analytics browse and the memories manager are live endpoints with no UI
(inventory §7) — they extend increment 15's scope.

---

### J11 — Publish & serve (your agent as a product)

**Narrative.** A built team/agent becomes something other people use: published under a public
name, consumed by external systems with scoped keys, connected over MCP, triggered by signed
webhooks, and chatted with in-console. The FE pages exist (Developer + chat); this journey
re-homes them as the first-class **Serve** story (Figma diagram 08) rather than Admin leaves.

| # | Step | Endpoint |
| --- | --- | --- |
| 1 | Publish under a public name (admin); name collision surfaces inline (409 slug-taken) | `POST /v1/agents` · manage `GET /v1/agents`, `GET /v1/agents/{slug}/details` |
| 2 | Mint an integration key — bound to one agent or to capabilities; **secret shown once** | `POST /v1/integration-keys` (+ rotate: old secret dies; revoke: terminal) |
| 3 | External consumer: read metadata + invoke synchronously with the key | `GET /v1/agents/{slug}` · `POST /v1/agents/{slug}/invoke` (key bearer) |
| 4 | Connect via MCP (key-only auth — a member JWT is 403); console shows the connection snippet | `POST /v1/mcp` |
| 5 | Webhook trigger: subscription with a display-once HMAC secret; signed inbound events start runs | `POST/GET/DELETE /v1/webhook-subscriptions` · `POST /v1/webhooks/{id}` (public, signed) |
| 6 | Member chat: private threads bound to a published agent; synchronous turns; thumbs feedback | `/v1/chat/threads*`, `…/messages`, `…/feedback` |
| 7 | Unpublish — warns that live integrations break (tombstone) | `DELETE /v1/agents/{slug}` (admin) |

**States.** *Empty:* nothing published → "Publish a team to give it an audience" with the one
prerequisite listed. *Secrets:* one-time display with an explicit "I saved it" confirm; never
retrievable. *Chat error:* a turn that fails keeps the thread intact with a retryable notice.
**Design constraints:** key/secret handling follows the Connections secret rules (send-only);
admin-gated actions hidden below admin role (recognition, not error-on-click).

---

## 6. Design-system constraints (bind on every journey above)

Per the DS brand book (`Oraclous AI - Design System/README.md`) and the shipped console:

1. Mint `#10D88A` = **live signal only** (a running run, a healthy connection). Never buttons,
   never state that merely *exists*. "Waiting on human" is neutral/warning, never mint.
2. No emoji anywhere; Lucide only (1.5px, monochrome).
3. Banned words in ALL user-facing copy: revolutionize, unleash, supercharge, AI-powered,
   game-changing, seamlessly, leverage (verb), robust, cutting-edge, innovative, empower,
   intuitive, ecosystem, **journey**. (Internal artifact naming exempt.)
4. Sentence case; second-person bare imperative ("Draft the team", "Approve", "Re-run failed
   members"). Numerals as digits.
5. Two-surface model (paper ⇄ ink) only; no third surface, no gradients.
6. `>|` never appears alone; cursor blink `1.06s steps(1,end)`; respect `prefers-reduced-motion`.
7. WCAG AA floor from the first increment: semantic structure, focus order, names/roles;
   drawers keep the `useDrawerA11y` focus trap; tables stay `role="table"`.

> Discrepancy to resolve (docs-writer): FE `CLAUDE.md` §3.4 says "six non-negotiables"; the DS
> `SKILL.md` ("Hard rules to never break") + `docs/handoff/frontend-catchup-roadmap.md` ("The 7
> non-negotiables") enumerate **seven**. Seven is the source of truth until reconciled.

**New-component needs (reground-ds deltas — file BEFORE the increment that consumes them):**
before increment 3 (Phase 1): status-chip set for the **7-value** member vocabulary (incl.
transient `re_task`; unknown values render neutrally), verdict card, pre-flight cost row;
before increment 8 (Phase 2): member-card, stage-rail, tool-ceiling chip, op-diff block, delta
chips (`re_confirmed` machine key). Compose everything else from the shipped console primitives
(drawer/sheet/card/field/status-pill).

---

## 7. What we adopt / reject from the industry (benchmark synthesis)

Surveyed 2026-07-03: OpenAI AgentKit, Claude Code (subagents/teams/skills), Devin, LangGraph/
LangSmith, CrewAI (+AMP/Studio), Relevance AI, Lindy, Copilot Studio, Dust, n8n/Flowise,
Salesforce Agentforce, Intercom Fin, Sierra.

**Adopt (proven patterns):**
- Plan-before-run visibility (Devin's confidence-gated plan) → our compile → review → GO covers
  it, with the lock's polarity kept intact: **compile-and-run is the default; a blocking
  plan-approval hold is opt-in** (lock §4 / item 15 / ADR-047). Landing in J3 review is the
  natural flow, never a required approval gate — a green-validated draft can GO immediately.
- Chat + structure sharing one state (CrewAI Studio) → J3's NL refine beside the roster.
- Inbox-for-interrupts (LangGraph Agent Inbox) → the Approvals surface, with **Revise** (edit +
  feedback), not just approve/reject.
- Retry-from-failure preserving successes (n8n debug/pin ethos) → `rerun` is server-native; give
  it a first-class button.
- Publish-blocking evaluation (Relevance's Publish gate) → our `would_block` validator strip.
- Consumption drill-down + threshold alerts (Salesforce Digital Wallet) → Billing later; run/
  schedule cost surfaces now.
- Typed, visible structural deltas (AgentKit's typed edges) → the op-diff preview in J3.

**Reject (documented failure modes):**
- Canvas-first authoring — AgentKit's Agent Builder was deprecated within ~8 months; OpenAI now
  steers to code or pure NL. Our two doors (NL + files) skip the doomed middle. No node canvas.
- Credit opacity / surprise burn (Lindy, Relevance top complaint) → always show token/user-priced
  reality; say "not yet priced" honestly (⛔C-2), never invent a number.
- Silent overrun or silent partiality (Fin's "assumed resolution" resentment) → COST_BUDGET halts
  and PARTIAL labeling are contractual UI, not fine print.
- One-way export lock-in (AgentKit) → import stays symmetric: what you brought remains yours;
  fidelity is the acceptance test.
- Per-tool auth walls mid-run (everyone) → readiness checklist before GO (J4), 409 deep-links.

**Whitespace we own:** pre-GO cost pre-flight; import-fidelity as a promise; capability-absence
fail-closed at draft time; the labeled-partial delivery contract.

---

## 8. Backend-gap Contracts — reconciled against ADRs + the issue board (2026-07-03)

The first draft of this register was corrected by a full reconciliation pass (ADR-040/041/044/047/
048, issues #472–#604). The **cloud-first pivot is ratified** — ADR-040 Decision 7 (accepted
2026-06-24), encoded in #523 ("local import/export — PARKED per Reza's cloud-first decision") and
#388 (local GO demoted) — and explains what was parked deliberately vs genuinely missing.

**Already BUILT (no Contract — the earlier draft overstated these):**
- *Compiler reachability*: the compiler runs through `POST /v1/engine/team-runs` as a team harness
  — ADR-047's explicit posture ("no new gateway routing"); validate/refine are the
  `core/manifest-validate@1` / `core/manifest-refine@1` registry tools. E10 #593/#594/#595/#596
  all CLOSED (#597 eval-set + #440 book-GO remain open, both `needs-human` acceptance items).
- *Standing-team persistence*: the schedule row durably persists `manifest_inline`/`manifest_ref`
  + `graph_id` + `recurring_cost_tokens` (#601).
- *Schedule cost pre-flight*: `POST /v1/engine/schedules/preflight` with per-member
  `priced`/`usd_per_fire`/`usd_per_day` + `unpriced_members` (#603; rates from the harness
  `billing/rates.py`).
- *Deliver-back (was "C-6" — withdrawn)*: #515/#542/#544 CLOSED, ADR-041 Accepted. A sink is a
  member tool (`core/github-sink@1`: configured `repo`, PAT via broker, clean-delta branch/PR,
  idempotent NO_OP; `send-to-drafts` for draft-only). The residue is the FE "connect your sinks"
  composition (J8 s6), leaning on **open #505** for the `needs_credential` prompt — an FE story,
  not a backend Contract.

**Contracts — filed just-in-time, not up-front (Reza, 2026-07-03).** No backend work starts
before the FE pipeline actually approaches the consuming increment: **C-5** files when Phase 1
nears increment 7; **C-1** when Phase 2 nears increment 12; **C-2**'s USD portion only if/when
increment 11 wants dollars (token caps carry it meanwhile). Until then these rows are a tracked
plan, not open tickets.

| # | Missing capability | Consuming journey/step | User-facing requirement (the shape is solution-architect's) |
| --- | --- | --- | --- |
| **C-1 (re-scoped)** | **On-ramp ergonomics + draft persistence.** (a) The compiler-team manifest is constructible only by `packages/ohm build_compiler_team()` — nothing serves or seeds it, so a browser cannot obtain it; (b) an interactive draft (compile → refine → …) has no save/list/re-open/version home (`apply_refine()` is stateless; #601 covers only *scheduled* teams); (c) re-import merge onto an existing team (lock O5) is unticketed (adjacent to parked #523). | J1 s2 · J3 s1 · J2 s5 | (a) The console can fetch/instantiate the compiler team (seeded or served); (b) drafts persist per org — also enables team-level attribution on workspaces; (c) re-import merges: upstream changes + in-platform edits both survive, conflicts surfaced, never a silent clobber. One validator seam stays shared (#593). |
| **C-2 (re-scoped)** | **USD-surfacing harness.** `TeamRunCost.usd` is null by documented design and `OHMBudget.max_usd_total` is recorded-but-inert (`manifest.py:326` — the pool's USD axis is never incremented); both hang off the same missing USD-surfacing work. Optional (b): a run-level (non-schedule) pre-flight projection. | J5 s1/s5 · J6 s2 · J9 s2 | Real `usd` on run status; a USD cap that actually halts; (optional) "~$ for this run" before a one-shot GO. |
| **C-5 (unchanged)** | **Team-run list endpoint** (org-scoped, state-filterable, paginated). Only `GET …/team-runs/{id}` + per-schedule lists exist; #472 built the per-run O4 status, not a list. | J6 s1 · J7 s1 (Approvals needs "all PAUSED") | Runs page lists team runs; Approvals lists paused ones. |

Minor/flagged, not Contracts yet: no SSE/streaming anywhere (polling is the design — revisit only
if chat UX demands it); named batteries have no standalone trigger endpoint (by design — read-side
only); `/api/v1/ontology`-suggest and `/api/v1/communities`-kinds routers are not in the gateway
route table (KGS-side; flag to solution-architect with C-1); webhook/docify sink connectors beyond
github/drafts are the ADR-041 future path (#541 MCP-imported sinks); several live, console-consumed
route groups (orgs/members/invitations, communities, roundtables, activity/usage) are **absent from
the published `openapi/v1.yaml`** — a docs-contract gap for docs-writer/solution-architect, not a
capability gap (the 2026-07-03 API sweep enumerated 93 features; the spec + Figma board are drawn
from the live routes).

Register these in `flows/interface-contracts.md` when filed. G1 (OAuth connect) and G2 (agent
bindings) from the June-18 register are **shipped** — the register in the inventory is updated.

---

## 9. Build order (increments grouped into phase-sized deliveries)

**Delivery model (Reza, 2026-07-03 — replaces the per-increment baton for this spec):**
- **One PR per phase.** The increments below remain the tracked issues (each carries its
  live-app test recipe), but a phase ships as **ONE PR with one commit per increment** — never a
  stream of tiny PRs "delivering nothing". A phase is the smallest unit Reza looks at.
- **Review is one pass per phase PR, two questions only:** (1) are we on the spec's track, and
  (2) is it **operating, not a mock** — driven on the running console against the real gateway
  (real endpoints, real runs, zero fabricated data; the FUCK_CLAUDE_FUCK_PAPERCLIP no-fake rule
  applies to the FE too). No interleaved review iterations, no craft-nit rounds, no human CI
  babysitting before a phase is shippable; the automated FE invariant checks run machine-side as
  usual.
- **Reza tests the shipped phase live**, then the next phase readies.

Each increment still runs on the live app and states its test; land order within a phase is fixed.

**Phase 0 — plumbing (no visible UI):**
1. `api-client`: `teamRuns` namespace (`create/get/status/tree/advance/rerun`), `schedules`
   (+`preflight`), `artifacts`, `graphs.batchIngest` + `graphs.memories`, types for
   `TeamRunOut`/`member_status` (7 values)/`GateDecision`/error envelope extras
   (`needs_credential`, 405 hints). *Test: typecheck + a mocked-transport unit suite; no page
   changes.*
2. Retire the dead legacy monolith client export (`client.ts`) — delete or quarantine. *Test:
   build green; no page imports it.*

**Phase 1 — Runs & Approvals (real data exists today via e2e-created runs):**
3. Run detail v2 for team runs: status header + member grid + terminal banners (J6 s2–5), reached
   by id (deep link) until C-5 lands. *Test: run the e2e seed script; open `/app/runs/team/{id}`;
   all 6 member-status chips render; PARTIAL and COST_BUDGET banners match §J6 table.*
4. Run tree + member execution drill-down (J6 s4). *Test: tree renders root+children for a
   fan-out run.*
5. Re-run failed members (J6 s6). *Test: a FAILED seeded run → rerun → only failed members
   re-drive; 409 handled on a SUCCEEDED run.*
6. Approvals inbox v1: harness assignments + gate detail + advance approve/revise/reject (J7),
   with **interim paused-run discovery** (assignments + per-schedule team-runs + ids of runs
   launched this session) — deep-link-only is a dev-test posture, not a user-facing release; the
   gate-keeper must be able to find a paused run without recalling a URL. *Test: a PAUSED seeded
   run → appears via interim discovery → revise with feedback → re-pauses; approve → completes;
   revision counter shows.*
7. Runs list v2 + Approvals list (⛔C-5) — lands when C-5 ships; replaces the interim discovery.
   *Test: paused runs appear in Approvals without a deep link.*

**Phase 2 — the team loop (review → runnable → GO):**
8. Team review surface (J3 s1–2): roster + stage rail + validation strip, fed from a local
   draft (fixture or C-1). *Test: a draft with an unsurveyed tool shows the blocking row;
   fixing it flips the strip.*
9. NL refine rail (J3 s3–4). *Test: "add a fact-checker" → op-diff shown → apply → roster gains
   the member, others byte-identical; an op naming an unknown tool is rejected with the manifest
   untouched.*
10. Readiness checklist + 409 deep-link (J4). *Test: strip a credential → GO disabled with
    reason; 409 from any call lands on Connections with the provider pre-selected.*
11. Pre-flight & GO sheet (J5). *Test: GO on a seeded draft creates a run (202) and routes to J6;
    unpriced members show token caps, not fake USD.*
12. On-ramp doors, **Describe first** (J1 s1) — behind **C-1(a/b)**. *Test: prose objective →
    compiler progress → roster review.* The Import door (J2 s1–2) is **parked** with #523
    (cloud-first, ADR-040 D7) and un-parks when Reza re-opens local import — its design stays
    signed and ready.

**Phase 3 — standing & substrate:**
13. Nav v2: insert **Teams** + **Approvals** + the **Serve** group (re-homing the built
    Developer/chat pages, J11), regroup Library/Knowledge, relabel Members → People and
    Billing → Usage & spend (§4). *Test: all old routes redirect; persona trees correct; axe
    clean.*
14. Schedules surface + Home health column (J9) — built **org-level** against the live
    `/v1/engine/schedules*` routes now; its placement folds into Team detail when C-1 lands
    (Team detail requires draft persistence). *Test: create daily schedule with pre-flight
    shown; fire-now produces a listed run.*
15. Artifacts tab + agents-using-this-workspace relabel + batch ingest + memories exposure +
    communities/analytics browse (J10) — extends the existing GraphDetailPage bindings panel,
    does not add a new one. *Test: a seeded run's artifacts list and open; batch ingest of a
    3-file folder shows 3 jobs; the analytics card renders node/edge counts.*
16. Results tab: verdict card + refresh-delta chips (J8). *Test: a seeded-refresh run renders
    the 5-way delta.*
17. "Connect your sinks" (J8 s6) — **unblocked backend-side** (ADR-041 sink-tool model): bind a
    sink member + configure its instance (repo) + credential (PAT via broker); folds in the open
    #505 `needs_credential` prompt story. *Test: a team with `core/github-sink@1` configured
    delivers a clean-delta PR; re-deliver is NO_OP.*

DS re-grounding deltas (§6) file in two tranches: chips/verdict/cost-row before increment 3;
member-card/stage-rail/tool-chip/op-diff before increment 8. Dashboard refresh (team health
strip) rides with 14.

---

## 10. Supersession map

| Prior artifact | Status now |
| --- | --- |
| `journeys/tools.md`, `connections.md`, `recipes.md` | Valid, supporting surfaces (Library / Connections / Knowledge). Unbuilt increments still apply. |
| `journeys/navigation-ia.md` | Superseded by §4 (nav v2) — its increments shipped; §4 is the next restructure. |
| `journeys/agents-harness.md` | Valid for the single-agent Library surface; its G2 gap is shipped (`/api/v1/agent-bindings`). Team authoring does NOT extend the single-agent builder — it is J3. |
| `product/roadmap.md` | Updated alongside this spec (epic order → §9 phases). |
| `oraclous-frontend/docs/handoff/frontend-catchup-roadmap.md` | **Superseded as product frame.** Keep only as a build-history record. |
| June-18 inventory gap register (G1, G2) | Both shipped; replaced by C-1/C-2/C-5 (§8). |

*Signed: experience-architect, 2026-07-03. The journeys above are walkable against the running
gateway except where marked ⛔C-n; those steps are Contract-gated and must not ship as FE
workarounds.*
