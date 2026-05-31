# ADR-009 — Metering at Substrate, Billing as Separable

| Field | Value |
| --- | --- |
| Status | Accepted |
| Date | 27 May 2026 |
| Approved by | tech-lead (Reza Jahankohan) |

## Decision

Metering is a substrate concern. The substrate emits authoritative **usage events** at every metered action. Billing is a separable consumer of the usage event stream, not the owner of the metering data.

Usage events: `{ organisation_id, principal, action_type, quantity, unit, dimensions, timestamp }`. The stream is durable and append-only.

**Substrate emits tokens/count/bytes, never USD and never credits** (both are rate tables → downstream billing).
