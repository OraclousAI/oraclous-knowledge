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

---

## Backend-gap register (capabilities a journey will need that the gateway does not expose yet)

| # | Gap | Consuming journey | Status |
| --- | --- | --- | --- |
| G1 | OAuth-connect bridge: a provider token captured at login → resolvable as a broker tool credential | Connections / OAuth-connect | Contract to file (solution-architect) |
| G2 | Workspace↔harness binding (define a harness for a workspace) | Workspace harness | Needs an ADR (solution-architect) |

These become GitHub `Contract` issues for `solution-architect` when their journey is scheduled.
