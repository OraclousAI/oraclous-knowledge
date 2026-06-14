---
title: "Journey — Agents & harness: legible build, run, resolve — then bind to a workspace"
owner: experience-architect
status: signed
signed-by: experience-architect
surface: AgentBuilderPage / AgentHarnessDetailPage / AgentDetailPage / AgentsPage
grounds-in: capability-surface-inventory.md §4 (harness-runtime + kind:harness capabilities)
legacy-divergence: the OHM agent builder/runtime already exists (not a legacy clone); this is clarity + completeness, plus one new concept (workspace↔harness binding) the backend does not model yet.
backend-gaps: G2 (workspace↔harness binding — blocks increment 6)
---

# Journey — Agents & harness

**Persona.** The operator/builder who authors agents and reads their runs — and wants to "define the agent(s)
for a workspace." The most complete surface on the platform; this epic is clarity, completeness, and one new
concept, not a rebuild.

**Today (the problem).** The builder maps 1:1 onto the OHM manifest but is a long flat scroll with a free-text
model binding and a BYOM-key requirement only hinted at the bottom (the #1 reason runs fail). Runs poll
correctly but the table is bare and the per-step provenance trace is only reachable by drilling into one run;
**a run that escalates to a human is a dead end** — the assignment/claim/complete/resume endpoints exist on
the gateway but the api-client only exposes `spend()`. And there is **no** "agents for this workspace" concept
(OHM anchors only on `owner_organization_id`; backend gap **G2**).

## Design constraints
Mint = a running-run dot or healthy indicator only; "waiting on human" stays neutral/warning (never mint).
Replace AgentDetailPage's literal `✓`/`←` text glyphs with Lucide if that file is touched. Runs table stays
`role="table"`; RunDetail stays a focus-trapped drawer. Sentence case, no emoji, AA floor; compose from
existing agent.css/runs.css primitives. A model picker needing a new combobox token, or a binding affordance
needing a new relation-chip, is a separate `reground-ds` delta — never inline.

## Increments (small, vertical, each testable on the app)

| # | Increment | Gateway capability | Test on the app | Blocked |
| --- | --- | --- | --- | --- |
| 1 | **Separate OHM agents from tool instances** (IA + copy clarity) | renders from existing data | `/app/agents`: lower block reads "tool instance" throughout (no "Create agent"); one-line distinction | no |
| 2 | **Model picker + BYOM-key readiness** in the builder | client-side model list + existing `useCredentials()` | Model is a picker (+ "other" free-text); no key → neutral "key required" marker + Create disabled | no |
| 3 | **Pre-save review summary** in the builder | in-form state | review summary (name/model/key-wired/tool count/budget) above Create; reflects `valid` | no |
| 4 | **Richer runs table** with per-run step/provenance summary | existing jobs poll + execution fetch | each run row shows outcome cue + step summary; running=mint, escalated=neutral, failed=error | no |
| 5 | **Resolve an escalated run** (claim / complete / resume) | `/v1/harnesses/assignments*` + `/{id}/resume` — **new api-client methods** (gateway exposes them) | escalated run → claim → complete/resume → flips ESCALATED→SUCCEEDED/FAILED; state stays neutral | no |
| 6 | **Define the agent(s) for a workspace** | **needs G2** (workspace↔harness relation + endpoint) | workspace detail shows "Agents for this workspace" + attach/detach; agent shows its workspace(s) | **G2** |

## Increment 1 — build brief (the first issue)

**Goal.** Stop calling two different things "agent": keep OHM agents as the primary "Agents" section and
re-label the tool-instance block consistently, with one line distinguishing them.

**Scope (in).** On `AgentsPage.tsx` keep the OHM-agents section primary; re-label the "Create a tool instance"
block + its submit (currently "Create agent") to "tool instance" consistently; add one line of sub-copy:
"an agent is an OHM manifest run durably through the engine" vs "a tool instance is a single configured tool
run directly", with a Lucide-iconed inline note linking the two. No data-model or route change; compose from
existing card/empty/status-pill/cat-tile primitives.

**Scope (out).** No builder/runs changes; no nav/route restructure; no workspace concept.

**How to test on the app.** `VITE_API_BASE_URL=<gateway> pnpm --filter @oraclous/console dev`, open
`/app/agents`: top "Agents" section unchanged and primary; lower block reads "tool instance" throughout (no
"Create agent"); the one-line distinction is visible. Keyboard reaches "New agent", the create-instance form,
and every tile in order; axe-core AA clean. No regression: creating a tool instance still navigates to
`/app/agents/{id}`; clicking an OHM agent still opens `/app/agents/harness/{id}`.

## Backend gap G2 (Contract/ADR → solution-architect, oraclous-backend)
There is no relation tying an OHM agent (harness) to a workspace (knowledge graph) — an OHM manifest anchors
only on `owner_organization_id` (OHM spec line 96); `/api/v1/graphs` and `/api/v1/capabilities` are
independent surfaces with no binding endpoint. Delivering "define the agent(s) for this workspace" needs an
**ADR** from solution-architect deciding the relation (direction; manifest label vs capability-registry edge
vs knowledge-graph association; ReBAC/org-scoping implications) and a gateway endpoint to list/attach/detach
the harnesses bound to a graph. **User-facing requirement:** open a workspace and see/manage the agents that
operate on it, instead of every agent living in one flat org-wide list.
