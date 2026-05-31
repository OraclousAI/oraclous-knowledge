---
confluence_id: "164042"
title: "Tooling and Integration Map"
---

# Tooling and Integration Map

The external tools the Oraclous engineering process depends on, how they connect, and what each is the source of truth for. This page exists because the platform crosses several systems (Atlassian, GitHub, Claude Code, model providers) and the integration boundaries need to be explicit.

## Sources of truth

Each artifact lives in exactly one place. When systems disagree, the table below resolves it.

| Artifact | Source of truth | Mirror or derivative |
| --- | --- | --- |
| Architecture, ADRs, design docs | Confluence (this space) | None |
| Issues, epics, sprints | Jira (project ORA) | None |
| Source code | GitHub (`OraclousAI/oraclous-backend`, `OraclousAI/oraclous-frontend`) | None |
| Container images | GitHub Container Registry | None |
| Production OHM seed artifacts | Backend repo `seeds/` directory | Customer workspaces (after bootstrap update) |
| API contracts | Backend OpenAPI spec (generated from code) | Frontend types (generated from OpenAPI) |
| Knowledge base content | Confluence pages | None |

## Atlassian setup

* **Site** — `oraclous.atlassian.net`
* **Cloud ID** — `1eb21297-5f52-49a0-a303-3436694b148c`
* **Confluence space** — Oraclous Platform (key `OP`, ID `688131`)
* **Jira project** — Oraclous V1 (key `ORA`, ID `10001`)
* **Issue types in ORA** — Epic, Story, Task, Subtask, Feature, Bug, Spike, ADR

### Jira Kanban columns (target configuration)

The Kanban board for ORA is configured with the following columns (set in the Jira UI):

1. **Backlog**
2. **Ready**
3. **Tests Authoring** — WIP limit 3
4. **Tests Review** — WIP limit 3
5. **Implementation** — WIP limit 5
6. **Code Review** — WIP limit 5
7. **Done**
8. **Blocked**

The WIP limits enforce focus and surface stalls; tickets sitting in any column beyond expected duration trigger investigation.

### Confluence hub IDs

For agents and future contributors that need to add pages, the parent IDs are:

* **Homepage** — `688237`
* **01. Architecture** — `753665`
* **Platform Architecture v1.1 parent** — `753707`
* **02. ADRs** — `589826`
* **03. Engineering** — `65923`
* **04. Services Reference** — `786433`
* **05. Operations** — `753686`
* **06. Compliance** — `163984`
* **07. Frontend** — `65944`
* **08. Meta** — `851969`

## GitHub setup

* **Organisation** — `OraclousAI` ([https://github.com/organizations/OraclousAI/)](https://github.com/organizations/OraclousAI/))
* **Backend repo** — `OraclousAI/oraclous-backend` (to be created on first commit)
* **Frontend repo** — `OraclousAI/oraclous-frontend` (to be created on migration from legacy)
* **Legacy frontend (transitional)** — `Jahankohan/oraclous-app` on the `develop` branch; migrating to OraclousAI org
* **Container registry** — GitHub Container Registry under `OraclousAI` org

### GitHub Actions

CI runs on every PR and on every merge to `main`:

* Backend: unit tests, integration tests, security tests, lint, type-check, OpenAPI generation, container build
* Frontend: unit tests, component tests, Playwright smoke E2E, lint, type-check, container build (or static artifact)

Deploy workflows trigger on releases (semver tag), not on every merge.

## Claude Code setup

Claude Code is configured with the 11-agent team described in **Agent Team Roster** (under 03. Engineering):

* **Architecture-tier**: solution-architect, security-architect
* **Planning-tier**: product-planner, tech-lead (human)
* **Implementation-tier**: test-author, backend-implementer, frontend-implementer, devops-implementer
* **Review-tier**: code-reviewer, qa-engineer
* **Documentation-tier**: docs-writer

### MCP connections in Claude Code

* **Atlassian MCP** — for Jira issue and Confluence page management
* **GitHub MCP** — for source code, PRs, issues, CI runs
* **Filesystem MCP** — for local repo work

## Model providers (BYOM)

Per ADR-007, three protocol shapes are supported in v1:

* **Anthropic native** — for development; Claude Max subscription for engineering work; production model selection per organisation
* **OpenAI-compatible** — covers OpenAI, OpenRouter, Azure OpenAI, LM Studio, and others speaking the same protocol
* **AWS Bedrock native** — for AWS-aligned customers

Excluded from v1: Google Gemini, Cohere, Mistral (deferred; revisit when customer demand justifies).

## Communication

* **Engineering decisions** — Confluence (ADRs and architecture pages)
* **Work tracking** — Jira (project ORA)
* **Code review** — GitHub PRs
* **Operational alerts** — TBD; configured per the Incident Response page
* **External customer status** — TBD; status page for cloud-hosted

## Workflow boundaries

* **Code never lives in Confluence** — only documentation; code lives in GitHub
* **Documentation never lives in code** — except for the README quickstart and [CLAUDE.md](http://CLAUDE.md) per repo; substantive docs live in Confluence
* **Issues live in Jira, not in GitHub issues** — GitHub PRs reference Jira tickets
* **Agent activity is tracked in Jira** — every agent run that produces a deliverable creates or updates a Jira ticket

## Related references

* **ADR-011** — External Jira and Confluence (not local wiki)
* **Agent Team Roster (under 03. Engineering)** — agent configuration detail
* **Git Workflow (under 03. Engineering)** — branch and PR conventions
* **Definition of Done (under 03. Engineering)** — what needs to land where for a ticket to close
