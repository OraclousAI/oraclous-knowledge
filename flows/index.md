---
confluence_id: "1212418"
title: "10. Engineering Flows"
---

**Document status:** <custom data-type="status" data-id="id-0">Active</custom> · **Maintained by:** [solution-architect](https://oraclous.atlassian.net/wiki/spaces/OP/pages/164068) with [tech-lead](https://oraclous.atlassian.net/wiki/spaces/OP/pages/983101) sign-off

This hub holds the **flows** — the documented sequences by which the agent team turns big units of work into small, doable, assignable pieces, and by which team members reach agreement on shared things (data structures, API contracts, manifest fields, ReBAC relations). The release pages under [09. Releases](https://oraclous.atlassian.net/wiki/spaces/OP/pages/164160) say _what_ ships; the flows here say _how_ the work gets broken down and how cross-cutting decisions get made and recorded.

This hub exists because the system had the nouns (ADRs record decisions; the OHM Spec, Governance Taxonomy, and Threat Catalogue hold agreed structures) but not the verbs (how a decision or a shared shape actually gets agreed between two implementers working in separate repositories). These flows are those verbs.

## 1. The work breakdown hierarchy

Work descends through these levels. Each level has an owning agent and, where relevant, a gate that agent owns.

| Level | Artifact home | Owning agent(s) | Gate owned |
| --- | --- | --- | --- |
| **Architecture** — the 9-month migration arc | Confluence ([Section 8](https://oraclous.atlassian.net/wiki/spaces/OP/pages/688329)) | human tech-lead + solution-architect | — (strategic) |
| **Release** — a coherent slice of platform work | Confluence ([09. Releases](https://oraclous.atlassian.net/wiki/spaces/OP/pages/164160)) | human tech-lead + solution-architect | — (strategic) |
| **Migration source map** — per-release: what to lift from legacy vs build new, per deliverable | Confluence (section on each release page; see [09. Releases](https://oraclous.atlassian.net/wiki/spaces/OP/pages/164160) Section 7) | product-planner (verdicts) + solution-architect (target shape) + security-architect (threats) | Planned → Briefed |
| **Epic** — one coherent capability within a release, scoped to one repo | Jira | product-planner | — |
| **Contract** — an agreed shape that binds two repos or two services | Jira (issue) + canonical home (Confluence / OHM Spec / Governance Taxonomy) | solution-architect (+ security-architect if security-touching) | see Cross-cutting agreement protocol |
| **Story** — one independently-shippable behaviour; 1–3 days; carries a lift-tag | Jira | product-planner | Backlog → Ready (joint with architects) |
| **Tests** — the failing-tests PR | GitHub `[tests]` PR | test-author | Ready → Tests Authoring → Tests Review |
| **Tests sign-off** | GitHub | solution-architect (+ security-architect if marked) | Tests Review → Implementation |
| **Implementation** — the code PR | GitHub `[impl]` PR | backend-implementer / frontend-implementer | Implementation → Code Review |
| **Final review** | GitHub + Jira | code-reviewer + qa-engineer + architects + human tech-lead | Code Review → Done |
| **Doc reconciliation** | Confluence | docs-writer | — (triggered by Done) |

Two notes. The **TDD pair** (a `[tests]` PR and an `[impl]` PR) is not a Jira level — one story produces two PRs but remains one story; the PRs are tracked in GitHub and linked from the story. And the **Contract** level sits between Epic and Story: an epic can spawn contracts, and a contract spawns the paired implementing stories (one per repo).

## 2. The two flows in this hub

* **Cross-cutting agreement protocol** — how team members agree on a shared data structure, API contract, OHM field, or ReBAC relation, and where the agreement is recorded. This is the flow that prevents two repo sessions from each inventing their own incompatible version of a shared shape.
* **Interface Contracts** — the canonical home (interim, until the gateway's OpenAPI spec exists at R6) for agreed cross-repo API shapes. The record that the agreement protocol writes to.

The migration source map convention itself lives on [09. Releases](https://oraclous.atlassian.net/wiki/spaces/OP/pages/164160) Section 7, because it is bound tightly to the release pages it annotates.

## 3. Why these flows are coordinator-owned

Every level from Release down through Story-in-Ready is planning, architecture, or agreement work that needs the whole-workspace view — it reads both repositories but produces Confluence pages and Jira tickets, not repository code. Every level from Tests Authoring down through Done is execution work that needs one repository's filesystem. The fault line between them is the Story → Tests boundary. The flows in this hub all live above that line, which is why they are owned by the planning and architecture personas (product-planner, solution-architect, security-architect in threat-model mode, docs-writer) rather than by the implementer personas.

## 4. Related references

* [09. Releases](https://oraclous.atlassian.net/wiki/spaces/OP/pages/164160) — the release hub; Section 6 is the Agent Identity Convention, Section 7 is the migration source map convention
* [Section 8 — Consolidation and Migration Plan](https://oraclous.atlassian.net/wiki/spaces/OP/pages/688329) — the migration arc the breakdown executes against
* [Definition of Done](https://oraclous.atlassian.net/wiki/spaces/OP/pages/66010) — the gate sequence each story walks
* [Agent Skills Catalogue](https://oraclous.atlassian.net/wiki/spaces/OP/pages/753852) — the agents that own each level
