# Tooling and Integration Map

The external tools the Oraclous engineering process depends on.

## Sources of truth

| Artifact | Source of truth | Mirror or derivative |
| --- | --- | --- |
| Architecture, ADRs, design docs | Confluence (OP space) → this repo | This repo is canonical |
| Issues, epics, sprints | Jira (project ORA) | None |
| Source code | GitHub (`OraclousAI/oraclous-backend`, `OraclousAI/oraclous-frontend`) | None |
| API contracts | Backend OpenAPI spec (generated from code) | Frontend types (generated from OpenAPI) |

## Atlassian setup

- **Site** — `oraclous.atlassian.net`
- **Cloud ID** — `1eb21297-5f52-49a0-a303-3436694b148c`
- **Confluence space** — Oraclous Platform (key `OP`, ID `688131`)
- **Jira project** — Oraclous V1 (key `ORA`, ID `10001`)
- **Homepage** — `688237`

### Confluence hub IDs

| Hub | Page ID |
| --- | --- |
| 01. Architecture | 753665 |
| 02. ADRs | 589826 |
| 03. Engineering | 65923 |
| 04. Services Reference | 786433 |
| 05. Operations | 753686 |
| 06. Compliance | 163984 |
| 07. Frontend | 65944 |
| 08. Meta | 851969 |
| 09. Releases | 164160 |
| 10. Engineering Flows | 1212418 |

### Jira field IDs

- `Agent Owner` = `customfield_10074`, single-select, **13 options**
- `needs-human` = `customfield_10075`, multi-checkbox, option id `10032`
- `human` option id = `10031`
- `Contract` issue type = `10049`, `ADR` = `10016`, `Spike` = `10015`

## GitHub setup

- **Organisation** — `OraclousAI`
- **Backend repo** — `OraclousAI/oraclous-backend`
- **Frontend repo** — `OraclousAI/oraclous-frontend`
