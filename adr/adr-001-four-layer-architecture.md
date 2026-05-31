# ADR-001 — Four-Layer Architecture

| Field | Value |
| --- | --- |
| Status | Accepted |
| Date | 27 May 2026 |
| Approved by | tech-lead (Reza Jahankohan) |
| Supersedes | None (founding ADR) |
| Driving artifact | Section 3 — Layered Architecture |

## Context

Oraclous v0 grew organically: services were added where they fit at the moment they were needed. The result was a system where data flowed in too many directions, where state could live in any service, and where security boundaries were enforced at whichever layer noticed the request rather than at a designed enforcement plane.

## Decision

The platform is organised into exactly four layers, with strict downward-only dependencies:

1. **Substrate** — the only stateful layer. Owns persistence, ReBAC primitives, KMS integration, audit storage, the OHM document store, the asset store, and the per-organisation tenancy anchor.
2. **Capability registry** — the catalogue of capabilities. Depends only on the substrate.
3. **Harness runtime** — loads OHM documents, resolves their references, executes harnesses.
4. **Application gateway** — the external API surface.

The dependency direction is strict: substrate code does not import from any higher layer.

## Consequences

**Positive:** Every architectural question has an unambiguous home. Security enforcement points are predictable.

**Negative:** Some changes will need to thread through three layers to deliver a single user-visible effect.
