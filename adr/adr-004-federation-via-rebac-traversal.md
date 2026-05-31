---
confluence_id: "131083"
title: "ADR-004 — Federation via ReBAC Traversal"
---

# ADR-004 — Federation via ReBAC Traversal

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

Many platform features only become valuable when organisations can share capabilities across organisational boundaries: a partner offers a specialised retrieval capability to its customers; an open-source community publishes capabilities a customer can adopt; a customer wants to expose a capability to a sister organisation it controls. The platform either supports this natively or pushes the work into ad-hoc per-customer integration code, which is what v0 ended up doing.

Cross-organisation access has two layers of complexity. The first is identity: which principal is making the cross-org call, and how is its authorisation established? The second is reference semantics: when a harness in org A references a capability in org B, what does the platform do at load time? Both layers can be solved with bespoke per-relationship logic, but that solution does not scale — each new federation pattern becomes its own code path, its own audit surface, its own bug class.

The platform already uses relationship-based access control (ReBAC) for intra-organisation authorisation: principals have relations to objects, and access decisions follow the relations. Extending the same model to cross-organisation traversal — rather than inventing a parallel federation mechanism — keeps the security model unified, reuses the ReBAC enforcement points already required at every layer, and makes federation policies expressible in the same vocabulary as ordinary access policies.

## Decision

Cross-organisation access is mediated entirely by the substrate's ReBAC layer. There is no parallel "federation" subsystem; federation is a pattern of ReBAC relations, not a separate concept.

Concretely:

* The capability registry exposes a third registry prefix, `federated:<federation-id>`, in addition to `core` and `org:<org-id>`. References to `federated:*` resolve to capabilities owned by other organisations.
* Resolving a `federated:*` reference at harness load time requires the substrate to find a `has_federation_agreement` relation between the calling organisation and the target organisation. Absent the relation, resolution fails closed.
* The federation agreement itself is a ReBAC relation, not a separate data type. Establishing a federation means establishing the relation; revoking the federation means revoking the relation.
* The audit log records the federation traversal with both organisation identities and the relation that authorised it.
* The policy set bound to the harness must permit the `federated:*` registry (see [Structured Governance Taxonomy](https://oraclous.atlassian.net/wiki/spaces/OP/pages/688439); `policy-set:production-federated@1.0.0` is the default federation-enabled policy set).

## Alternatives considered

### A. Separate federation subsystem

Build a federation service with its own concept of trust agreements, its own policy language, its own audit pipeline. Common pattern in enterprise systems. Rejected because it duplicates ReBAC concerns and creates a second authorisation surface that must be kept consistent with the first. Two surfaces means twice the bugs and twice the audit complexity.

### B. Federation via per-organisation API keys

Each organisation issues API keys to organisations it federates with. Simpler to implement initially, but moves authorisation into key-management rather than relationship-management, and loses the ability to express fine-grained federation policies (e.g. "org A may use only these specific capabilities from org B"). Rejected.

### C. Federation via public marketplace

Treat federated capabilities as publicly listed and rely on per-invocation paywalls or rate limits rather than per-organisation agreements. Suits a future marketplace product; not appropriate as the founding federation mechanism because most platform-grade federation use cases (partner integrations, sister organisations, regulated industries) need explicit pairwise agreement.

### D. No federation in v1 (defer the problem)

Ship v1 with single-organisation only, decide federation later. Considered seriously because federation is genuinely complex. Rejected because deferring federation means deferring the integration use cases that justify several of the platform's positioning claims, and because the ReBAC-traversal approach is cheap to ship (the substrate already enforces ReBAC; the federation cost is mostly the policy-set surface and audit additions).

## Consequences

### Positive

* Federation reuses the ReBAC enforcement points already required at every layer. No new authorisation surface, no second policy language, no parallel audit pipeline.
* Federation policies are expressible in the same vocabulary as ordinary access policies. [security-architect](https://oraclous.atlassian.net/wiki/spaces/OP/pages/557195) reviews federation patterns with the same skill set as ordinary access reviews.
* Federation is auditable through the substrate's audit primitives; no special-case logging.
* The platform supports a wide range of federation patterns — bilateral agreements, group federations (a relation on an organisation set), conditional federations (relations with additional clauses) — all expressed through ReBAC.

### Negative

* ReBAC traversal across organisations is more expensive than intra-organisation traversal. The substrate must check both that the relation exists and that it is current. Phase 1 includes caching with bounded staleness (subsecond invalidation) to manage the cost.
* Federation requires both organisations to be on Oraclous deployments that share a trust anchor. Heterogeneous federation (Oraclous to non-Oraclous) is not addressed by this ADR and would require a future decision.
* The "federation is a ReBAC pattern" framing requires careful documentation to be discoverable; operators looking for "federation settings" will not find a dedicated subsystem and need to be pointed at the relations. [docs-writer](https://oraclous.atlassian.net/wiki/spaces/OP/pages/557230) owns making this discoverable.

## Implementation notes

* The `has_federation_agreement` relation is the founding federation relation. Future ADRs may introduce sub-relations (e.g. `has_capability_specific_federation`) without changing the federation model.
* The capability registry's federated-resolution path is a documented service-reference page (Phase 1 deliverable).
* [Structured Governance Taxonomy](https://oraclous.atlassian.net/wiki/spaces/OP/pages/688439) includes `policy-set:production-federated@1.0.0` as the founding federation-enabled policy set; harnesses bound to other policy sets cannot resolve `federated:*` references.
* Federation revocation propagates within seconds, with bounded staleness explicitly documented for security review (see [Threat T2 mitigation T2-M2](https://oraclous.atlassian.net/wiki/spaces/OP/pages/983129)).

## References

* [Section 6 — Governance Model](https://oraclous.atlassian.net/wiki/spaces/OP/pages/720900)
* [ADR-006](https://oraclous.atlassian.net/wiki/spaces/OP/pages/393403) — organisation tenancy, the boundary federation crosses
* [Structured Governance Taxonomy](https://oraclous.atlassian.net/wiki/spaces/OP/pages/688439)
* [Structured Threat Catalogue](https://oraclous.atlassian.net/wiki/spaces/OP/pages/983129) — T2 (privilege escalation), T4 (capability poisoning)
* [ADR-002](https://oraclous.atlassian.net/wiki/spaces/OP/pages/557058) — OHM's `federated:*` capability reference shape

## Revision history

| Date | Change |
| --- | --- |
| 27 May 2026 | Initial publication in uniform ADR template. |
