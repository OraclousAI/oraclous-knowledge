# Agent Consciousness for Development

This skill defines how every Oraclous development agent accumulates and applies knowledge across stories and sprints.

## What this skill does

The consciousness skill runs at two moments: at the end of every agent turn (per-agent), and on a scheduled sweep (team-wide). At each invocation it:

1. **Gathers** — recent actions, tool calls, outcomes, errors
2. **Detects** — patterns: repetitive failures, repetitive solutions, hand-off problems, recurring ambiguity, velocity anomalies
3. **Categorises** — observation, suggestion, proposed change, or escalation
4. **Permission-gates** — drops proposed action to the highest permission the agent actually holds
5. **Writes** — records in the appropriate substrate location

## Permission model

| Permission | Default for dev agents |
| --- | --- |
| `can_record_observations` | True for all agents |
| `can_suggest_improvements` | True for all agents |
| `can_propose_skill_changes` | True for all agents (draft requires tech-lead acceptance) |
| `can_propose_adr` | True for solution-architect, security-architect, tech-lead; False for others |
| `can_auto_apply_changes` | **False for every agent. No exceptions.** |

## Consultation on next turn

Before planning any turn, every agent reads its consciousness record for the last 10 entries and the team consciousness record for the last 5 entries marked relevant to its role.
