---
confluence_id: "393380"
title: "Section 2 — Conceptual Model"
---

# Section 2 — Conceptual Model

**Related structured artifacts:** several entries below — _Manifest_, _Harness_, _Capability_, _Organisation_, _ReBAC_, _Provenance_ — are dictionary-level definitions. Their implementation contracts live in sibling pages: [OHM v1.0 Standalone Specification](https://oraclous.atlassian.net/wiki/spaces/OP/pages/393501) defines what a Manifest _is_ on disk; [Structured Governance Taxonomy](https://oraclous.atlassian.net/wiki/spaces/OP/pages/688439) codifies the policy sets that the platform's governance model binds to; [Structured Threat Catalogue](https://oraclous.atlassian.net/wiki/spaces/OP/pages/983129) codifies the founding threats the substrate's isolation guarantees defend against.

When the two disagree, this section is authoritative for the concept; the artifact is authoritative for the implementation contract.

This is the platform's dictionary. Every term has a precise definition. When the same word means two things in different contexts, it is called out.

## Organisation

An organisation is the **outermost tenancy unit** of Oraclous — the boundary that separates one customer's deployment from any other. In self-hosted mode, a deployment typically contains one organisation (the customer's own company). In cloud-hosted mode, the same Oraclous-the-company-operated substrate hosts many organisations, each fully isolated from the others.

### Isolation guarantee

**Cross-organisation data flow is structurally impossible.** Every node, every relationship, every query, every cache entry, every audit log carries an `organization_id` in addition to any inner scope (workspace, graph, agent). No API can return data from another organisation. No Cypher query, however constructed, can traverse across the organisational boundary. The substrate enforces this at every layer — API, service, query, index, cache, audit.

This isolation is enforced **identically in both deployment modes**. Self-hosted deployments with a single organisation get the same enforcement as cloud-hosted deployments with many. The code is the same; the data path is the same; the guarantee is the same.

### What an organisation owns

* A set of **workspaces** (arranged in a hierarchy — see _Workspace_ below)
* A set of **members** (humans with credentials)
* A set of **LLM provider configurations** (organisation-level defaults that workspaces can inherit or override)
* A set of **policies** at the organisational level (budget ceilings, compliance posture, audit retention)
* A **billing relationship** (in cloud mode) or **usage metering** (in self-hosted mode) — see _Metering_ below

### Identification and creation

Organisations are created at deployment setup time. In self-hosted mode, the first organisation is the deployment's only organisation by default. In cloud mode, organisations are created during customer onboarding. In both modes, an organisation is a permanent, top-level entity that cannot be merged with or moved into another organisation — moving would breach the isolation guarantee.

---

## Workspace

A workspace is the **primary working unit** of Oraclous. It nests inside an organisation (workspaces are always organisation-scoped) and contains members, agents, tools, knowledge graphs, harnesses, task boards, and policies. **Members and agents are symmetric inhabitants** — both are actors that can be assigned work, hand off to each other, and operate under the workspace's governance.

### Nesting within organisations

Every workspace belongs to exactly one organisation. The organisation is the outermost tenancy boundary; workspaces are the inner working units. A workspace cannot exist without an organisation; an organisation can contain many workspaces.

### Hierarchy

Within an organisation, workspaces are arranged in a **hierarchy**: a parent workspace can contain child workspaces. The structure is a tree, not a flat namespace. Example: within the `acme-corp` organisation, the `Company` workspace contains `Tech`, `Marketing`, `Product` workspaces; within `Tech`, there are `Mobile`, `Frontend`, `Backend` workspaces.

**This hierarchy is always inside one organisation.** Cross-organisation workspace relationships do not exist. The `acme-corp` organisation's `Tech` workspace cannot have a parent or sibling relationship to another organisation's workspaces — that would breach the isolation guarantee.

### Isolation and connection

Workspaces can be **isolated** or **connected**. Two workspaces at the same level (e.g. `Tech` and `Marketing`) are typically isolated _from the perspective of their members_ — a Tech engineer cannot see Marketing's data. But isolation is enforced by ReBAC, not by physical separation: at the database level, all workspaces share the substrate, and a user or agent with sufficient permission (e.g. a CEO-level role, or a cross-org security role) can traverse from one workspace to another.

"Isolation" in Oraclous is **permission-scoped visibility**, not physical sharding. A CEO-rule agent operating across `Tech` and `Marketing` reads from the same substrate as Tech and Marketing members — but where they see one workspace, the agent sees both, connected.

### What a workspace owns

* A set of **members** (users) with roles
* A set of **agents** with roles and access scopes
* A **capability inventory** (tools, skills, sub-agents, harnesses, declared human roles)
* One or more **knowledge graphs**
* A set of **harnesses** (committed orchestration specs)
* One or more **task boards** (the operational state of running harnesses)
* A set of **policies** (budgets, HITL rules, escalation paths)

---

## Actor

An **actor** is any entity — human member or AI agent — that can be assigned work in a harness. Actors share a common interface from the harness's perspective: they have an identity, a scope, a capability allocation, and they can be:

* Assigned tasks
* Return results
* Hand off to another actor
* Escalate

The differences between humans and agents — humans being asynchronous, requiring notifications, having judgment outside the harness's specification; agents being synchronous or scheduled, instructable in prose, bounded by capability allocation — are runtime concerns, not model concerns.

This term is the **unifier**. When the manifest declares actors, it doesn't distinguish humans and agents structurally — only by kind. The harness plans for both the same way.

---

## Member

A member is a **human actor** belonging to one or more workspaces, with a role per workspace. Roles determine what a member can see, edit, and operate within that workspace. Membership in a parent workspace can imply elevated access to child workspaces — that is a workspace-policy decision, not a built-in rule.

From a harness's view, members are actors with specific capabilities (judgment, creative work, decisions requiring authority) that agents are typically not allocated. Members can be:

* Assigned tasks by harnesses
* Hand off to agents
* Escalate to other members
* Act as approvers in HITL gates

---

## Agent

An agent is a **non-human actor** that operates within one or more workspaces under a defined identity, role, and scope. An agent has:

* An **identity** — its own credential, distinct from any human's
* A **role** — prose description of what it is responsible for
* A **capability allocation** — which tools, skills, sub-agents, sub-harnesses it can invoke
* A **scope** — which workspaces, which data, which members' delegated permissions it can act under
* Optionally, a **sub-harness** governing its internal behaviour (recursive)
* A **consciousness record** — its experiential memory (see _Consciousness_ below)

Agents are not the LLM. The LLM is a _resource_ the agent uses; the agent is the persistent identity that owns role, scope, history, and policy.

---

## Capability

A capability is **anything an actor can invoke**. The unified concept that collapses today's scattered tool registries. Capabilities come in five kinds:

### Tools

Deterministic functions an actor calls with structured inputs — a Postgres reader, a Google Drive fetcher, a Cypher query. Closest to the existing `BaseToolExecutor` concept in the current codebase.

### Skills

Prose-defined behavioural modules an actor loads to handle a class of task — a _"respond to SOC2 compliance question"_ skill, a _"draft a cold outreach"_ skill. Closest to the Claude Code `SKILL.md` pattern. Skills don't execute; they _instruct_.

### Agents

Other agents invoked as sub-agents. A capability allocation can include another agent. This is how multi-agent topologies compose.

### Harnesses

A full harness invoked as a callable unit. A harness can be a capability in another harness, enabling hierarchical orchestration without rewriting topology.

### Human roles

A declared role a human member fills (e.g. _"brand lead"_, _"on-call SRE"_, _"legal reviewer"_). The compiler can route tasks to these roles; the runtime resolves the role to one or more actual members at execution time. Human roles are first-class capabilities — the symmetric counterpart to agents.

### What every capability carries

* A **structured schema** — input/output for runtime use
* A **natural-language description** — what it is good for, written for the compiler's LLM to reason about
* A **credential requirement** — what scopes it needs
* A **workspace scope** — which workspaces can see and use it

---

## Harness

A harness is a **workspace artifact describing how a goal gets done across humans and agents**. It is the central abstraction of the platform.

### What a harness contains

* A **goal statement** — the prose description of what the harness is for
* A **roster of actors** — humans and agents, declared symmetrically; each with a role, capability allocation, scope, and (for agents) optional sub-harness
* An **orchestration spec** — routing rules, hand-offs, escalation paths; mostly in prose, with structured edges where governance matters
* A **schedule and trigger spec** — when does this harness run (events, cron, manual, external triggers)
* A **task board reference** — the operational state this harness reads from and writes to
* A **policy envelope** — budget caps, HITL gates, output redaction rules; all coded constraints
* A **provenance link** — the substrate anchor where this harness's audit trail lives

### Routing across actor kinds

A harness can route any task to any actor. A hand-off from agent to human is structurally identical to a hand-off between two agents — the runtime handles the difference (notification vs. tool dispatch) under the hood.

A harness is stored in the **manifest format**, which is the platform's portable contract.

---

## Manifest

The manifest is the **serialised form of a harness**. It is what gets written to disk, committed to the substrate, published to external runtimes, and consumed from external runtimes. The manifest format is the open standard that gives the platform its portability.

### Two zones

* **Structured zone** — actors, capabilities, scopes, policies, schedules. Machine-validated. Governance lives here.
* **Prose zone** — role descriptions, orchestration rules, hand-off conditions, escalation criteria. Model-interpreted. Flexibility lives here.

### The governance principle

The runtime is the one that enforces the structured zone _regardless_ of what the prose says. This is the architectural principle that makes prose-defined orchestration safe: **governance never lives only in the prose.**

---

## Harness Compiler

The compiler is **the system that takes a goal and emits a manifest**. It is **not a platform layer** — it is a harness installed by default on every workspace, executing on the same runtime customers use for their own harnesses. The default compiler is a team of agents with appropriate tools, scopes, and prose orchestration. Customers can replace the default compiler with their own, or customise individual agents within it, using the same primitives they use to define any other harness.

This is the first concrete instance of the platform's recursion principle: **the compiler is a harness running on the platform, not part of the platform.**

### What the compiler does per request

1. Ingest the operator's goal in natural language
2. Survey the workspace's available capabilities under the operator's ReBAC scope
3. Optionally ask clarifying questions
4. Plan an actor topology — roles, hand-offs, schedules, including which steps go to humans vs. agents
5. Emit a draft manifest
6. Engage in review/edit dialog with the operator
7. Commit the manifest when approved

### Customisation

Because the compiler is itself a harness, customers can:

* Replace it entirely with a different compiler harness
* Modify individual agents within the default compiler team
* Add new capabilities to the compiler's allocation (e.g. domain-specific planning skills)
* Restrict its scopes or budgets via policy envelope

### Access

The compiler is accessible via UI, API, and MCP. It is never UI-locked.

---

## Harness Runtime

The runtime is **the system that executes a committed manifest**. It is the lifted-and-generalised descendant of today's `AgentExecutor`.

### What the runtime does

* Loads a harness from the substrate
* Resolves capability allocations via the registry
* Drives the orchestration — for each turn, decides which actor to invoke, dispatches tools or assigns tasks, feeds results back
* Manages working memory and conversation state
* Reads from and writes to the task board
* Enforces the policy envelope on every action (budget, HITL, scope)
* Traverses workspaces under delegated identity when needed
* Waits on human actors with the same primitives it uses to wait on tool returns
* Writes provenance and consciousness records back to the substrate

---

## Execution Engine

The execution engine is **the durable layer underneath the runtime**. It owns:

* Long-running jobs
* Retries
* Schedules
* Checkpoints
* Pause / resume

When a harness needs to run beyond a single request, when an agent wakes on a schedule, when a job must survive a process restart, the execution engine is the layer responsible.

The runtime delegates to the execution engine whenever execution must outlive a single in-memory request.

---

## Task Board

A task board is the **shared operational surface for humans and agents** in a workspace. Each harness reads tasks from and writes results back to its task board. Both human members and AI agents are **first-class assignees**: a task can be assigned to _"the brand lead"_ or _"the drafting agent"_ with equal standing.

### What task boards are

Task boards function as the **operational fabric of the organisation's second mind** — the place where work that used to live in heads, Slack messages, and scattered tools becomes a unified, queryable, governed substrate. A task board is closer to **Linear or Asana** than to a job queue — but with agents as first-class assignees and harnesses as first-class task generators.

### What task boards support

* **Assignment** to humans or agents (or human roles, resolved at runtime)
* **Status tracking** — proposed, claimed, in progress, blocked, done, escalated, cancelled
* **Hand-offs** — one actor passing a task to another
* **Dependencies** — this task waits on that one
* **Schedules** — recurring tasks that wake up agents or notify humans
* **Provenance** — full audit of who did what when, under what scope

### Where they live

Task boards live in the substrate, with full provenance and ReBAC enforcement. They are queryable artifacts, not opaque queues.

---

## Consciousness

Consciousness is **an agent's experiential memory** — the record of what it has tried, what worked, what failed, what patterns it has noticed in its own operation.

### What consciousness is not

* Not **working memory** (within a single task, lost after)
* Not the **workspace knowledge graph** (the operator's data, not the agent's experience)
* Not **conversation history** (verbatim transcripts, not learnings)

### What consciousness enables

An agent can record:

* _"The v2 API endpoint returns 410 — use v3 going forward"_
* _"This customer always asks about pricing first"_
* _"This audit pattern repeats — propose a tool"_
* _"Last time I tried this routing, the human reviewer rejected it for X reason"_

The substrate gives each agent a place to write these records; the runtime consults them before planning a turn.

### How consciousness is governed

An agent's access level determines whether it can:

* Record observations (most agents)
* Suggest new tools or routing changes (escalated)
* Propose harness modifications (requires HITL approval)
* Auto-create tools or modify its own harness (requires explicit operator grant)

This bounded learning is what makes consciousness safe — it is not unbounded self-modification, it is **bounded learning with HITL where required**.

---

## Delegated Identity

When an agent acts on behalf of a member (e.g. a CEO's agent reading a `Marketing` workspace), it does so under **delegated identity** — the agent's own identity, _plus_ a scope grant from the member explicitly authorising the action.

The substrate enforces both:

1. The agent must have its own permission
2. AND its delegated scope from the member must cover the action

This extends the OAuth scope model to internal agent-to-data and agent-to-agent permissions.

---

## ReBAC

**Relationship-Based Access Control.** Permissions are defined by _relationships_ between entities — not by static roles.

* A member's access to a workspace depends on their relationship to that workspace (member, admin, observer)
* An agent's access depends on its scope grant
* Cross-workspace traversal depends on the hierarchy relationship plus delegated scope

ReBAC is the substrate's enforcement model for everything access-related.

---

## Provenance

Provenance is the **audit trail of every action in the platform**. Every tool call, every retrieval, every actor invocation, every task assignment, every harness execution, every policy decision is recorded with:

* Who did it
* On whose behalf
* Against what data
* Under what scope
* With what result

Provenance is anchored in the substrate and is the spine that makes the platform auditable and the actors' actions reviewable.

---

## LLM Provider

An LLM provider is the **external service that supplies language model inference** to agents on the platform. Oraclous is fundamentally **BYOM (Bring Your Own Model provider)**: the platform never operates LLMs itself; it dispatches to providers the customer has configured. This is true in both self-hosted and cloud-hosted deployment modes — even cloud customers bring their own LLM credentials, which are stored in their organisation's credential broker, never in Oraclous-the-company's infrastructure.

### Supported providers (v1)

The platform commits to first-class support for three protocol shapes covering six provider categories:

* **Anthropic native** — direct integration with Anthropic's API
* **OpenAI-compatible** — covers OpenAI itself, OpenRouter, Azure OpenAI, and any self-hosted OpenAI-compatible endpoint (LM Studio, Ollama, vLLM, Together, Anyscale, Groq, etc.)
* **AWS Bedrock native** — for AWS-native customers using Bedrock-hosted models

Adding a new provider that fits one of these protocol shapes is a configuration concern, not a code change. Adding a provider with a new protocol shape (e.g., Google Gemini's native API) is a contained code change in the LLM client factory; it does not require architectural revision.

### Three-level resolution

The platform resolves which provider to use for any given LLM call via a three-level chain:

1. **Agent-level** — the agent's OHM declares a specific provider/model (rare; used when an agent has hard requirements)
2. **Workspace-level** — the workspace declares a default provider, used by all agents in the workspace unless they override
3. **Organisation-level** — the organisation declares the default, used by all workspaces unless they override

Within each level, configurations include the provider identifier, the model name, and a credential reference (which the credential broker resolves at invocation time). Customers control LLM choice at every level.

### Why this matters architecturally

BYOM is the architectural commitment to **portability of inference**. A customer running on OpenAI today can move to Anthropic tomorrow by changing organisation-level configuration. A workspace doing high-cost work can shift to a cheaper provider without changing any harness or agent code. The platform's value is the substrate, the runtime, and the orchestration — not the inference. Lock-in to a specific LLM vendor would compromise that value proposition.

---

## Metering

Metering is the **substrate-level tracking of resource consumption** per organisation and per workspace. Every action that consumes a meaningful resource — an LLM token consumed, a tool invocation completed, a storage write, a compute-time tick — produces a metering record.

### What metering captures

* **LLM tokens** — input and output tokens per provider, per model, per agent, per workspace, per organisation
* **Tool invocations** — counts and durations per capability
* **Storage** — bytes per workspace (graphs, task boards, chat history, consciousness records)
* **Execution time** — wall-clock time spent in runtime and execution engine per harness run
* **Cross-workspace traversals** — counts and bytes-read for federation operations

Metering records are stored in the substrate with the same isolation guarantees as any other data — `organization_id` and `workspace_id` on every record.

### What metering does NOT do

Metering captures _what was consumed_; it does not assign _prices_ or generate _invoices_. Pricing logic and invoice generation belong to the optional Billing Service (cloud mode only — see _Billing_ below). In self-hosted mode, the metering surface exposes usage metrics that customers can use for their own internal chargeback or analytics; the platform itself never charges money.

### Why metering is a substrate concern

Metering must work identically in both deployment modes. It must be tamper-evident. It must be impossible to bypass. These properties only hold if metering is enforced at the substrate level — written by the runtime and execution engine as a non-negotiable side effect of every metered operation. Moving metering up the stack would create paths for circumvention.

---

## Billing Relationship

A billing relationship is **cloud-hosted-only**: the contractual arrangement between an organisation and Oraclous-the-company for usage of the cloud-hosted platform. In self-hosted mode, billing is the customer's internal concern; the platform exposes metering data but does not generate invoices, charge cards, or hold payment information.

### What a billing relationship contains (cloud mode)

* Subscription tier or pricing model (per-workstation monthly, per-token, hybrid — TBD by product strategy)
* Payment method
* Invoice history
* Usage limits and overage policies
* Compliance documentation (the customer's signed agreements, applicable terms)

### How billing relates to metering

Metering produces usage data. Billing consumes metering data, applies pricing rules, and generates invoices. The metering surface is the platform's commitment; the billing service is a separable concern that operates against that surface in cloud mode only.

### Why billing is NOT a substrate concern

Billing is product strategy. Pricing models change; tiers evolve; promotions happen. Embedding billing in the substrate would make these changes architecturally disruptive. By keeping billing as a separable cloud-mode service that consumes metering, the platform can iterate on pricing without touching the substrate.

---

## Application

An application is **a product built on Oraclous** — a digital twin, a customer support system, a code auditor, an FTOps platform. Each application is composed of one or more harnesses plus a thin product surface (UI, external integrations, customer-facing logic).

**Applications are not part of the platform.** They are _the reason the platform exists._
