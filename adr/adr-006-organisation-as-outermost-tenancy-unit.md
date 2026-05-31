# ADR-006 — Organisation as Outermost Tenancy Unit

| Field | Value |
| --- | --- |
| Status | Accepted |
| Date | 27 May 2026 |
| Approved by | tech-lead (Reza Jahankohan) |
| Refined by | ADR-012 |

## Decision

The **organisation** is the outermost tenancy unit on Oraclous. Every storage operation, audit event, ReBAC relation, BYOM credential, OHM document, capability publication, and metering record is anchored on an `organisation_id`.

- Every substrate table has an `organisation_id` column. There is no "global" tenant-scoped data.
- Every read parameterises by `organisation_id`, sourced from the authenticated principal context (never from request body).
- Cross-organisation traversal goes through the ReBAC layer exclusively.
