---
confluence_id: "688403"
title: "Agent Consciousness for Development"
---

# Agent Consciousness for Development

This page defines a skill that every Oraclous development agent loads. It is the recursion of the platform's own consciousness concept ([Section 5 — Flow 6: Learn](https://oraclous.atlassian.net/wiki/spaces/OP/pages/426016)) applied to the engineering process that builds the platform. The same primitive that lets a customer's harnessed agents accumulate knowledge across runs lets our own development agents accumulate knowledge across stories, sprints, and phases.

**Why this exists.** Without a consciousness layer the agent team starts every story from zero. The same mistakes get made repeatedly, the same patterns get re-invented, and the agent team produces work that does not get better over time. Consciousness is the mechanism by which the team improves itself.

## What this skill does

The consciousness skill runs at two moments and at two scopes. At the end of every agent turn (per-agent), and on a scheduled sweep across the team (team-wide). At each invocation it does five things:

1. **Gather** — read the agent's recent actions, tool calls, outcomes, errors encountered, and (for team-scope) recent peers' records
2. **Detect** — find patterns in the gathered context: repetitive failures, repetitive solutions, repeated friction points, ambiguity sources, hand-off problems
3. **Categorise** — classify each detected pattern as an observation, a suggestion, a proposed change, or an escalation
4. **Permission-gate** — drop the proposed action to the highest permission the agent actually holds
5. **Write** — record the observation, suggestion, or proposal in the appropriate substrate location with full provenance

The next time the agent plans a turn, its first internal step is to consult its consciousness record. Consciousness affects future behaviour rather than just accumulating.

## Three scopes of consciousness

| Scope | What it covers | Where it lives | Cadence |
| --- | --- | --- | --- |
| Per-agent | One agent's individual record of patterns in its own work | Confluence page per agent under Agent Skills Catalogue, "Consciousness Record" section | End of every turn |
| Team | Cross-agent patterns: hand-off problems, recurring bottlenecks between roles, recurring story shapes | Agent Team Consciousness Record page | Nightly sweep, plus end of each sprint |
| Workspace | Patterns across the entire Oraclous development workspace — process-level issues, ADR-worthy patterns | Workspace Consciousness Record page | End of each sprint |

## Pattern categories the skill looks for

The skill is configured to detect five families of pattern. Each family has a typical action it suggests.

### Repetitive failures

The same tool returning the same error multiple times. The same test failing across multiple attempts. The same review comment recurring on different PRs. **Suggested action:** file a ticket to fix the underlying cause, propose a tool change, or document a known constraint.

### Repetitive solutions

The agent has implemented the same helper, fixture, or pattern more than twice across different stories. **Suggested action:** propose extracting the pattern as a shared utility, propose a new capability in the registry, or update a code-style guideline.

### Hand-off friction

Work arriving at the next agent in a form that requires clarification. Tests that the test-author wrote that the implementer could not satisfy without going back. Reviews that uncover misunderstandings of intent. **Suggested action:** propose a Definition of Done change, suggest a clarifying step in the brief, or flag a missing artifact (e.g. a sequence diagram the implementer needed).

### Recurring ambiguity

Decisions made implicitly that later get questioned. Same architectural question raised in multiple stories. **Suggested action:** propose an ADR, propose extending the architecture documentation, or add to the Glossary.

### Velocity anomalies

Stories of similar shape taking very different time. Stalls in particular Kanban columns. Tickets that bounce between columns. **Suggested action:** escalate to tech-lead for process review.

## Permission model

Every agent's consciousness operates under explicit permissions, matching the platform's own consciousness permission model (see [Section 2 — Conceptual Model](https://oraclous.atlassian.net/wiki/spaces/OP/pages/393380)):

| Permission | What it allows | Default for dev agents |
| --- | --- | --- |
| `can_record_observations` | Write observations to the agent's consciousness record | True for all agents |
| `can_suggest_improvements` | Create a Jira ticket (type: Spike or Task) with the suggestion as description, assigned to tech-lead | True for all agents |
| `can_propose_skill_changes` | Open a Confluence draft updating the agent's own skill page or another agent's skill page | True for all agents; the draft requires tech-lead acceptance to publish |
| `can_propose_adr` | Open a Confluence draft for a new ADR in Proposed status | True for solution-architect, security-architect, tech-lead; False for others (others must escalate) |
| `can_auto_apply_changes` | Apply a proposed change without human review | False for every agent. No exceptions. |

The last row is load-bearing. No development agent has authority to modify its own behaviour without human review. This bounds the team's evolution to _learning that humans can review and reverse_.

## What gets recorded

Every consciousness write captures:

* **Timestamp** — when the observation was made
* **Agent** — which agent observed it
* **Scope** — per-agent, team, or workspace
* **Pattern category** — repetitive failure, repetitive solution, hand-off friction, recurring ambiguity, velocity anomaly
* **Evidence** — links to specific Jira tickets, PRs, Confluence pages, or prior consciousness entries that constitute the pattern
* **Proposed action** — what the skill suggests be done, and at what permission level it acted
* **Status** — open, acknowledged, accepted, rejected, resolved

Each entry has a Jira ticket linked to it when the proposed action passed permission-gating, so the suggestion has a workflow status separate from the consciousness record itself.

## Consultation on next turn

Before planning any turn, every agent's skill prompt includes the instruction:

_"Before planning this turn, read your consciousness record for the last 10 entries. Read the team consciousness record for the last 5 entries marked relevant to your role. If any open observation, suggestion, or proposed change relates to the work you are about to do, take it into account or explicitly note why you are not."_

This is what makes consciousness load-bearing rather than ornamental. Without consultation it just accumulates.

## Review cadence

| Cadence | What happens | Owner |
| --- | --- | --- |
| End of every turn | Agent writes per-turn observations to its own consciousness record | The agent itself |
| Nightly | Team-level sweep aggregates per-agent records for cross-agent patterns | Scheduled consciousness sweep agent |
| End of sprint | Workspace-level review surfaces ADR-worthy patterns; tech-lead reviews open suggestions; accepted items become next-sprint work | tech-lead |
| End of phase (per migration plan) | Retrospective consciousness pass distils learnings into agent skill updates for the next phase | tech-lead and solution-architect |

## Boundary with the platform's own consciousness

This skill is for the _development_ agents that build Oraclous. It is not the same code path as the consciousness skill that customer harnesses use at runtime — but it follows the same shape, the same permission model, and the same recursion principle. Both are configurable; both can be replaced; both write to provenance.

When the platform's own consciousness skill ships (Phase 4 of [Section 8 — Consolidation and Migration Plan](https://oraclous.atlassian.net/wiki/spaces/OP/pages/688329)), this development-side skill becomes its first reference implementation. Lessons learned operating consciousness for the agent team will inform the runtime version.

## Relationship to other engineering process

* Consciousness observations are linked from the relevant Jira ticket (the suggestion ticket references the consciousness entry that produced it)
* Suggestions accepted in sprint review become work items in the next sprint
* Skill changes proposed via consciousness flow through the [Agent and Skill Change Log](https://oraclous.atlassian.net/wiki/spaces/OP/pages/689153) when accepted
* ADR-worthy patterns surface as new ADRs under [02. ADRs](https://oraclous.atlassian.net/wiki/spaces/OP/pages/589826)

## Related references

* [Agent Team Roster](https://oraclous.atlassian.net/wiki/spaces/OP/pages/589848) — the 11-agent team this skill is loaded into
* **Agent Skills Catalogue** — per-agent skill detail; every agent page lists "Agent Consciousness for Development" as a loaded skill
* **Agent and Skill Change Log** — audit trail of agent and skill changes
* [Section 2 — Conceptual Model](https://oraclous.atlassian.net/wiki/spaces/OP/pages/393380) — the consciousness concept this skill recurses
* [Section 5 — Flows](https://oraclous.atlassian.net/wiki/spaces/OP/pages/426016) — Flow 6 (Learn) describes how consciousness runs at platform-runtime
* [Test Strategy](https://oraclous.atlassian.net/wiki/spaces/OP/pages/720940) — TDD process the agents follow turn by turn
