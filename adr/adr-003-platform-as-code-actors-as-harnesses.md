# ADR-003 — Platform-as-Code, Actors-as-Harnesses

| Field | Value |
| --- | --- |
| Status | Accepted |
| Date | 27 May 2026 |
| Approved by | tech-lead (Reza Jahankohan) |

## Decision

The platform is "platform-as-code" — the platform itself is code deployed and versioned through normal engineering practice. The _actors_ on the platform are not code. They are harnesses, described by OHM documents, interpreted by the harness runtime.

Every executable thing on the platform is a harness. Composition is expressed by a harness referencing other capabilities, not by a separate workflow concept. Governance, audit, and budget apply at the harness level.
