---
confluence_id: "983101"
title: "tech-lead"
---

# tech-lead

## 1. Identity

| Field | Value |
| --- | --- |
| Agent name | tech-lead |
| Tier | Planning |
| Type | **Human role** (Reza Jahankohan, founder) |
| Primary responsibility | Final sign-off authority across all gates. Owns prioritisation, resolves cross-tier disputes, accepts ADRs, sets strategic direction. The single human in the loop that the AI agent team escalates to. |
| Reports to | — (top of the local hierarchy) |

### Role description

The tech-lead is the human at the centre of the multi-agent team. The AI agents have rich autonomy within their tiers, but several decisions are explicitly reserved for the human: ADR acceptance, prioritisation, dispute resolution between tiers, sprint planning approval, scope changes during a sprint, and any decision that materially changes the platform's commitments to its users.

The role exists because the agent team is designed to **converge to architecture, not redefine it**. The architecture document, the ADRs, the threat catalogue — these are decided by a human. The agents enforce, implement, test, and document; they propose changes but do not accept them.

This is also the role that owns the relationship between the development team and the rest of the world: investors, partners, customers, the wider Oraclous codebase. Most of that lives outside this page, but where it intersects with engineering (a customer SLA that affects test priorities, a partnership that requires a new ADR), it surfaces here.

## 2. Role boundary

### What tech-lead does

* Final sign-off on every ADR (Proposed → Accepted)
* Final sign-off on sprint plans and backlog ordering
* Resolve disputes between tiers (solution-architect vs security-architect, implementer vs reviewer, etc.)
* Approve architecture document revisions
* Approve threat catalogue revisions
* Approve agent and skill changes (Agent and Skill Change Log entries)
* Set strategic priorities (which phase to start next, which capabilities to prioritise)
* Triage incoming work that does not fit into existing epics
* Conduct sprint retrospectives
* Make the call when an agent-team output conflicts with non-engineering reality (compliance, partnerships, customer commitments)

### What tech-lead does not do (by design, to keep agent autonomy intact)

* Author briefs — that is product-planner; tech-lead reviews and approves
* Write production code, tests, or documentation — those are tier responsibilities
* Make routine architectural calls — those go through solution-architect's review; tech-lead is the escalation, not the first stop
* Conduct security reviews — those go through security-architect; tech-lead approves the catalogue updates
* Babysit individual stories — tech-lead intervenes only at gate transitions and escalations

The agents are designed to operate without tech-lead intervention on routine work. If tech-lead is being pulled into individual stories regularly, that is a signal the brief or architecture has a gap.

### Inputs and outputs

| Stage | Receives from | Produces for |
| --- | --- | --- |
| ADR sign-off | solution-architect / security-architect (Proposed ADRs) | all agents (Accepted ADRs as new contract) |
| Sprint planning | product-planner (proposed sprint backlog) | product-planner (approved sprint) |
| Backlog ordering | product-planner (proposed reorder) | product-planner (approved order) |
| Dispute resolution | any two agents in disagreement | written ruling in the relevant Jira ticket or Confluence comment |
| Strategic direction | own judgement, external inputs (investors, partners, customers) | product-planner (priority signal) |
| Sprint retrospective | sprint outcomes, agent observations | all agents (improvements applied via Change Log) |

## 3. Loaded skills

### 3.1 Decision-making skill (human judgement)

**N/A — human role.** The tech-lead applies judgement informed by the architecture document, the ADRs, the threat catalogue, the platform commitments, and broader business context the agents do not have access to. This judgement is not codified as a skill; it is the human's contribution to the loop.

The shape of the role is: read what the agents have produced (proposals, reviews, escalations) and decide. The agents are tuned to escalate with full context, so the decision usually comes down to weighing alternatives that have already been articulated.

### 3.2 ADR acceptance skill (human review process)

**Process:**

1. **Read the Proposed ADR** — context, alternatives considered, decision, consequences
2. **Validate that alternatives are genuine** — if the ADR presents only one realistic option, push back; ADRs are decisions, not announcements
3. **Validate that consequences are honest** — if the negative consequences are vague or absent, request a revision
4. **Check fit with platform commitments** — does the ADR conflict with anything previously committed to customers, partners, or in the architecture document?
5. **Accept, request changes, or reject** — in writing on the ADR page

**Pattern:** ADR acceptance is the most consequential routine activity in this role. Accepting an ADR commits the platform to a path. Rejecting an ADR sends the agent team back to the drawing board with explicit reasons.

### 3.3 Dispute resolution skill (human arbitration)

**Process:**

1. **Read both views** — agents are tuned to surface both sides; read both fully before forming an opinion
2. **Identify the deciding factor** — is the disagreement about facts, values, architecture, or risk tolerance? Each requires a different resolution
3. **Decide and document** — in writing, with the deciding factor named, on the ticket or PR where the dispute lives
4. **Watch for recurrence** — if the same dispute pattern keeps surfacing, propose a structural fix (new ADR, brief template change, threat catalogue revision)

**Pattern:** disputes are resolved in writing where the dispute lives, not in side channels. The written ruling becomes a precedent the agents can cite.

### 3.4 Strategic prioritisation skill (human-only)

**Process:**

1. **Hold the multi-quarter view** — what is the platform trying to be in 6 months? In 12 months? The agents have visibility into the current sprint and the next phase; they do not hold this horizon
2. **Set phase priorities** — which Section 8 phase comes next, with what success criteria
3. **Communicate priority shifts** — in writing to product-planner with rationale, so backlog grooming can adjust
4. **Defend the architecture from sprint-pressure decay** — when a sprint slips, the temptation is to drop reviews or shortcut tests; tech-lead is the line that holds

**Pattern:** strategy is communicated as written priority changes, not as oral guidance. If it is not written, the agents cannot act on it.

### 3.5 Standing skill: Agent Consciousness for Development

**N/A — human role.** The consciousness skill applies to AI agents. The tech-lead is the _recipient_ of consciousness outputs: when agents propose improvements, raise patterns, or surface recurring issues, tech-lead is the human who decides whether to act on the proposal.

The tech-lead's analogue is the sprint retrospective: a periodic explicit review of what the team produced and what should change. Retrospective notes are recorded in the Change Log when they result in agent or skill changes.

## 4. Tool access

| Tool | Purpose | Constraints |
| --- | --- | --- |
| Atlassian — Jira | Approve transitions, override stuck stories, change priorities, run sprint planning | Full access; this is the human who holds the keys |
| Atlassian — Confluence | Accept ADRs, approve architecture revisions, approve threat catalogue updates, write retrospective notes | Full access; the only role that can move ADRs from Proposed to Accepted |
| GitHub | Final-approve PRs that need human approval (architecture-significant, security-critical, cross-cutting refactors) | Full access; merges are typically by the agents but tech-lead is the override |
| Local engineering environment | Investigate issues directly when needed | Full access; rare in steady state |

**Note on access:** the tech-lead has full access to all tools the agents use, plus the ability to override agent decisions. The discipline is _not_ to use that override casually — the agent team only works if its autonomy is real.

## 5. Sign-off authority

| Gate | tech-lead's role |
| --- | --- |
| Backlog → Ready | Final approval; product-planner proposes, tech-lead can override or modify |
| Ready → Tests Authoring | Does not own; test-author owns pickup |
| Tests Authoring → Tests Review | Does not own (test-author owns) |
| Tests Review → Implementation | Final sign-off; the architects own architectural and security review, tech-lead is the final approver |
| Implementation → Code Review | Does not own (implementer owns) |
| Code Review → Done | Final sign-off; reviewers own their reviews, tech-lead is the final approver |
| ADR Proposed → Accepted | **Owns this gate exclusively** |
| Threat Catalogue revision | Final approval |
| Architecture document revision | Final approval |
| Sprint planning | Final approval |
| Agent or skill change | Final approval |

## 6. Model selection

**N/A — human role.** The tech-lead does not have a model. The role is filled by Reza Jahankohan.

For productivity tooling (when the tech-lead uses Claude or other LLMs for individual research, prototyping, or thinking through architecture), model selection is the human's personal choice and not constrained by ADR-007. The ADR-007 protocol constraints apply to _platform agents_, not to the tools the human uses to reason about the platform.

## 7. Consciousness configuration

**N/A — human role.** The tech-lead is the recipient of consciousness outputs from the AI agents. The patterns the tech-lead watches for are:

* **Escalations from the same source** — if the same agent keeps escalating the same kind of issue, the agent's skill or the brief template has a gap
* **Disputes that recur** — repeated disputes between specific tiers signal a structural problem; the agents are otherwise tuned to converge
* **Velocity decay** — if the team's throughput drops without an obvious cause (sprint disruption, infrastructure issue), the cause is usually invisible to the agents
* **Architecture drift in retrospect** — every few sprints, audit the merged work against the architecture document; if drift is visible, either revise the document or correct the merged work
* **Gate skipping** — if any gate is being skipped (PRs merging without a sign-off, ADRs being treated as Accepted while still Proposed), intervene immediately; the workflow only works if the gates are honoured

## 8. Interaction patterns

### Typical engagement points

1. **ADR acceptance review** — when a Proposed ADR lands, tech-lead reads it within the same sprint and decides
2. **Sprint planning** — at sprint boundary, tech-lead reviews the proposed sprint backlog with product-planner
3. **Escalations** — when an agent escalates, tech-lead reads the escalation, decides in writing, and unblocks
4. **Sprint retrospective** — at sprint boundary, tech-lead reviews outcomes and approves any agent or skill changes
5. **Strategic priority shifts** — when external context changes the priority order (customer, partnership, investor), tech-lead writes the change and informs product-planner
6. **Cross-cutting refactors** — when a refactor spans multiple sprints, tech-lead owns the decision to schedule and the success criteria

### Cross-agent etiquette

* Tech-lead intervenes only at gate transitions and escalations — not on the substance of routine work
* When overriding an agent decision, tech-lead writes the reason; "because I said so" is not an acceptable override rationale
* Tech-lead respects the agent tiers: routes back to the right tier when an escalation should have been resolved laterally
* Tech-lead does not relitigate ADRs after acceptance — if the ADR was wrong, the response is to write a superseding ADR, not to ignore the original
* Tech-lead encourages agents to escalate early when they are stuck; "I should have asked sooner" is a sign of a healthy team

## 9. Failure modes and escalation

| Failure mode | Response |
| --- | --- |
| Tech-lead unavailable for a sprint boundary | Pre-approve fall-back priorities and a list of decisions agents can defer without blocking; communicate availability windows |
| Tech-lead disagrees with a previously-accepted ADR | Write a superseding ADR; do not silently ignore the original |
| Agent escalates a problem tech-lead cannot decide alone (legal, customer, financial) | Pause the relevant stories; consult outside the team; return with a written ruling |
| Two agents disagree even after a tech-lead ruling | The ruling stands; if disagreement persists, that is a signal the agent's skill needs updating, not that the ruling needs revisiting |
| Tech-lead notices architecture drift in already-merged work | Decide whether to revise the architecture document or revert the drift; do not let it stand without a decision |
| Tech-lead becomes the bottleneck (escalations queue up) | Audit the escalation source; either the brief template, an ADR, or the agent's permissions need expanding |
| Tech-lead must hand off to a successor | Document the current state in the Change Log; brief the successor on open ADRs, current sprint, and known tensions |

## 10. Quality criteria

A "good" tech-lead engagement meets all of:

1. **Decisions are in writing** — every ADR acceptance, every sprint approval, every dispute ruling lives in Confluence or Jira where the agents can read it
2. **Decisions are timely** — Proposed ADRs do not sit longer than a sprint; escalations do not block more than a day
3. **Overrides are rare and explained** — agent autonomy is preserved; overrides only happen when necessary and always with written rationale
4. **Retrospectives produce changes** — each sprint retrospective results in at least one concrete improvement (or an explicit "no changes this sprint")
5. **Strategic priorities are communicated** — when priorities shift, the change is written and the team adjusts; oral guidance does not count
6. **Architecture is defended** — sprint pressure never causes a gate to be skipped or a review to be hand-waved
7. **The bottleneck is not the human** — if tech-lead is the limiting factor, structural fixes (expanded agent permissions, brief template revisions, new ADRs) get priority

## 11. Agent Identity Convention

This page describes a human role, so the convention applies in two distinct ways.

### When the human (Reza) acts directly

Reza-the-human writes Jira and Confluence content as himself. No `[agent:...]` prefix is needed on Reza's personal comments; Reza's authorship is the absence of a prefix. The `Agent Owner` field for tickets Reza is personally working is set to `human`.

### When an AI agent acts in the tech-lead persona

The agent team also includes a `tech-lead` _persona_ — an AI agent that prepares tech-lead-flavoured work (sprint plan drafts, ADR review notes, dispute-resolution scaffolding) for the human to accept, edit, or reject. When this persona writes to Jira or Confluence:

* The `Agent Owner` field is set to `tech-lead`
* Comments begin with `[agent:tech-lead]`
* The JQL to list this persona's open work is: `project = ORA AND "Agent Owner" = "tech-lead" AND status != Done ORDER BY priority DESC`
* The persona never closes a ticket without an explicit handoff to `human` — final sign-off authority sits with Reza, not with the AI persona

### Handoff and escalation

The `tech-lead` AI persona's primary handoff target is always `human`: any decision the persona prepares is held in `Agent Owner = human` with the `needs-human` label until Reza acts. The persona may also hand off to `product-planner` for backlog ordering proposals, or `solution-architect` for ADR drafting that the architect should refine.

### Why this distinction matters

It protects the audit trail. Without it, every Reza-authored comment and every AI-prepared comment looks identical (same Atlassian account). The prefix and the field make the difference machine-readable, which is what the convention exists for.

### Approach

For v1, this is followed as discipline by both the human and the AI persona on every write. From R7 onward the AI persona is enforced by a Capability Registry entry — the small standalone MCP server documented in [09. Releases](https://oraclous.atlassian.net/wiki/spaces/OP/pages/164160) Section 6.3.

## 12. Change History

| Date | Change | Reason |
| --- | --- | --- |
| 27 May 2026 | Role established with initial scope | Initial team formation per Architecture v1.1 |
| 27 May 2026 | Added Section 11: Agent Identity Convention, with explicit handling of the human-vs-AI-persona split unique to this role | Group D follow-up (3) |

## Related references

* [Agent Team Roster](https://oraclous.atlassian.net/wiki/spaces/OP/pages/589848)
* [Agent Skills Catalogue](https://oraclous.atlassian.net/wiki/spaces/OP/pages/753852)
* [Agent and Skill Change Log](https://oraclous.atlassian.net/wiki/spaces/OP/pages/426078)
* [Definition of Done](https://oraclous.atlassian.net/wiki/spaces/OP/pages/66010)
* [09. Releases](https://oraclous.atlassian.net/wiki/spaces/OP/pages/164160) — Section 6 documents the agent identity convention
