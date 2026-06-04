---
confluence_id: "753852"
title: "Agent Skills Catalogue"
---

# Agent Skills Catalogue

The per-agent skill pages for the Oraclous development team. Each child page documents one agent in full: identity, role boundary, loaded skills with detailed prose, tool access, sign-off authority, model selection, consciousness configuration, and change history.

This catalogue is the source of truth for what each agent does, how it does it, and what it is and is not allowed to touch. The [Agent Team Roster](https://oraclous.atlassian.net/wiki/spaces/OP/pages/589848) describes the team at a glance; this catalogue is where the actual contract for each agent lives. Which session each agent runs in is recorded in [Session topology and persona residency](https://oraclous.atlassian.net/wiki/spaces/OP/pages/1736705).

## Why per-agent pages and not one big roster

The Agent Team Roster gives the bird's-eye view: who's on the team, what tiers exist, how a story flows. It is intentionally short because at-a-glance is its job.

Each agent's _skill_ definition is much longer: the loaded skills section alone is several paragraphs per skill, with explicit pattern descriptions, permission settings, and example invocations. Cramming all of those into one page would make the roster unusable. So each agent gets its own page here, and the roster links into the catalogue.

This also lets the [Agent and Skill Change Log](https://oraclous.atlassian.net/wiki/spaces/OP/pages/426078) reference specific agents by URL when changes happen.

## Agent index

The team is 11 full agents plus one narrow verification persona (`be-test-reviewer`). The "Session" column records where each runs; see [Session topology and persona residency](https://oraclous.atlassian.net/wiki/spaces/OP/pages/1736705) for the full rationale.

| Tier | Agent | Session | Status |
| --- | --- | --- | --- |
| Architecture | [solution-architect](https://oraclous.atlassian.net/wiki/spaces/OP/pages/164068) | Coordinator | <custom data-type="status" data-id="id-0">Skill page current</custom> |
| Architecture | [security-architect](https://oraclous.atlassian.net/wiki/spaces/OP/pages/557195) | Coordinator | <custom data-type="status" data-id="id-1">Skill page current</custom> |
| Planning | [product-planner](https://oraclous.atlassian.net/wiki/spaces/OP/pages/884840) | Coordinator | <custom data-type="status" data-id="id-2">Skill page current</custom> |
| Planning | [tech-lead (human)](https://oraclous.atlassian.net/wiki/spaces/OP/pages/983101) | All | <custom data-type="status" data-id="id-3">Skill page current</custom> |
| Implementation | [test-author](https://oraclous.atlassian.net/wiki/spaces/OP/pages/294957) | Backend | <custom data-type="status" data-id="id-4">Skill page current</custom> |
| Implementation | [backend-implementer](https://oraclous.atlassian.net/wiki/spaces/OP/pages/294995) | Backend | <custom data-type="status" data-id="id-5">Skill page current</custom> |
| Implementation | [frontend-implementer](https://oraclous.atlassian.net/wiki/spaces/OP/pages/295035) | Frontend | <custom data-type="status" data-id="id-6">Skill page current</custom> |
| Implementation | [devops-implementer](https://oraclous.atlassian.net/wiki/spaces/OP/pages/164102) | Coordinator (acts on both repos) | <custom data-type="status" data-id="id-7">Skill page current</custom> |
| Review | [code-reviewer](https://oraclous.atlassian.net/wiki/spaces/OP/pages/622800) | Backend | <custom data-type="status" data-id="id-8">Skill page current</custom> |
| Review | [qa-engineer](https://oraclous.atlassian.net/wiki/spaces/OP/pages/884874) | Backend | <custom data-type="status" data-id="id-9">Skill page current</custom> |
| Review (narrow) | [be-test-reviewer](https://oraclous.atlassian.net/wiki/spaces/OP/pages/1703937) | Backend | <custom data-type="status" data-id="id-10">Skill page current</custom> |
| Documentation | [docs-writer](https://oraclous.atlassian.net/wiki/spaces/OP/pages/557230) | Coordinator (acts on both repos) | <custom data-type="status" data-id="id-11">Skill page current</custom> |

`be-test-reviewer` is a deliberately narrow verification persona, not a full architect. It exists so the backend Tests Review gate has an owner that lives in the backend session without making `solution-architect`/`security-architect` dual-resident. See its page and [Session topology and persona residency](https://oraclous.atlassian.net/wiki/spaces/OP/pages/1736705) Section 3.

## Page template — every agent skill page contains

1. **Identity** — name, tier, one-paragraph role description, primary responsibilities
2. **Role boundary** — what this agent does and what it explicitly does not do; what hand-offs go in and out
3. **Loaded skills** — every skill this agent loads, with its full prose, the patterns it follows, and the outputs it produces
4. **Tool access** — every MCP tool and capability this agent can invoke
5. **Sign-off authority** — which gates this agent owns in the TDD workflow
6. **Model selection** — which model(s) this agent uses, against which BYOM protocol shape
7. **Consciousness configuration** — which Agent Consciousness for Development permissions are enabled, and which patterns this agent's consciousness is specifically configured to detect
8. **Interaction patterns** — how this agent participates in the team flow; typical inputs, outputs, and hand-off shapes
9. **Failure modes and escalation** — what this agent does when stuck, what triggers escalation to tech-lead
10. **Quality criteria** — what "good output" looks like for this agent, with concrete examples where possible
11. **Change History** — table of changes to this agent or its skills, with references to the Agent and Skill Change Log

## Standard skill: Agent Consciousness for Development

Every agent in the catalogue loads [Agent Consciousness for Development](https://oraclous.atlassian.net/wiki/spaces/OP/pages/688403) as a standing skill. Each agent's page documents only the _specific permissions and pattern configurations_ that agent has for the consciousness skill; the skill itself is defined once and referenced.

## Standard skills loaded fleet-wide

Two additional skills are now loaded across the fleet, alongside Agent Consciousness for Development:

* **kb-retrieve** — token-efficient KB retrieval: read the root `llms.txt`/`index.md`, then the one relevant section index, then only the needed file; never read the whole tree. Defined at `oraclous-knowledge/.claude/skills/kb-retrieve/SKILL.md`.
* **graphify** — build and query the KB knowledge graph (`graphify-out/`): `graphify <repo> --update` refreshes the graph after KB changes; `graphify query "…"` / `path` / `explain` answer relationship questions. Used to keep the KB graph current (ORAA-4 §16).

## How an agent page gets updated

Per the [Agent and Skill Change Log](https://oraclous.atlassian.net/wiki/spaces/OP/pages/426078) process:

1. A change is proposed (via consciousness, tech-lead, or ADR)
2. Tech-lead reviews the proposed change to the agent page
3. On approval, the agent page is updated and a Change Log entry is created
4. The agent's "Change History" section gets a new row referencing the Change Log entry

## Related references

* [Agent Team Roster](https://oraclous.atlassian.net/wiki/spaces/OP/pages/589848) — the bird's-eye view of the team
* [Session topology and persona residency](https://oraclous.atlassian.net/wiki/spaces/OP/pages/1736705) — which session each agent runs in
* [Agent Consciousness for Development](https://oraclous.atlassian.net/wiki/spaces/OP/pages/688403) — the standing skill every agent loads
* [Agent and Skill Change Log](https://oraclous.atlassian.net/wiki/spaces/OP/pages/426078) — audit trail for changes
* [ADR-010 — Test-Driven Development with Test-Author Agent](https://oraclous.atlassian.net/wiki/spaces/OP/pages/557078) — the workflow these agents implement
* [Test Strategy](https://oraclous.atlassian.net/wiki/spaces/OP/pages/720940) — the testing approach the agents enforce
