---
confluence_id: "393443"
title: "ADR-011 — External Jira and Confluence (Not Local Wiki)"
---

**Superseded by ADR-014** — Repo-canonical knowledge base; Confluence as mirror; work tracked as GitHub Issues + PRs. This page is now a mirror of `adr/ADR-011-*.md` in [oraclous-knowledge](https://github.com/OraclousAI/oraclous-knowledge). See [ADR-014](https://oraclous.atlassian.net/wiki/spaces/OP/pages/589826) for the decision that supersedes this one.

# ADR-011 — External Jira and Confluence (Not Local Wiki)

## Status

| Field | Value |
| --- | --- |
| Status | <custom data-type="status" data-id="id-0">Superseded</custom> |
| Date | 27 May 2026 |
| Approved by | tech-lead (Reza Jahankohan) |
| Supersedes | None (founding ADR) |
| Superseded by | [ADR-014 — Repo-canonical knowledge base; Confluence as mirror; work tracked as GitHub Issues + PRs](https://oraclous.atlassian.net/wiki/spaces/OP/pages/589826) (merged 2026-05-31, commit `76dd833b`) |
| Driving artifact | 03. Engineering (workflow conventions for the agent team) |

## Context

The agent team needs two infrastructures for its work: a ticketing system (for stories, backlogs, sprints, escalations) and a documentation system (for architecture, ADRs, service references, runbooks). Both can be built in-house, both can be off-the-shelf, both can be hosted or self-hosted. The decision affects everything from how agents author content to how the human (tech-lead) reviews it to how external collaborators (investors, partners, future hires) read it.

Building in-house is appealing because the agent team is itself a product-engineering team that could prototype ticketing and wiki interfaces quickly. It is rejected for the founding decision because the agents have a finite budget and the tools have to exist _before_ the team can start producing. Founding a development team by building its own tooling is a common way to spend a year producing tooling instead of product. The same reasoning applies to selecting and self-hosting an open-source alternative (e.g. Plane, Wiki.js, BookStack): the team would pay setup and maintenance costs against unfamiliar tools without compensating benefits in the founding period.

The remaining choice is which off-the-shelf provider. The team has prior experience with Atlassian (Jira, Confluence), the agents have direct MCP integration available (the Atlassian Rovo MCP server used to author the current documentation), and the human (tech-lead) has accumulated patterns for working with Atlassian over many years. The cost of switching to a different provider would not be technical; it would be the cumulative cost of learning new patterns at a time when the platform itself is the thing the team should be learning.

## Decision

The agent team uses external **Atlassian Confluence** for documentation and external **Atlassian Jira** for ticketing. Neither lives in the Oraclous codebase; both are hosted by Atlassian on the team's Atlassian Cloud subscription. The Confluence space is "Oraclous Platform" (key `OP`); the Jira project is "Oraclous" (key `ORA`).

Operational consequences:

* Architecture, ADRs, service references, runbooks, and all developer-facing documentation live in Confluence under the locked structure (01. Architecture, 02. ADRs, 03. Engineering, 04. Services Reference, 05. Operations, 06. Compliance, 07. Frontend, 08. Meta).
* All stories, epics, bugs, sprints, and backlog grooming happen in Jira under project ORA.
* Agents interact with both through the Atlassian Rovo MCP server. [solution-architect](https://oraclous.atlassian.net/wiki/spaces/OP/pages/164068), [security-architect](https://oraclous.atlassian.net/wiki/spaces/OP/pages/557195), [product-planner](https://oraclous.atlassian.net/wiki/spaces/OP/pages/884840), [qa-engineer](https://oraclous.atlassian.net/wiki/spaces/OP/pages/884874), [docs-writer](https://oraclous.atlassian.net/wiki/spaces/OP/pages/557230), and the implementer agents all have scoped access through their tool-access configurations.
* Customer-facing documentation (the product's public docs, when they exist) is a separate decision; this ADR is about internal development documentation only.

## Alternatives considered

### A. Build a local wiki and ticketing inside the Oraclous repo

Author content as Markdown in the repo; render with a static site generator (e.g. mkdocs); track stories as GitHub issues. Self-contained, single-source. Rejected for v1 because (a) it forces every agent that needs to read or write to learn a custom Markdown convention and a static-site rendering, (b) it pushes ticketing onto GitHub issues which lack the structure (sprints, backlogs, links) the team's workflow needs, and (c) it ties documentation evolution to repo changes, which is the opposite of the discipline this team's documentation needs (docs evolve faster than code, not slower).

### B. Self-host open-source alternatives (Plane + Wiki.js, or similar)

Get the structure of Atlassian without the subscription cost or vendor lock-in. Considered seriously because the team has open-source preferences in many other places. Rejected for the founding period because the setup, maintenance, and MCP-integration costs would absorb agent budget that is more valuable building the platform. The decision is revisitable; a future ADR can migrate to self-hosted tools if and when the value-vs-cost balance shifts.

### C. Notion (or similar all-in-one)

Notion bundles documentation and ticketing into one product with better UX than Atlassian for many tasks. Rejected because Notion's structure is less well-suited to the team's discipline (status workflows, sprint cadence, formal ADR processes), and its MCP integration is less mature for the structured operations the agents perform.

### D. GitHub-only (issues + wiki + code in one repo)

Maximally consolidated. Rejected because GitHub's wiki is intentionally lightweight and would not support the structured browsing, status workflows, and inter-page link auditing the platform's documentation needs. GitHub remains the source of truth for code; this ADR allocates documentation and ticketing elsewhere.

## Consequences

### Positive

* The agent team has functioning ticketing and documentation infrastructure from day one. No setup overhead is absorbed by the team's founding work.
* The Atlassian Rovo MCP server is already mature and exposes the operations the agents need (page CRUD, story CRUD, JQL search, sprint operations).
* Documentation is rich-structured (Confluence's stored format, status macros, info panels, code blocks, hierarchical pages) rather than Markdown-flat. The architecture and ADR pages benefit from this directly.
* External collaborators (investors, partners, future hires) can be granted scoped read access without giving them repo access.

### Negative

* The team pays an ongoing subscription. The cost is modest at the team's current scale but is real and increases with adopters.
* The team depends on Atlassian's availability for both documentation and ticketing. Mitigated by periodic exports as part of the operational disciplines; Phase 1 includes a documented export procedure (devops-implementer + docs-writer).
* If Atlassian's MCP server changes shape or capability, the agent team must adapt. This is a real coupling cost; it is bounded by the fact that the agents' Atlassian use is structured (and could be re-implemented against another MCP if needed) rather than freeform.
* External collaborators need Atlassian accounts to read. This is friction; the platform accepts it for v1.

## Implementation notes

* The Confluence space structure is locked: the 8 top-level hubs (01–08) plus their children are the canonical layout. New top-level hubs require an ADR or an architecture revision.
* Jira project ORA uses the Kanban-with-sprints workflow defined in [Definition of Done](https://oraclous.atlassian.net/wiki/spaces/OP/pages/66010).
* Every agent's tool-access table (in its skill page) declares the Atlassian access scope it needs. The principle of least privilege applies: docs-writer can write to 04, 05, 06; cannot write to 01 or 02 unilaterally.
* Periodic exports (weekly Confluence space export, weekly Jira project export) are an operational discipline owned by devops-implementer and run from CI. The exports live in a separate backup location.
* If the team eventually migrates away from Atlassian, the migration is an explicit ADR-level decision with an explicit plan, not a silent transition. The structured artifacts (ADRs, OHM spec, Governance Taxonomy, Threat Catalogue) are deliberately authored to survive a migration: their content is portable Markdown / YAML / HTML, not Atlassian-specific structures.

## References

* 03. Engineering — the hub for engineering workflow conventions
* [Definition of Done](https://oraclous.atlassian.net/wiki/spaces/OP/pages/66010) — the Kanban workflow this ADR is the substrate for
* [Git Workflow](https://oraclous.atlassian.net/wiki/spaces/OP/pages/131103) — the parallel GitHub-side conventions
* [Agent Skills Catalogue](https://oraclous.atlassian.net/wiki/spaces/OP/pages/753852) — agents whose tool-access scopes are anchored on this decision
* [ADR-010](https://oraclous.atlassian.net/wiki/spaces/OP/pages/557078) — the TDD workflow this tooling supports

## Revision history

| Date | Change |
| --- | --- |
| 27 May 2026 | Initial publication in uniform ADR template. |
| 31 May 2026 | Marked **Superseded** by ADR-014 (PR merged commit `76dd833b`). Banner added. \[agent:docs-writer\] |
