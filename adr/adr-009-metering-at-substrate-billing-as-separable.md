---
confluence_id: "393423"
title: "ADR-009 — Metering at Substrate, Billing as Separable"
---

# ADR-009 — Metering at Substrate, Billing as Separable

## Status

| Field | Value |
| --- | --- |
| Status | <custom data-type="status" data-id="id-0">Accepted</custom> |
| Date | 27 May 2026 |
| Approved by | tech-lead (Reza Jahankohan) |
| Supersedes | None (founding ADR) |
| Superseded by | None |
| Driving artifact | [Section 6 — Governance Model](https://oraclous.atlassian.net/wiki/spaces/OP/pages/720900) |

## Context

Every multi-tenant platform needs to know what each tenant used. The question is where that knowledge lives and how it is structured. Two extremes bound the space. On one end, the platform treats metering as a billing concern: a billing service ingests events from various services, normalises them, and produces invoices. On the other end, the platform treats metering as a substrate concern: the substrate emits authoritative usage events, and any number of consumers (billing being one) read them.

The billing-first approach is common because billing is the visible business need. Its cost is that "what did this organisation use this month?" can only be answered by querying the billing service, which means a customer who wants their own usage data for cost analysis, capacity planning, or internal chargeback has to either get it from the billing service (which may not expose it cleanly) or instrument their harnesses independently (which gives a different answer than billing). When billing is the only source of truth for usage, billing's authority becomes total.

The substrate-first approach treats usage as a first-class observation. The substrate emits a usage event for every meaningful action (capability invocation, model token consumption, storage operation, audit event). Billing is one consumer; cost analysis, capacity planning, chargeback, anomaly detection, and FinOps tooling are others. The cost is that usage emission becomes a load-bearing substrate concern that must be reliable even when billing is irrelevant (e.g. self-hosted deployments).

## Decision

Metering is a substrate concern. The substrate emits authoritative **usage events** at every metered action. Billing is a separable consumer of the usage event stream, not the owner of the metering data.

Concretely:

* Every metered action emits a structured usage event from the substrate: `{ organisation_id, principal, action_type, quantity, unit, dimensions, timestamp }`.
* Metered actions include: model token consumption (input, output, cached), capability invocations, storage reads and writes (rated by bytes), audit-log emission (rated by bytes), substrate operations (rated by count).
* The usage event stream is durable and append-only. Past events are not modified; corrections take the form of compensating events.
* Billing is a downstream service that consumes the usage event stream and produces invoices. It is one consumer; nothing about the metering design assumes billing exists. Self-hosted Oraclous deployments have metering and no billing, with no source-code differences in the metering path.
* Customers can read their own organisation's usage event stream through the application gateway. The stream is part of the platform's surface, not a billing-internal artifact.

## Alternatives considered

### A. Billing-owned metering

Billing is the source of truth; usage data is a billing-service implementation detail. Familiar, simple. Rejected because the platform's customers (especially the data-sovereignty-focused ones) have legitimate FinOps and chargeback needs that should not depend on the billing surface. Coupling usage to billing creates the wrong abstraction for self-hosted deployments where billing is absent.

### B. Per-service metering (each service emits its own usage)

Each service (substrate, capability registry, harness runtime, application gateway) emits its own usage events. Decoupled but redundant: usage events from different services frequently describe the same action from different angles. Rejected because the substrate is the only layer that observes every metered action authoritatively; other layers' "usage" is necessarily derived.

### C. Sampled metering (sample N% of actions, extrapolate)

Standard observability technique for high-volume systems. Considered as an optimisation. Rejected for v1 because usage events drive billing for cloud-hosted; sampled billing is not credible to customers. Sampling may be acceptable for some downstream consumers (e.g. capacity planning) but not for the source-of-truth stream.

### D. Metering only when billing-relevant (no usage stream in self-hosted)

Save the cost of usage emission in self-hosted deployments. Rejected because the cost is small, the operational consistency matters more, and self-hosted customers also want FinOps and chargeback insights.

## Consequences

### Positive

* Usage is a first-class observation, available to billing, FinOps, anomaly detection, customer dashboards, capacity planning, and internal chargeback in customer organisations.
* Self-hosted and cloud-hosted modes are uniform in metering. The substrate behaves identically; only the downstream billing consumer differs.
* Billing changes (new pricing, new dimensions, new aggregation windows) do not require substrate changes. Billing is just another reader.
* The customer can answer "what did my organisation use?" from their own data; they do not have to ask Oraclous-the-company.

### Negative

* Usage emission is on every metered path. The cost is small per emission but is a tax the substrate pays continuously; performance budgets must include it.
* The usage event schema becomes a platform commitment that downstream consumers depend on. Schema evolution requires the same discipline as other platform contracts (deprecation windows, additive changes).
* The line between "metered" and "not metered" is itself a policy decision. The decision is documented in the platform's pricing model (which is a billing-service concern, not architectural) but the substrate must know which actions to emit events for. Updates to the metered-action list become a coordinated change between billing and substrate.

## Implementation notes

* Usage events emit through the substrate's audit pipeline alongside audit events, but to a separate stream. The two streams share schema discipline but not destination.
* The usage stream is append-only with retention defined per deployment mode: cloud-hosted retains for the billing cycle window plus one full cycle for reconciliation; self-hosted retains per operator's configuration.
* Customer-facing usage reads are paginated and filterable by action_type and time window. The application-gateway service-reference page documents the surface.
* Billing for cloud-hosted reads from the usage stream into a separate billing data warehouse; the warehouse is the source of truth for invoices, not the live stream.
* Phase 1 ships substrate-side emission with the founding metered actions (model tokens, capability invocations, storage operations); billing-side ingestion is Phase 2.

## References

* [Section 6 — Governance Model](https://oraclous.atlassian.net/wiki/spaces/OP/pages/720900)
* [ADR-001](https://oraclous.atlassian.net/wiki/spaces/OP/pages/753752) — substrate as the only stateful layer; metering belongs here for the same reason
* [ADR-006](https://oraclous.atlassian.net/wiki/spaces/OP/pages/393403) — organisation tenancy; usage events anchor on `organisation_id`
* [ADR-008](https://oraclous.atlassian.net/wiki/spaces/OP/pages/753792) — cloud-hosted operator-separation; usage events are metadata, not customer state, so they can be read by Oraclous for billing without breaking operator-separation
* [Structured Governance Taxonomy](https://oraclous.atlassian.net/wiki/spaces/OP/pages/688439) — policy-set budget ceilings interact with metering (budgets are enforced against the same emission)

## Revision history

| Date | Change |
| --- | --- |
| 27 May 2026 | Initial publication in uniform ADR template. |
