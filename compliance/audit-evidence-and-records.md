---
source_page_id: 884800
title: "Audit Evidence and Records"
---

# Audit Evidence and Records

Where compliance evidence lives, how it's collected, and how auditors access it. This page is the index for evidence sources — the actual evidence sits in the systems that generate it.

## Status

Placeholder — populated as evidence sources come online

## Evidence philosophy

* **Generate evidence as a side effect of operation** — not as a separate compliance activity. PR approvals are evidence of change management. Provenance is evidence of data handling. On-call rotation records are evidence of incident response readiness.
* **Single source of truth per control** — every control has one designated evidence source; never duplicate evidence collection
* **Queryable, not scraped** — auditors who can use a query interface get faster access; canned reports are pre-built for non-technical reviewers
* **Tamper-evident retention** — evidence retention uses append-only stores (provenance, immutable backups) wherever the control demands it

## Evidence sources

| Evidence type | Source | Retention | Owner |
| --- | --- | --- | --- |
| Code review records | GitHub PRs in `OraclousAI/oraclous-backend`, `OraclousAI/oraclous-frontend` | Lifetime of org | Engineering |
| Deployment approvals | GitHub Actions deploy logs + Jira release tickets | Lifetime of org | Engineering |
| Access reviews | Identity provider audit logs + quarterly review records in Confluence | 7 years | Security |
| User authentication | auth-service logs + identity provider logs | 1 year hot, 7 years cold | Security |
| Data access (customer-domain) | Platform provenance spine (the substrate) | Per customer policy; default 7 years | Customer (their data) |
| Operator access (cloud-hosted) | Cloud provider audit logs + bastion session recordings | 7 years | Security |
| Incident records | Jira incidents + post-mortem pages in Confluence | 7 years | Operations |
| Vulnerability scans | Scanner output + remediation tickets in Jira | 3 years | Security |
| Backup tests | Recovery test records in Confluence | 3 years | Operations |
| Risk register | Confluence (restricted) | Current + 3 years history | Security |
| Policy approvals | Confluence page version history | Lifetime of org | Security |
| Training completion | Identity provider + training platform records | Duration of employment + 3 years | People |
| Subprocessor changes | Confluence subprocessor page version history | Lifetime of org | Legal |
| Change Advisory Board minutes | Confluence | 7 years | Engineering |

## What this page will cover

* **Detailed evidence catalogue** — for every control, the specific query/report/document that demonstrates operation
* **Auditor access process** — how auditors are granted access, what they see, how their access is logged
* **Customer access to selected evidence** — what customers see (audit reports under NDA), what they don't (internal risk register, raw provenance from other customers)
* **Evidence freshness checks** — automated checks that flag stale or missing evidence
* **Annual evidence review** — what's checked, by whom, with what cadence
* **Sample evidence** — anonymised examples of common evidence formats (for new compliance staff and customer evaluations)

## Provenance as evidence

The platform's provenance spine is a first-class evidence source. Standard queries auditors will run:

* "Show every operator access to customer X's data in the audit period"
* "Show every cross-organisation access attempt (allowed and denied)"
* "Show every change to a production OHM artifact"
* "Show every credential access by service Y"
* "Show every HITL gate triggered and resolved"

These queries answer specific control objectives directly from the system rather than via reconstructed logs.

## Related references

* **ISO 27001 Programme** — for which evidence maps to which Annex A control
* **SOC 2 Programme** — for which evidence maps to which TSC criterion
* **Section 6.5** — Security threats with mitigations (each mitigation has an evidence source)
* **Incident Response** — generates incident evidence
* **Monitoring and Observability** — telemetry as evidence (where applicable)
