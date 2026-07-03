---
title: "Capability-surface inventory"
owner: experience-architect
status: living
source-of-truth: the application-gateway route table + the per-service routes (verify against the running gateway)
---

# Capability-surface inventory

**What this is.** The catalogue of what the Oraclous platform can actually expose to a user **through the
gateway today** — the single grounding substrate every journey, IA decision, and design traces to. It is
the antidote to cloning the legacy app: a product surface is legitimate only if it maps to a row here (a
real capability) or to a filed backend-gap Contract. A surface that maps to neither is out of scope.

**How it was built.** From the gateway route table (`application-gateway-service/.../domain/route_table.py`)
— the only edge surface the frontend may call — plus the per-service routes confirmed in the post-R6 audit.
This is a **living** document: `experience-architect` refreshes it (`/xa inventory --refresh`) and grows
detail as journeys need it. Endpoint paths below are gateway paths (what the typed `@oraclous/api-client`
calls); the frontend talks to nothing else (FE invariant §1.1).

**FE coverage legend:** ✅ built · 🟡 partial / browse-only · ⛔ absent (capability exists, no UI) · 🚧 backend gap.

> **Refresh 2026-07-03 (experience-architect).** §7 added: the team-of-agents runtime surface
> (team runs, gates, schedules, cost pre-flight, artifacts, seeded refresh) shipped through the
> gateway since mid-June — none of it has UI yet. The old gap register (G1/G2) is closed — both
> shipped (`/oauth/{p}/connect*` + `/api/v1/agent-bindings`) — and replaced by C-1/C-2/C-5.
> The consuming spec is `journeys/team-of-agents-console.md` (journey spec v2). §1–§6 coverage
> marks reflect the shipped Tools/Connections/Recipes/Nav epics where noted; verify per-row
> against the running console when a journey picks the row up.

---

## 1. Tools & capabilities (capability-registry) — `/api/v1/{tools,capabilities,instances,executions}`

The platform's tool model is **register a tool descriptor → create a configured *instance* of it → attach
credentials to the instance → validate → execute.** The instance is the first-class "a configured, usable
tool" object. The legacy-cloned Tools page exposes only the catalogue + MCP import.

| Capability | Gateway endpoint(s) | What it lets a user do | FE coverage |
| --- | --- | --- | --- |
| Browse the tool catalogue | `GET /api/v1/tools` | See the org's tools (built-ins + registered) | ✅ `ToolsPage` |
| Inspect one tool | `GET /api/v1/tools/{id}` | See a tool's capabilities, credential requirements, docs | ⛔ tiles are inert |
| Register a custom tool | `POST /api/v1/tools` (OHM descriptor) | Add a tool that isn't a built-in | ⛔ |
| Import an MCP server's tools | `POST /api/v1/tools/import-mcp` → pending-approval | Bulk-add external MCP tools (admin) | ✅ admin-only |
| Approve / reject imported tool | `POST /api/v1/tools/{id}/{approve,reject}` | Supply-chain HITL gate (admin) | ✅ admin-only |
| Capability CRUD | `GET/POST/PUT/DELETE /api/v1/capabilities[/{id}]` | Manage capability descriptors | ⛔ |
| Create a configured tool instance | `POST /api/v1/instances` (`configuration`/`settings`) | "Set up this tool" for use | ⛔ (client exists, used only in agent loop) |
| Attach credentials to an instance | `POST /api/v1/instances/{id}/configure-credentials` | Map credential_type → a stored credential | 🟡 only inside the agent builder |
| Validate an instance | `GET /api/v1/instances/{id}/validate-execution` | "Test connection" before using it | ⛔ |
| Instance health | `GET /api/v1/instances/{id}/health` | See if the configured tool is healthy | ⛔ |
| Execute a tool instance | `POST /api/v1/instances/{id}/execute` (+ `/executions`) | Run a tool directly | 🟡 agent run loop only |

**Headline gap (FE, not backend):** the whole register → instance → configure-credentials → validate
lifecycle exists through the gateway but is invisible on the Tools page. This is the user's "tools aren't
configurable / where do I add tools / how do I attach credentials" complaint — a frontend exposure gap.

## 2. Recipes & ingestion (knowledge-graph) — `/api/v1/recipes`, `/api/v1/graphs/{id}/ingest*`

A recipe is an agent-authored (data-specialist), schema-validated **format-0.2** document (ADR-022) that
projects a source into graph nodes/edges. It is authored from a template + a sample, dry-run-previewed,
saved as a draft, then **run as an ingestion job against a chosen graph** — not edited as free CRUD fields.

| Capability | Gateway endpoint(s) | What it lets a user do | FE coverage |
| --- | --- | --- | --- |
| Browse recipes | `GET /api/v1/recipes` | See the org's ingestion recipe library | ✅ `RecipesPage` |
| Inspect a recipe | `GET /api/v1/recipes/{id}` | View the recipe document | 🟡 raw JSON dump |
| Start from a template | `GET /api/v1/recipes/templates` | Get an author-ready starting point | ⛔ |
| Dry-run a recipe | `POST /api/v1/recipes/dry-run` | Preview the projection over a sample, no writes | ⛔ |
| Save a recipe (draft) | `POST /api/v1/recipes` | Persist an authored recipe | ⛔ (client has no POST) |
| Run a recipe on a graph | `recipe_id` on `POST /api/v1/graphs/{id}/{ingest,upload,ingest-sql}` | Ingest a source into a workspace | ⛔ |

**Note:** a naive "add a recipe" CRUD form is the *wrong* model — recipes need template + dry-run + save +
run-on-graph. The page today is an inert viewer; that's the real miss.

## 3. Connections & credentials (credential-broker + auth OAuth) — `/credentials`, `/oauth`

| Capability | Gateway endpoint(s) | What it lets a user do | FE coverage |
| --- | --- | --- | --- |
| List my connections | `POST /credentials/retrieve/` | See stored tool/model credentials | 🟡 Settings → Connections |
| Add a credential (manual secret) | `POST /credentials/` | Paste an API key / connection string | ✅ manual entry |
| Update / delete a credential | `PATCH/DELETE /credentials/{id}` | Manage a stored credential | 🟡 partial |
| List providers / data-sources | `GET /credentials/{providers,available-data-sources}` | See what can be connected | 🟡 |
| App sign-in via OAuth | `GET /oauth/{providers,{provider}/login,{provider}/callback}` | Log in with Google/GitHub/Notion | ✅ login only |
| **Connect a provider to use as a tool credential** | — (auth captures the token at login; **no gateway bridge** to the broker) | OAuth auto-connect a tool instead of pasting keys | 🚧 **backend gap** — auth stores the provider token at login but nothing exposes it as a broker credential; needs a bridge Contract |

**Note:** the OAuth auto-connect the user wants is *most of the way built* — auth-service already captures
Google/GitHub/Notion access+refresh tokens at sign-in and the broker has a full token resolver; what's
missing is (a) a gateway bridge so a connected provider's token is resolvable as a tool credential, and
(b) a "Connect with…" affordance. That bridge is the first backend-gap Contract.

## 4. Agents & harnesses (harness-runtime + capability-registry) — `/v1/harnesses`, `kind:"harness"` capabilities

| Capability | Gateway endpoint(s) | What it lets a user do | FE coverage |
| --- | --- | --- | --- |
| Author an agent (OHM manifest) | `POST /api/v1/capabilities` (`kind:"harness"`) | Build an agent: prompt, model, tools, budget | ✅ `AgentBuilderPage` |
| View an agent / its runs | harness capability + `GET /v1/harnesses/.../executions` | Inspect an agent and its runs | ✅ `AgentHarnessDetailPage` |
| Run a harness | `POST /v1/harnesses/execute` (manifest or ref + input) | Execute an agent to completion | ✅ |
| Resume / spend / assignments | `/v1/harnesses/...` | Durable run controls | 🟡 |
| **Bind a harness to a workspace** | — (org-scoped only; no workspace↔harness relation) | "Define the agent(s) for this workspace" | 🚧 **new concept** — needs an ADR (workspace↔harness relation) |

## 5. Workspaces / graphs & retrieval (knowledge-graph + retriever) — `/api/v1/graphs`, `/v1/{search,graph,federated}`

| Capability | Gateway endpoint(s) | What it lets a user do | FE coverage |
| --- | --- | --- | --- |
| Workspaces (= knowledge graphs) | `GET/POST /api/v1/graphs` | Create/list a workspace (a graph) | ✅ `WorkspacesPage` |
| Workspace detail: ingest / ontology | `/api/v1/graphs/{id}/...` | Ingest sources, edit ontology | ✅ `GraphDetailPage` |
| Search / subgraph / federated | `GET /v1/search`, `/v1/graph/{id}`, `/v1/federated/*` | Query a workspace; cross-graph reads | ✅ Explorer |
| Retrieval-quality evaluation | `POST /v1/graph/{id}/evaluate` | RAGAS-style eval (#331) | ⛔ |

## 6. Identity, orgs, billing, execution-engine — `/v1/{auth,orgs,invitations}`, `/v1/engine`

| Capability | Gateway endpoint(s) | What it lets a user do | FE coverage |
| --- | --- | --- | --- |
| Auth / session | `/v1/auth/*` | Sign up, log in, session | ✅ |
| Orgs, members, roles, invites | `/v1/orgs/*`, `/v1/invitations/*` | Manage the org and members | ✅ Members |
| Durable orchestration | `/v1/engine/*` | Execution-engine flows above the harness | 🟡 Jobs |
| Billing / metering | (per org) | Cost/usage | ✅ Billing |

## 7. Teams, runs, schedules, evaluation, budgets (execution-engine + harness-runtime + KGS) — `/v1/engine/*`, `/v1/harnesses/*`, `/v1/artifacts`

The team-of-agents runtime (the locked product — north-star lock §0): two on-ramps (compile /
import) converge on one validator, then one governed team run. Shipped through the gateway since
mid-June (#576–#604); **no FE coverage anywhere in this section.** Full request/response detail:
`journeys/team-of-agents-console.md` §5.

| Capability | Gateway endpoint(s) | What it lets a user do | FE coverage |
| --- | --- | --- | --- |
| **Start a team run (GO)** | `POST /v1/engine/team-runs` (202) — `{manifest, sub_harnesses, gate_decisions, graph_id, workspace_root?, inputs?, seed_from_run_id?}` | Run a whole team as one governed unit; seed fan-out inputs; seeded refresh | ⛔ |
| Read a team run | `GET /v1/engine/team-runs/{id}` — state, `results{role}`, `member_status{role}` (succeeded/failed/blocked/skipped/budget_skipped/partial + transient `re_task`), `paused_at`, `verdict`, `refresh_delta` (`re_confirmed` underscore key), `partial`, `revision_rounds` | Full run readout incl. evaluation verdict + refresh delta | ⛔ |
| Light status | `GET /v1/engine/team-runs/{id}/status` — `{healthy, state, progress 0-100, last_outcome, cost{tokens, usd\|null}}` | "Is my team healthy / what did it cost" at a glance (lock O4) | ⛔ |
| Run tree | `GET /v1/engine/team-runs/{id}/tree` | Root + child executions (drill into member provenance via `/v1/harnesses/executions/{id}`) | ⛔ |
| **Advance a human gate** | `POST /v1/engine/team-runs/{id}/advance` — `{gate_decisions:{role:{decision: approve\|revise\|reject, feedback, edited_payload}}}` | Resolve a PAUSED blocking gate; revise re-runs the producer sub-tree; `max_revisions` fail-closes to REJECTED | ⛔ |
| Re-run failed members | `POST /v1/engine/team-runs/{id}/rerun` | Re-drive FAILED+BLOCKED only, keep SUCCEEDED (409 if nothing failed) | ⛔ |
| Terminal/degraded states | **team-run** `state`: QUEUED · RUNNING · SUCCEEDED · PAUSED · REJECTED · FAILED · COST_BUDGET (degrade surfaces as SUCCEEDED + `partial` member entries; human-needed incl. verdict escalation = PAUSED). Single-harness **jobs** keep their own set incl. PARTIAL/ESCALATED/TIMED_OUT/CANCELLED | Degrade-not-crash (labeled partial, lock O3); pooled-budget halt with `budget_skipped` members | ⛔ |
| **Validate a draft team** (the shared validator) | `Manifest Validate` capability → `POST /api/v1/instances/{id}/execute` (sync 201, ExecutionOut envelope) → `output_data:{would_block, blocking[], report}` | Deterministic, keyless dry-run gate — same validator for compiled and imported teams | ⛔ |
| **NL refine as typed delta** | op-drafter (tiny team run) + `Manifest Refine` capability → `POST /api/v1/instances/{id}/execute` (sync 201) → `output_data:{would_block, applied, blocking[], manifest\|null}` | "Add a fact-checker" as a typed op; preserve-the-rest; unsurveyed tool → rejected (`applied=false`), manifest untouched | ⛔ |
| Schedules (standing teams) | `POST/GET/DELETE /v1/engine/schedules`, `POST …/{id}/fire-now`, `GET …/{id}/runs`, `GET …/{id}/team-runs` | Cron/event-fired teams with a bound graph + per-period budget (lock R6b) | ⛔ |
| **Cost pre-flight** | `POST /v1/engine/schedules/preflight` — "~$X/day at this cadence" + `unpriced_members` | Projected recurring bill BEFORE GO (lock O2) | ⛔ |
| Run artifacts | `GET /v1/artifacts?graph_id=…&q=&source_type=`, `GET /v1/artifacts/{id}` | Deliverables a run landed on the team's graph, verbatim content | ⛔ |
| Single-harness runs (existing) | `POST /v1/harnesses/execute`, `…/{id}/resume`, `GET /v1/harnesses/executions*`, `/v1/engine/jobs*` | The single-agent runtime under the team layer | ✅ (agents/runs pages) |
| Human task board (harness HITL) | `GET /v1/harnesses/assignments`, `POST …/{id}/claim\|complete` | Claim/complete escalated human tasks | ⛔ |
| BYOM spend (retrospective) | `GET /v1/harnesses/spend?since=` | Estimated provider spend from token sums (ADR-009) | ✅ Billing |
| Retrieval-quality eval | `POST /v1/graph/{id}/evaluate` (RAGAS-style, #331) | Judge a Q/A against a graph | ⛔ |
| Batch ingest | `POST /api/v1/graphs/{id}/batch-ingest` (202/job-per-item) | Folder/repo ingestion (#522) | ⛔ |
| **Deliver-back sinks** | sink = a member tool: `core/github-sink@1` (instance-configured `repo`, PAT via broker, clean-delta branch/PR, idempotent NO_OP re-deliver) · `send-to-drafts` (draft-only) — ADR-041, #515/#542/#544 | Run outputs land in the user's own git tree / drafts queue, one-shot and scheduled | ⛔ |
| Graph memories | `/api/v1/graphs/{id}/memories*` (add/search/context/update/delete/consolidate) | Facts in/out of the substrate | ⛔ |

**Frontend contract notes (edge behavior):** org comes from the JWT — never send org headers;
202+poll for run-producing operations (team-runs, advance, rerun, fire-now, ingest) while the
registry execute seam (validator/refine), harness execute, and schedule create are synchronous
201 with the result inline (no SSE/WebSocket anywhere; chat is synchronous); uniform error envelope
`{error:{code,message,requestId,retryable,details?,needs_credential?}}` — 409 `CREDENTIALS_REQUIRED`
carries `needs_credential:{requirement_id,provider}`, 422 carries loc/type detail rows, 405 carries
a curated hint + `Allow`; gateway-native lists paginate `?limit=&offset=` (default 100, max 200,
bare arrays); admin-gated ops: publish agent, integration keys, webhook subscriptions, MCP
import/approve.

---

## Backend-gap register — reconciled against ADRs + the issue board (2026-07-03)

Cloud-first is ratified (ADR-040 Decision 7; #523 parks local import/export; #388 demotes local
GO) — it explains what was parked deliberately vs genuinely missing. Full reconciliation:
journey spec v2 §8.

| # | Gap | Consuming journey | Status |
| --- | --- | --- | --- |
| **C-1 (re-scoped)** | **On-ramp ergonomics + draft persistence:** (a) the compiler-team manifest is only constructible via `packages/ohm build_compiler_team()` — nothing serves/seeds it to a browser (the compiler itself runs through `POST /v1/engine/team-runs`, ADR-047 "no new gateway routing"); (b) interactive drafts have no save/list/version home (#601 persists only *scheduled* teams); (c) re-import merge (lock O5) unticketed | J1/J3 (J2 s5) | Contract to file (solution-architect) |
| **C-2 (re-scoped)** | **USD-surfacing harness:** `TeamRunCost.usd` null by documented design; `max_usd_total` recorded-but-inert (`manifest.py:326`, pool USD axis never incremented). Optional: run-level pre-flight. Schedule pre-flight is **BUILT** (#603) | J5/J6/J9 | Contract to file (solution-architect) |
| **C-5** | **Team-run list endpoint** (org-scoped, state-filterable, paginated) — only `GET …/{id}` + per-schedule lists exist (#472 was per-run) | J6 runs list · J7 approvals inbox | Contract to file (solution-architect) |
| ~~C-6~~ | Delivery sink write-back | J8 | **WITHDRAWN — built** (#515/#542/#544, ADR-041): sink = a member tool (`core/github-sink@1` clean-delta/idempotent; `send-to-drafts`); residue = FE "connect your sinks" story, leaning on open **#505** |
| ~~import door~~ | Local bundle import endpoint | J2 | **Parked by decision** (ADR-040 D7 / #523) — not a gap; un-parks when local re-opens |
| ~~G1~~ | OAuth-connect bridge | Connections | **Shipped** (`POST /oauth/{p}/connect` + `…/connect/complete`; Connections page built) |
| ~~G2~~ | Workspace↔harness binding | Agents | **Shipped** (`/api/v1/agent-bindings`, consumed by GraphDetailPage) |

These become GitHub `Contract` issues for `solution-architect` when their journey is scheduled.
