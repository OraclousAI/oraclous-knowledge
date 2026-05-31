# Audit Evidence and Records

**Status:** Placeholder — populated as evidence sources come online

## Evidence philosophy

- Generate evidence as a side effect of operation — not as a separate compliance activity
- Single source of truth per control — every control has one designated evidence source
- Queryable, not scraped — auditors who can use a query interface get faster access
- Tamper-evident retention — evidence retention uses append-only stores wherever the control demands it

## Evidence sources

| Evidence type | Source | Retention |
| --- | --- | --- |
| Code review records | GitHub PRs | Lifetime of org |
| Deployment approvals | GitHub Actions deploy logs + Jira release tickets | Lifetime of org |
| Data access (customer-domain) | Platform provenance spine (the substrate) | 7 years (default) |
| Incident records | Jira incidents + post-mortem pages | 7 years |
