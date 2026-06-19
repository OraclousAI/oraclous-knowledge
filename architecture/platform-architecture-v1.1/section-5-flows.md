---
confluence_id: "426016"
title: "Section 5 — Flows"
---

# Section 5 — Flows

**Related structured artifacts:** when debugging a flow, the artifacts answer the "by what contract?" questions that the prose intentionally elides.

* **Flows 1, 2, 3, 8** manipulate OHM documents (compile emits OHM; execute and schedule load OHM; bootstrap-update diffs OHM versions). The field-by-field contract lives in [OHM v1.0 Standalone Specification](https://oraclous.atlassian.net/wiki/spaces/OP/pages/393501).
* **Flows 2 and 7** reference the policy envelope (budget enforcement in Step 8; HITL gates in `policies.hitl.required_at`). The concrete policy sets the substrate ships with — what counts as "production-strict" vs "staging-default", what each ceiling is, where it's enforced — live in [Structured Governance Taxonomy](https://oraclous.atlassian.net/wiki/spaces/OP/pages/688439).
* **Flow 4** (cross-workspace traversal) is the runtime projection of [ADR-004](https://oraclous.atlassian.net/wiki/spaces/OP/pages/131083) (federation via ReBAC). The threats it defends against — T1 (data exfiltration), T2 (privilege escalation) — and their required tests live in [Structured Threat Catalogue](https://oraclous.atlassian.net/wiki/spaces/OP/pages/983129).
* **Flow 6** (consciousness) is the runtime projection of the bounded-learning permissions discussed in [Section 6](https://oraclous.atlassian.net/wiki/spaces/OP/pages/720900). The OHM fields that gate it (`consciousness.permissions.*`) are specified in the OHM spec; the threat surface it must respect lives in the Threat Catalogue.

This section is authoritative for what each flow does; the artifacts are authoritative for the contracts each step must respect.

This section describes how Oraclous **behaves** end to end. The previous sections defined _what exists_; this section defines _what happens_.

Eight flows are covered:

1. **Compile flow** — operator goal → committed harness
2. **Execute flow** — committed harness → running work
3. **Schedule flow** — recurring agents waking on triggers
4. **Traversal flow** — cross-workspace federation under ReBAC
5. **Round-table flow** — synchronous multi-actor coordination
6. **Learn flow** — consciousness recording and consultation
7. **HITL flow** — human-in-the-loop assignment and resolution
8. **Bootstrap update flow** — platform-published defaults reaching a workspace

Each flow is described as a sequence of platform events. Internal naming is consistent with Sections 3 and 4 — Substrate, Registry, Runtime, Gateway, OHM, actor, capability, task board, etc.

A note on style: these flows are described at the level of _what the platform does_, not _how it does it in code_. Implementation details (database schemas, API signatures, in-memory representations) are deliberately omitted — those belong in implementation plans, not in architecture.

---

## Flow 1: Compile

**Trigger:** an operator (member with `harness.author` permission) initiates a compile.

**Goal:** turn a prose goal into a committed OHM harness manifest.

### The flow

**Step 1 — Operator states the goal.** The operator opens a compile session via the Gateway (UI, API, or MCP). They submit a prose goal, optionally with constraints: budget caps, preferred actors, schedule expectations, criticality.

**Step 2 — Gateway invokes the compiler harness.** The Gateway looks up the workspace's installed compiler harness (the default one shipped with the workspace, or a customer-installed replacement). It dispatches the compile request to the Runtime as a new harness execution.

**Step 3 — Compiler harness begins execution.** The Runtime loads the compiler harness manifest, resolves its capability allocations, and starts the orchestration. The compiler harness is a normal harness — there is no privileged code path. It executes on the same Runtime any other harness uses.

**Step 4 — Workspace survey.** The compiler's first internal action is to query the Capability Registry for what's available in this workspace, ReBAC-bounded by the operator's identity. It receives a list of capabilities (tools, skills, agents, sub-harnesses, declared human roles) the operator could legitimately use. Capabilities the operator can't see are omitted — the compiler cannot plan with what the operator doesn't have access to.

**Step 5 — Substrate survey.** The compiler queries the Substrate for relevant knowledge graphs, recent harnesses, existing task boards, and consciousness records. This gives the compiler context: what kind of work has been done here before, what patterns the workspace's agents have learned, what data is available to plan against.

**Step 6 — Clarifying questions (optional).** If the goal is underspecified, the compiler may engage the operator in dialogue. _"You mentioned 'cold outreach' — does this include re-engagement of dormant customers, or only first-touch prospects?"_ The dialogue happens through the Gateway's compile session. The operator answers; the compiler incorporates.

**Step 7 — Topology planning.** The compiler plans the actor topology: which agents, which human roles, what capability allocations each gets, what the orchestration looks like. This is where the compiler's own intelligence (its agents, their skills, their reasoning loops) does the heavy lifting. The plan is internal at this stage — not yet a manifest.

**Step 8 — Task board design.** The compiler proposes a task board structure suited to the goal. Simple goals get a simple board (todo / doing / done). Complex goals get richer boards with explicit transitions. This is part of the manifest the compiler is composing.

**Step 9 — Manifest emission.** The compiler emits a draft OHM document for the harness. It includes the goal (preserved verbatim from the operator), the actors, the task board, the orchestration prose, declared triggers, policies, cross-workspace declarations, and consciousness setup. The manifest is fully valid OHM at this point — but uncommitted.

**Step 10 — Review dialogue.** The operator reviews the draft. They can request changes in prose ("the drafter should not handle existing customers"), and the compiler revises the manifest. This is iterative; multiple rounds are normal.

**Step 11 — Commit.** When the operator approves, the manifest is written to the Substrate as a new harness artifact with a content hash and optional semver tag. The Substrate records provenance: who compiled it, from what goal, with what compiler version. The harness is now live.

**Step 12 — Trigger setup.** Triggers declared in the harness (schedules, webhooks) are registered with the Execution Engine. The harness is ready to run.

### What can go wrong

* **No matching capabilities.** The compiler may find that the workspace lacks the capabilities needed to fulfil the goal. It emits a draft that flags missing capabilities and proposes how to acquire them (install a capability pack, request access, create a tool).
* **ReBAC conflict.** The goal requires access the operator doesn't have. The compiler emits a manifest with explicit access requests the operator must obtain before commit can succeed.
* **Policy conflict.** The compiler may propose a topology that violates workspace-level policies (e.g. budget caps too high). The Substrate rejects the commit; the compiler revises.
* **Operator abandonment.** The session is abandoned without commit. The draft is preserved for a configurable retention period and can be resumed.

### Customisation

Customers can replace the entire compiler harness, modify individual agents within it, or extend it with domain-specific skills (e.g. _"the compiler should always propose a SOC2 review step for harnesses touching customer data"_). The compile flow itself does not change — only the compiler harness does. The Runtime is unaware of which compiler is in use.

---

## Flow 2: Execute

**Trigger:** a harness trigger fires (schedule, webhook, manual, external event).

**Goal:** run the harness end to end, dispatching to actors, until completion or escalation.

### The flow

**Step 1 — Trigger fires.** The Execution Engine receives a trigger event. It loads the relevant harness manifest from the Substrate and begins a new execution context.

**Step 2 — Capability resolution.** The Runtime resolves every actor reference and capability reference in the manifest against the Capability Registry. If any required capability is missing or its version is incompatible, the execution fails fast with a clear error in provenance. The runtime never proceeds with a partial resolution.

**Step 3 — Identity setup.** The Runtime establishes the execution context's identity: which member triggered it (if any), which agents are participating, what delegated scopes they have. Credentials are resolved lazily — fetched from the Substrate's credential broker when first needed by an actor.

**Step 4 — Initial dispatch.** The Runtime parses the orchestration prose to determine the entry point: which actor takes the first action. This decision is made by the Runtime giving an _orchestration agent_ (a built-in piece of the runtime, but itself reasoning over prose) the harness's orchestration block and asking _"given this trigger and current task board state, who acts first?"_

**Step 5 — Actor turn.** The chosen actor is dispatched. For an agent, the Runtime loads its role, loaded skills, capability allocation, and current consciousness records, then begins its tool-use loop. For a human, the Runtime creates a task on the task board with appropriate assignment, sends notifications via declared channels, and pauses execution awaiting completion.

**Step 6 — Tool dispatch (for agent actors).** Within an agent's turn, every tool invocation goes through the same path: the Runtime validates the tool is in the agent's capability allocation, resolves credentials if needed, dispatches the tool, captures the result, writes provenance. The agent receives the result and decides its next action.

**Step 7 — Hand-off.** When an actor completes its turn (or stalls awaiting another actor), the orchestration agent decides where the work flows next. The decision is made by reading the orchestration prose, the current task board state, and the result of the just-completed turn. The decision is logged with reasoning.

**Step 8 — Policy enforcement.** Every action — tool call, hand-off, escalation, task assignment — passes through the policy envelope. Budget consumed is tracked against the manifest's `policies.budget` limits. HITL gates check whether the upcoming transition requires human approval. Output redaction patterns are applied. Any policy violation halts the execution and surfaces the issue.

**Step 9 — Iteration.** Steps 5–8 repeat until one of: the goal is achieved (orchestration agent declares completion based on the prose's success criteria), the harness escalates beyond its scope, a policy is violated, or budget is exhausted.

**Step 10 — Provenance closure.** When execution ends — success, failure, or escalation — the Runtime writes a final provenance record summarising the run: actors invoked, capabilities used, tasks created/completed, credentials accessed, policies enforced, outcome. The Substrate now has a complete audit trail.

**Step 11 — Consciousness write.** Before the execution context is destroyed, each actor that has consciousness enabled gets an opportunity to write to its consciousness record. The default consciousness skill examines the run for repetitive failures, repetitive patterns, or notable events. The actor's permissions determine whether observations are recorded, suggestions escalated, or tool creation proposed.

### Synchronous vs. durable

Some executions run inside a single request (a chat-like interaction, a quick automation). These complete synchronously: trigger → run → result, all in one HTTP context.

Others span hours or days, with humans assigned tasks, external integrations awaited, schedules waking agents. These run **durably** — the Execution Engine persists state between activations, resumes from checkpoints, and survives process restarts. The same Runtime serves both; the trigger and the harness's declared characteristics decide the mode.

### Pause, resume, cancel

Durable executions support explicit pause, resume, and cancel operations, exposed through the Gateway. Pausing freezes the execution context; resumption picks up at the last checkpoint. Cancellation is final: provenance is closed with the cancel reason, in-flight tasks are marked cancelled, in-flight tool calls are best-effort aborted.

---

## Flow 3: Schedule

**Trigger:** a cron expression or recurring event declared in a harness's `triggers` block.

**Goal:** wake an agent or harness at the right moment, run its scheduled work, and sleep again until the next interval.

### The flow

**Step 1 — Schedule registration.** When a harness is committed (Flow 1, Step 12), each schedule trigger is registered with the Execution Engine. The engine maintains a persistent schedule table: which harness, which trigger, next fire time, schedule definition.

**Step 2 — Wake-up.** The Execution Engine fires the trigger at the scheduled time. It creates a new execution context, just like any other trigger source. The Runtime loads the harness and begins.

**Step 3 — Scheduled-specific entry.** A scheduled wake-up usually has a specific entry action declared in the trigger (`action: check_backlog`, for example). The orchestration agent uses this action as the starting context: _"this is a scheduled wake-up, the declared action is 'check_backlog' — what should happen first?"_

**Step 4 — Task board consultation.** Scheduled agents typically begin by reading the task board: what's open, what's stalled, what needs attention. The agent picks up work according to the orchestration prose.

**Step 5 — Consciousness consultation.** Before planning the wake-up's work, the agent consults its consciousness record. _"What did I try last wake-up? What failed? What patterns am I tracking?"_ This is what makes recurring agents accumulate knowledge across wake-ups rather than restarting from zero.

**Step 6 — Execution.** The agent's work proceeds as Flow 2, Steps 5–10.

**Step 7 — Sleep.** When the agent has done its wake-up's worth of work (defined by the orchestration prose, or by hitting budget limits, or by clearing the task board), the execution context closes. The Execution Engine schedules the next wake-up according to the trigger's cron expression.

### Why scheduled agents are special

Scheduled agents are the closest Oraclous gets to _autonomous_ agents. They wake without human prompting, plan based on accumulated state, act, and sleep. This makes consciousness load-bearing: a scheduled agent without consciousness restarts from zero each wake-up, losing all context about what it has tried and what has worked. The default consciousness skill is specifically designed for this case.

### Heartbeat semantics

The "heartbeat agent" pattern — agents that wake on a regular interval to check state and act if needed — is implemented as a scheduled harness with a frequent cron (every few minutes, every hour) and a short orchestration prose ("on wake, read the board, do up to N actions, sleep"). Nothing in the platform special-cases heartbeat agents; they are just a particular shape of scheduled harness.

---

## Flow 4: Traversal (Cross-Workspace Federation)

**Trigger:** an actor in one workspace needs to read or act in another workspace.

**Goal:** allow the traversal if ReBAC permits; reject otherwise; preserve provenance across the boundary.

### Federation as the default pattern

The platform's default cross-workspace pattern is **federation**, not replication. A single agent operating across multiple workspaces is _one_ agent with the right to traverse, not multiple copies of the agent each living locally in each workspace. This decision was made explicit in Section 3 and is reflected in OHM's `cross_workspace` block.

### The flow

**Step 1 — Traversal intent.** An agent in `workspace-A` needs to access a knowledge graph, capability, or task board in `workspace-B`. The intent is expressed as a normal operation — the agent invokes a tool or query as it would within its home workspace.

**Step 2 — Access decision.** Before the operation proceeds, the Substrate's access decision API is called: _"can this actor, acting under this delegated identity, perform this action against this resource in this workspace?"_ The Substrate evaluates the actor's identity, its delegated scope, the workspace hierarchy, and the ReBAC graph.

**Step 3a — Access granted.** If the relationship permits — the actor's identity has direct ReBAC permission, OR the actor has delegated scope from a member who has permission — the Substrate returns an effective access grant. The Runtime proceeds with the operation, scoped to `workspace-B`'s data.

**Step 3b — Access denied.** If no relationship grants the access, the Substrate refuses. The operation fails with a clear authorisation error. The agent receives the error and decides how to handle it — typically by escalating to a human or by recording the missed access in consciousness.

**Step 4 — Cross-workspace operation.** When granted, the operation executes against `workspace-B`'s state. The agent might read entities from `workspace-B`'s knowledge graph, invoke a capability registered in `workspace-B`, or write a task to a `workspace-B` task board.

**Step 5 — Provenance across boundaries.** The provenance record explicitly captures the cross-workspace action: which actor, from which workspace, accessing which workspace, under what delegated scope, with what result. The audit trail is queryable from either workspace's side, subject to ReBAC.

**Step 6 — Consciousness implications.** If the agent's consciousness is at a team or workspace level, cross-workspace traversals are recorded there. This matters for patterns: a CEO-level agent that frequently needs Tech data alongside Marketing data may surface the pattern as a suggestion to formalise the cross-workspace relationship.

### Hierarchical traversal

A child workspace's parent has _potentially_ elevated access — but only when the workspace policy declares it. The platform does not assume parent workspaces have access to children. Each cross-workspace relationship is declared in the ReBAC graph; the hierarchy is a structural property, not an automatic permission.

The CEO scenario from earlier conversations works like this: the CEO's workspace is declared as a parent of (or peer with cross-cutting permissions over) `Tech` and `Marketing`. The ReBAC graph encodes this. A CEO-rule agent declares its scope in the manifest as `workspaces: [ceo-workspace, tech, marketing]`. When the agent runs, the Substrate validates each cross-workspace access against the relationship graph. If the CEO-workspace-to-Tech relationship exists, the access succeeds.

### Why this is not a special protocol

Federation traversal is not a special runtime mode. It is the same access decision and the same provenance write as any in-workspace action — just with the scoping workspace differing between actor and resource. The platform's graph-native substrate means cross-workspace queries are graph traversals with ReBAC predicates, not RPC calls between isolated services.

This is exactly the model your earlier instinct pointed to: the substrate is one graph; isolation is permission-scoped visibility; federation emerges from permission grants, not from federation infrastructure.

---

## Flow 5: Round-Table

**Trigger:** an actor declares (via the runtime API) that a round-table is needed to resolve a question, alignment issue, or conflict.

**Goal:** open a short-lived, multi-actor conversation, collect contributions, produce a decision or alignment, record provenance.

### Round-table as a runtime primitive

Round-tables are a Runtime primitive. The Runtime owns: lifecycle (open, contribute, close), invitation, participation enforcement, decision capture, provenance. Harnesses invoke round-tables through standard capability invocations (`open_round_table`, `contribute_to_round_table`, `close_round_table`) which the Runtime exposes.

This means round-tables are first-class — but composable. An agent or human can initiate one. A harness can declare _"open a round-table whenever the orchestration prose says so."_

### The flow

**Step 1 — Open.** An actor (agent or human) invokes `open_round_table` with: a question or topic, a list of invited actors, a maximum duration, an optional fallback decision if no resolution is reached.

**Step 2 — Invitations.** The Runtime sends invitations to each invited actor. Agents are notified through their normal dispatch mechanism — they may join immediately (if available) or queue the invitation. Humans are notified through their preferred channel (task board mention, email, push).

**Step 3 — Conversation.** Each invited actor contributes when they can. Contributions are turn-based — the Runtime maintains a queue, gives each contributor their turn, and aggregates the conversation. Agents read prior contributions before adding their own. Humans see the conversation in a chat-like UI.

**Step 4 — Synthesis (optional).** Some round-tables include a designated synthesiser — an agent whose role is to summarise contributions, identify alignment, propose a decision. The synthesiser is invited like any other actor but flagged as such; their final contribution is the proposed decision.

**Step 5 — Decision capture.** The round-table closes when: the synthesiser proposes a decision and others confirm, OR a designated decider declares the decision, OR the maximum duration expires (and the fallback decision applies). The decision is structured: a clear outcome, the reasoning, the actors who participated, and any dissents.

**Step 6 — Outcome distribution.** The decision is written back to whatever invoked the round-table. If a harness's orchestration prose says _"open a round-table to resolve conflict, then proceed based on the decision"_, the orchestration resumes with the decision as input.

**Step 7 — Provenance.** The full round-table conversation, decision, and participation are recorded in the Substrate. Round-tables are searchable artifacts — _"why did we decide to ship feature X last month?"_ can be answered by querying past round-tables.

### When round-tables are used

The orchestration prose decides when to open one. Typical triggers:

* An agent and a human disagree more than N times
* An agent encounters ambiguity beyond its consciousness's resolution
* A harness reaches a decision point requiring input from actors outside its normal flow
* An escalation explicitly requests cross-functional input

### Round-tables vs. task boards

The distinction matters: a **task** is asynchronous work to be done. A **round-table** is synchronous (or near-synchronous) alignment. Tasks go on the board; round-tables sit alongside it. An action item from a round-table may produce new tasks — but the round-table itself is a conversation, not a task.

---

## Flow 6: Learn (Consciousness)

**Trigger:** an actor completes a turn, or a scheduled consciousness sweep runs.

**Goal:** record what was observed, identify patterns worth surfacing, propose actions if permitted.

### Consciousness as skill-loaded behaviour

Consciousness is not a Runtime primitive — it's a skill (or a specialised agent) configured on each actor. The Runtime's only consciousness-specific behaviour is: invoking the consciousness skill at the right moments, passing it the actor's recent state, and routing its outputs (observations, suggestions, proposed mutations) according to the actor's declared permissions.

### The flow

**Step 1 — Trigger.** Consciousness runs at two points: at the end of each actor turn, and on a workspace-level schedule (e.g. nightly sweep for cross-actor patterns). The default skill described in OHM examples runs at end-of-turn.

**Step 2 — Context gathering.** The consciousness skill receives: the actor's recent actions, tool calls and their outcomes, errors encountered, the actor's existing consciousness record, and (for team/workspace consciousness) recent peers' records.

**Step 3 — Pattern detection.** The skill examines the input for the patterns declared in its prose: repetitive failures (same tool, same error, multiple times), repetitive code or script implementations (the agent keeps writing the same helper), repetitive task patterns across teams (the same kind of task recurs across harnesses), or other patterns the skill is configured to detect.

**Step 4 — Categorisation.** Detected patterns are categorised by what action they might warrant: a passive observation, a suggestion to humans, a proposed tool creation, a proposed harness modification, an escalation.

**Step 5 — Permission gate.** Each proposed action is checked against the actor's consciousness permissions (declared in the agent OHM):

* `can_record_observations: true` → the observation is written to the consciousness record
* `can_suggest_tools: true` → the suggestion is escalated as a task to humans
* `can_auto_create_tools: true` → the tool is drafted and submitted to the Capability Registry with `pending_approval` status
* `can_propose_harness_changes: true` → a mutation proposal is queued in the harness review system

Anything the actor lacks permission for is downgraded to the highest-permitted action. _Suggest_ a tool the actor isn't allowed to _create_.

**Step 6 — Write.** The observation, suggestion, or proposal is written to the appropriate substrate location — the actor's consciousness record, the workspace's task board, the Capability Registry, or the harness review queue. Provenance is recorded.

**Step 7 — Consultation on next turn.** When the actor next plans a turn, its first internal step is to consult its consciousness record. The default skill's prose includes the instruction _"before planning a turn, check your consciousness record for relevant prior observations."_ This is what makes consciousness affect future behaviour rather than just accumulating.

### Per-agent, team, and workspace consciousness

The same flow runs at three scopes:

* **Per-agent** — the agent's individual record, scoped to its own actions
* **Team** — a shared record across agents in the same harness or team, capturing patterns no single agent could see
* **Workspace** — a record across all agents in the workspace, used for cross-harness pattern detection (e.g. "this kind of customer always pushes back on pricing")

Each scope has its own consciousness skill (the same default by default; customisable per scope). Workspace-level consciousness usually runs as a specialised agent on a schedule rather than as a per-turn skill.

### Why consciousness is bounded learning, not unbounded self-modification

The permission gates are load-bearing. An agent that can record observations cannot automatically modify its own harness. An agent that can suggest tools cannot create them without human approval. An agent with full self-modification rights is rare and requires explicit operator grant. This bounds the platform's behaviour to _learning that humans can review and reverse_. It is not autonomy; it is augmentation with audit.

---

## Flow 7: HITL (Human-In-The-Loop)

**Trigger:** an orchestration step reaches a `policies.hitl.required_at` transition, or an actor explicitly escalates.

**Goal:** assign a task to a human, notify them, wait for their response, route the resolution back into the execution.

### HITL as task-board-native

There is no separate HITL subsystem. HITL is task assignment to a human, with notification dispatch. The Runtime treats waiting on a human like waiting on a tool return — same primitives, different latency expectations and timeout semantics.

### The flow

**Step 1 — Gate triggered.** The Runtime is about to execute a transition that the harness's `policies.hitl.required_at` declares requires human approval. Execution pauses at this point.

**Step 2 — Assignee resolution.** The Runtime resolves the assignee declared in the policy. If it's a specific actor id from the harness's actor roster, that's the assignee. If it's a role (like `brand_lead`), the Runtime resolves the role against the workspace's member directory. If no member matches, fallbacks apply (workspace default assignee).

**Step 3 — Task creation.** The Runtime creates a task on the harness's task board, with: the assignee, the question or approval requested, the context (relevant artifact, prior orchestration state), expected response shape (approve/reject/modify, or freeform), and a timeout.

**Step 4 — Notification dispatch.** The Runtime dispatches notifications through the policy's declared `notification_channels`. Default is task board (which the assignee sees in their workspace UI). Additional channels (email, Telegram, PagerDuty, Slack) are dispatched in parallel. Each notification includes a direct link to the task.

**Step 5 — Pause and persist.** The execution context is persisted to the Execution Engine. The Runtime is now idle on this execution — it will be resumed when the human acts.

**Step 6 — Human acts.** The human reviews the task. They can: approve (execution resumes with approved=true), reject (execution resumes with approved=false and the rejection reason), or modify (execution resumes with the modified artifact). Their action is captured on the task board with provenance.

**Step 7 — Timeout escalation.** If the human does not act within the declared timeout (`escalation_after_hours`), the Runtime triggers the escalation: typically a notification through the declared escalation channel (PagerDuty, on-call rotation), with optional escalation to a different assignee.

**Step 8 — Resumption.** When the human acts (or the escalation is resolved), the execution resumes. The orchestration agent reads the human's response and decides next action: proceed with approved transition, route back for revision, branch into an alternative path.

### Why HITL is just task assignment

This design has a key property: **the Runtime treats human and agent actors symmetrically**. A pause for HITL is a pause for an actor turn. The actor happens to be human; the latency is hours not seconds; the notification mechanism differs. But the orchestration logic is identical to "wait for the drafter agent to finish drafting." The symmetry from Section 2 (actors as a unified concept) makes this work without special-casing.

### Configurable assertiveness

Different harnesses need different HITL behaviour. A high-stakes harness (legal review, customer-facing communication) declares aggressive HITL gates with short timeouts and high-priority escalation channels. A low-stakes harness (internal note generation) declares no HITL gates or only on critical transitions. The OHM `policies.hitl` block expresses this declaratively; the Runtime enforces what's declared.

---

## Flow 8: Bootstrap Update

**Trigger:** Oraclous publishes a new version of a default seed artifact (compiler harness, consciousness skill, default capability, policy template).

**Goal:** notify each workspace, present the change, let the customer accept, merge, or ignore.

### The flow

**Step 1 — Platform publishes.** The Oraclous reference catalog publishes a new version of a default artifact. The artifact has a content hash and semver tag (e.g. `default-compiler@2.1.0`).

**Step 2 — Workspace notification.** Each workspace using the prior version is notified through the Gateway. The notification includes: the change summary, a diff against the customer's current version, the reasoning (improvements, security fixes, behavioural changes), and a link to review.

**Step 3 — Customer review.** A workspace admin opens the review. They see the diff in OHM, can read prose changes, can compare structured fields. They can:

* **Accept** the new version (overwrites the workspace's current version; the old version is retained for rollback for a configurable window)
* **Merge selectively** (cherry-pick specific changes; the customer's local customisations are preserved)
* **Reject** the update (the workspace's current version remains, and the notification is dismissed)

**Step 4 — Optional automation.** If the workspace has installed a `platform-update-watcher` harness, that harness reads the notification, applies the customer's configured policy (e.g. "auto-accept non-breaking changes to consciousness skills, prompt on compiler changes"), and acts on the customer's behalf — itself going through HITL where the policy requires.

**Step 5 — Apply.** Accepted updates are committed as new versions of the workspace's artifact. The new version becomes active for future executions. In-flight executions continue with their pinned version (content hash) and complete normally.

**Step 6 — Rollback availability.** For a configurable window (default 30 days), the prior version is retained. Customers can roll back if they discover problems. After the window, the prior version is archived or pruned per the workspace's retention policy.

### Why this preserves sovereignty

The platform never modifies a workspace's state without explicit consent. Defaults are proposed, never imposed. The customer owns every artifact in their workspace from the moment of creation. Even the _update mechanism_ is itself customisable — the `platform-update-watcher` is a harness the customer can replace, restrict, or remove entirely.

This is the same recursion principle that governs the rest of the platform: there is no platform-layer magic that customers cannot reach.

---

## Cross-flow concerns

A few concerns affect every flow and deserve explicit treatment:

### Provenance is universal

Every flow writes to the same provenance spine. A single harness execution produces provenance entries from: the trigger (Flow 2 Step 1), each actor turn (Flow 2 Step 5–7), each capability resolution (Flow 2 Step 2), each cross-workspace access (Flow 4 Steps 3–5), each round-table contribution (Flow 5), each consciousness write (Flow 6), each HITL gate (Flow 7), and the platform updates that shaped the harness's version (Flow 8). The full execution trail is queryable by any actor with appropriate ReBAC access to the substrate.

### Failures cascade gracefully

Every flow has explicit failure modes. The principle across all of them: **fail loudly, fail with provenance, fail in a way the operator can debug.** No silent recoveries, no hidden retries beyond the policy-declared retry counts, no "the system did something but we're not sure what."

### State lives in the substrate

No flow holds important state in memory beyond a single request. Round-tables, scheduled wake-ups, paused HITL executions — all are persisted to the substrate. Process restarts, deployments, infrastructure changes do not lose work in progress.

### Customisation does not change flows

Customers can replace the compiler harness, the consciousness skill, the platform-update-watcher harness. They cannot change the flows themselves — the sequence of platform events that defines compile, execute, schedule, traverse, round-table, learn, HITL, and bootstrap update. The flows are platform code; the artifacts that participate in them are customer harnesses.
