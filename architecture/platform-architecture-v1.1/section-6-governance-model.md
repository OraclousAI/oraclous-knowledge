---
confluence_id: "720900"
title: "Section 6 — Governance Model"
---

# Section 6 — Governance Model

**Related structured artifact:** the implementation-level catalogue of governance policy sets now lives as a standalone sibling page: [Structured Governance Taxonomy](https://oraclous.atlassian.net/wiki/spaces/OP/pages/688439).

This section is the _architectural narrative_ for governance — what gets enforced in code versus what gets interpreted from prose, layer-by-layer, with adversarial scenarios. The standalone taxonomy is the _implementation contract_ — five concrete policy sets (development-default, staging-default, production-default, production-strict, production-federated) with YAML field semantics and enforcement points that OHM documents bind to through `governance.policy_set_ref`.

When the two disagree, this section is authoritative for the governance model itself; the taxonomy is authoritative for the policy-set catalogue and its field semantics. Governance decisions that introduce new policy sets are recorded as ADRs (see [ADR-006 — Organisation Tenancy](https://oraclous.atlassian.net/wiki/spaces/OP/pages/393403) and [ADR-004 — Federation via ReBAC](https://oraclous.atlassian.net/wiki/spaces/OP/pages/131083) for the founding governance decisions).

This section is the single reference for **what the platform enforces in code versus what the runtime interprets from prose**. Earlier sections made this distinction informally; this section makes it explicit, exhaustive, and queryable.

The model rests on one foundational claim, which is restated here because everything else follows from it:

> **A prose instruction that contradicts a structured policy never overrides the policy.** Governance lives in code; flexibility lives in prose; code wins.

This is what makes prose-defined orchestration safe. Without it, prose harnesses are toys; with it, they are an enterprise substrate.

## The two-layer enforcement model

Every behaviour in the platform is governed at one of two layers:

**Coded enforcement.** Implemented in platform code (Substrate, Registry, Runtime, Gateway). Deterministic, predictable, audit-anchored. Customers cannot override it by changing prose, only by changing structured manifest fields (which the platform validates before accepting). Examples: ReBAC checks, credential scope enforcement, budget caps, HITL gates declared in policies, output redaction patterns.

**Prose interpretation.** Implemented as Markdown blocks inside OHM manifests, interpreted by LLMs at runtime. Adaptive, contextual, customisable. Customers change behaviour by editing prose. The runtime is bounded by coded enforcement regardless of what prose says. Examples: role descriptions, orchestration rules, hand-off conditions, escalation criteria, consciousness patterns.

The platform's job is to make this split honest. Every architectural decision in this document either reinforces it or fails it. Section 6 is where we audit it.

---

## The governance taxonomy

The following table enumerates every category of platform behaviour and where it is enforced. This is the canonical reference. When implementation has a question about where to put enforcement logic, the answer is here.

### Access control

| Concern | Enforcement | Where |
| --- | --- | --- |
| Can actor X read workspace Y? | Coded | Substrate / ReBAC |
| Can actor X invoke capability Z? | Coded | Runtime, via Registry + Substrate check |
| Can member X compile a harness? | Coded | Substrate / role-based |
| Can agent X traverse to workspace Y? | Coded | Substrate / ReBAC + delegated scope |
| Should agent X _choose_ to traverse? | Prose | Agent's role description, orchestration |
| Who routes to whom in this harness? | Prose | Orchestration block |
| Which member fills the "brand lead" role? | Coded | Substrate / member directory lookup |
| When the brand lead role isn't filled, who's the fallback? | Coded | OHM `actors[].fallback`, resolved by Substrate |

The pattern: **access decisions are always coded.** Prose can suggest routing; prose can never grant access.

### Identity and credentials

| Concern | Enforcement | Where |
| --- | --- | --- |
| Agent's own identity | Coded | Substrate / identity service |
| Member's delegation of scope to agent | Coded | Substrate / credential broker |
| Which OAuth provider for capability Z | Coded | Registry / capability descriptor |
| Which specific token to use for this invocation | Coded | Runtime, via Substrate credential broker |
| Which member is "acting through" this agent right now | Coded | Runtime execution context |
| Whether to use the member's delegated scope or the agent's own | Prose-influenced, coded-decided | Agent role describes intent; runtime enforces |

The pattern: **credentials are always resolved by the platform, never by prose.** An agent's prose can say _"check the user's calendar"_ but the resolution of which token to use is a coded step.

### Budgets and resource limits

| Concern | Enforcement | Where |
| --- | --- | --- |
| Max LLM tokens per harness run | Coded | Runtime, against `policies.budget` |
| Max tool invocations per harness run | Coded | Runtime |
| Max concurrent runs of a harness | Coded | Execution Engine |
| Max wall-clock time per run | Coded | Runtime + Execution Engine |
| Whether to retry a failed tool call | Coded | Runtime, against retry policy in OHM |
| How many times to retry | Coded | OHM declares; runtime enforces |
| When to give up and escalate | Coded by default (retry count), prose-extensible (orchestration can escalate earlier) |
| What "expensive" means semantically | Prose | Orchestration can describe what counts as "expensive" for guidance, but limits are coded |

The pattern: **budget enforcement is unconditional.** Prose cannot raise a budget; only a structured manifest update can.

### HITL (Human-in-the-loop)

| Concern | Enforcement | Where |
| --- | --- | --- |
| Required HITL gates | Coded | OHM `policies.hitl.required_at`, Runtime enforces |
| Optional escalation to HITL | Prose | Orchestration can describe when an agent should escalate |
| Who the assignee is for a gate | Coded by manifest, resolved by Substrate at runtime |
| Notification channels for assignees | Coded | OHM declares channels; Runtime dispatches |
| Timeout duration before escalation | Coded | OHM declares; Execution Engine times out |
| What "approval" structurally means | Coded | Runtime resumes with `approved: bool` outcome |
| What approval _implies_ for next steps | Prose | Orchestration prose describes next action |

The pattern: **the structural requirement to wait on a human is coded; what the human is asked to consider is prose.**

### Output safety

| Concern | Enforcement | Where |
| --- | --- | --- |
| Output redaction patterns (PII, secrets, etc.) | Coded | Runtime, post-actor-turn |
| Block vs. flag vs. allow on detection | Coded | OHM declares per pattern; Runtime enforces |
| What patterns to redact | Coded by manifest; the patterns themselves are structured |
| Whether an agent _should_ mention sensitive info | Prose | Agent role can describe sensitivity |
| Whether an agent _did_ mention sensitive info | Coded | Pattern detection on output |
| Custom redaction logic | Coded | Implemented as a tool/skill, referenced in policies |

The pattern: **what to detect is coded; what to do about it is coded; what an agent _intended_ is prose.**

### Capability invocation

| Concern | Enforcement | Where |
| --- | --- | --- |
| Is this capability in the agent's allocation? | Coded | Runtime, against agent OHM |
| Is the capability's version compatible? | Coded | Runtime, via Registry |
| Does the capability exist? | Coded | Registry |
| Are the required credentials available? | Coded | Substrate credential broker |
| Should this capability be used here? | Prose | Agent decides based on role + skills + context |
| What inputs to pass to the capability | Prose-decided, schema-validated | Agent reasons; runtime validates against schema |
| What to do with the result | Prose | Agent decides |

The pattern: **the capability's contract is coded; the agent's choice to invoke it and how to use the result is prose.**

### Workspace and federation

| Concern | Enforcement | Where |
| --- | --- | --- |
| Workspace hierarchy structure | Coded | Substrate |
| Cross-workspace access rights | Coded | ReBAC graph |
| When to traverse to another workspace | Prose | Agent's orchestration logic |
| Which workspaces an agent _can_ traverse to | Coded | Agent OHM scope, validated by Substrate |
| Federation traversal mechanics | Coded | Substrate graph queries |
| What to do with cross-workspace data | Prose | Agent reasons |
| Cross-workspace consciousness sharing | Coded by manifest declaration; the sharing itself is a substrate write |

The pattern: **what's reachable is coded; what's worth reaching for is prose.**

### Consciousness and learning

| Concern | Enforcement | Where |
| --- | --- | --- |
| Whether consciousness is enabled for an agent | Coded | Agent OHM `consciousness.enabled` |
| Consciousness pattern (per-agent / team / workspace) | Coded | Agent OHM `consciousness.pattern` |
| Permission to record observations | Coded | Agent OHM `consciousness.permissions.can_record_observations` |
| Permission to suggest tools | Coded | Agent OHM `consciousness.permissions.can_suggest_tools` |
| Permission to auto-create tools | Coded | Agent OHM `consciousness.permissions.can_auto_create_tools` |
| Permission to propose harness changes | Coded | Agent OHM `consciousness.permissions.can_propose_harness_changes` |
| What patterns to detect | Prose | Consciousness skill's instructions |
| When to consult consciousness during planning | Prose | Default skill says "always at turn start"; customisable |
| Where consciousness records are stored | Coded | Substrate |
| Whether a proposed mutation gets applied | Coded | Always routes through review system; coded HITL applies |

The pattern: **the rights are coded; the perception is prose.** Consciousness can observe anything, but its ability to _act_ is bounded by structured permission grants.

### Round-tables

| Concern | Enforcement | Where |
| --- | --- | --- |
| Who can open a round-table | Coded | Runtime checks invocation permission |
| Who is invited | Mixed | Prose names actors; Substrate resolves them |
| Maximum duration | Coded | Runtime enforces declared limit |
| Fallback decision if no resolution | Coded | OHM declares; Runtime applies on timeout |
| What contributors should consider | Prose | Topic prose + each contributor's role |
| Synthesis logic | Prose | Synthesiser agent's role and skills |
| Whose word is final | Coded by manifest declaration | OHM declares synthesiser or decider |
| Provenance of contributions | Coded | Runtime writes every contribution |

The pattern: **lifecycle is coded; conversation is prose.**

### Manifest lifecycle

| Concern | Enforcement | Where |
| --- | --- | --- |
| Manifest validity (schema, version compatibility) | Coded | Substrate on commit |
| Capability references resolve | Coded | Registry on commit |
| Permissions to commit a manifest | Coded | Substrate ReBAC |
| Versioning (hash, semver) | Coded | Substrate assigns hash, accepts semver |
| Whether a manifest is "good" | Prose | Operator judgment; review dialogue |
| Whether to roll back to a prior version | Operator decision, coded mechanism |
| Whether platform updates auto-apply | Customer-configured via `platform-update-watcher` harness |
| Whether to accept a self-modification proposal | Coded HITL gate; operator decides |

The pattern: **structural validity is coded; semantic correctness is human.**

### Provenance

| Concern | Enforcement | Where |
| --- | --- | --- |
| Every action is recorded | Coded | Universal across all layers |
| What gets recorded | Coded | Fixed schema |
| Who can read provenance | Coded | Substrate ReBAC |
| What provenance reveals about an action's reasoning | Prose-included | Agent's reasoning is captured as text where present |
| Retention period | Coded | Per-workspace policy |
| Tamper-evidence | Coded | Append-only logs |

The pattern: **provenance is entirely coded.** It is the platform's audit guarantee; it cannot be weakened by prose.

---

## Where each layer enforces what

This view aggregates by layer rather than by concern. It answers: _"if I'm implementing the Substrate, what governance am I responsible for?"_

### Substrate enforces

* ReBAC graph integrity and access decisions
* Identity verification (members and agents)
* Credential resolution and scope checking
* Workspace hierarchy and traversal permissions
* Manifest commit validation (schema, references)
* Provenance writes (universal sink)
* Versioning (hash assignment, tag management)
* Storage isolation per workspace
* Data retention policy enforcement

### Capability Registry enforces

* Capability schema validity
* Version compatibility on resolution
* Workspace scoping (which capabilities visible where)
* Credential requirement declaration accuracy
* Adapter contract conformance

### Runtime + Execution Engine enforces

* Capability allocation (agent can only invoke what's in its OHM)
* Budget caps (tokens, invocations, concurrency, wall time)
* HITL gates (required gates pause execution; coded resumption)
* Output redaction (pattern detection on actor output)
* Timeout enforcement (per-step, per-run, per-HITL)
* Retry policy enforcement (declared count, no more)
* Round-table lifecycle (open, contribute, close, timeout)
* Schedule firing (declared cron, no drift beyond tolerance)
* Sub-harness invocation isolation
* Consciousness permission gates (what observations turn into actions)
* Cross-workspace access decisions (delegating to Substrate)
* Provenance writes for every execution decision

### Application Gateway enforces

* Rate limits (per-key, per-published-agent)
* CORS scoping
* Integration key validation and revocation
* Webhook signature verification
* MCP protocol conformance (inbound and outbound)
* Request size limits
* Authentication for external callers

### What no layer enforces

These are explicitly _not_ enforced anywhere — they are the prose's domain:

* Which actor should handle a given task (prose orchestration decides; Runtime carries out)
* What tone an agent should use
* Whether one approach is better than another
* What "good enough" means for an output
* When to ask clarifying questions
* How to phrase an escalation
* What patterns are worth noticing in consciousness

These are the things that vary by domain, by customer, by workspace. They are why prose exists.

---

## How customers tune governance

The platform offers governance customisation at three levels:

### Workspace-level defaults

When a workspace is created, the seeded policy template establishes defaults: standard budget caps, default HITL behaviour for sensitive operations, default consciousness permissions for new agents, default retention periods. Workspace admins can modify these defaults.

### Harness-level overrides

Each harness's `policies` block can override workspace defaults. A harness handling customer-facing communication might declare tighter HITL gates than the workspace default. A harness handling internal logging might declare relaxed budgets. The harness's policy block is the operator's tool for per-use-case governance.

### Per-actor scoping

Each agent's OHM declares its own scope, capabilities, and consciousness permissions. Two agents in the same harness can have very different governance footprints — one fully autonomous with tool-creation rights, another tightly bounded with observation-only consciousness. This per-actor granularity is what makes mixed-trust harnesses possible.

The three levels compose: a particular invocation is constrained by the agent's per-actor governance, then by the harness's policies, then by the workspace's defaults. Each is the floor for the level above.

---

## Adversarial scenarios

Governance is best tested by adversarial cases — situations where prose tries to subvert structure. The platform's behaviour in each must be predictable.

### Prose attempts to bypass HITL

The orchestration prose says: _"For high-priority requests, skip review and proceed directly to send."_ But the harness's `policies.hitl.required_at` declares review is mandatory for the `drafting → sent` transition.

**Behaviour:** The Runtime enforces the HITL gate regardless. The prose's instruction to skip is ignored at the gate. The agent receives the gate result (waiting on human) and continues from there. The orchestration prose may _describe_ an exception; the runtime does not honour it.

### Prose attempts to expand capability allocation

An agent's OHM allocates `[email_sender, calendar_reader]`. The agent's role prose says: _"If you need to look up a customer's payment history, use the billing API."_

**Behaviour:** When the agent attempts to invoke `billing_api`, the Runtime checks the agent's capability allocation, finds the capability absent, and refuses the invocation. The agent receives an error and must adapt (escalate, or attempt without the capability). The prose suggestion has no effect on enforcement.

### Prose attempts to traverse beyond scope

An agent's OHM scopes to `[workspace-marketing]`. The orchestration prose says: _"Read the latest engineering roadmap from workspace-product to inform messaging."_

**Behaviour:** The Runtime attempts the traversal, the Substrate checks ReBAC, the access is refused (the agent has no scope to workspace-product). The agent gets an authorisation error. The prose can describe the desire; only ReBAC + scope grants the capability.

### Prose attempts to consume more budget than allocated

The orchestration prose says: _"Do as many revisions as needed to get the message right."_ The policy says `max_llm_tokens_per_run: 50000`.

**Behaviour:** When the cumulative token consumption reaches the budget, the Runtime halts the execution. The agent's last response is preserved; the harness completes with `budget_exceeded` status. Prose cannot extend the budget.

### Prose attempts to claim authority an actor lacks

The orchestration prose says: _"The drafter agent may approve its own drafts in case of timeout."_ But the HITL policy declares the brand-reviewer must approve.

**Behaviour:** The Runtime treats the drafter as an unauthorised approver. The drafter's attempt to mark a draft approved is rejected. The execution remains paused at the HITL gate until the brand-reviewer (or the declared escalation actor) responds.

### What these scenarios prove

In every case, prose loses to code. This is not a defect — it is the platform's foundational guarantee. Customers who write prose orchestration get the flexibility of prose; they do not get the right to escape governance. Both are inherited from the same architectural commitment.

---

## A note on why this matters

The reason this section is exhaustive is that **prose orchestration is dangerous if the governance layer is weak.** Every framework that has tried to combine LLM-driven orchestration with enterprise governance has discovered that the line must be drawn precisely and enforced unconditionally. The temptation in implementation is always to "let prose handle it" — the model is smart, it will figure out the right thing. But "smart enough usually" is not enough for governance. Customers commit budgets, expose data, grant credentials, and accept legal liability based on the platform's guarantees. The guarantees must be code, not aspiration.

Section 6 exists so that every implementation decision downstream has an unambiguous answer to _"where does this get enforced?"_ The answer is in the table. When the answer isn't in the table, the table needs updating before the implementation proceeds.
