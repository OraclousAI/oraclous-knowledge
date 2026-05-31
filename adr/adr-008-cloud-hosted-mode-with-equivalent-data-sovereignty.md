---
confluence_id: "753792"
title: "ADR-008 — Cloud-Hosted Mode with Equivalent Data Sovereignty"
---

# ADR-008 — Cloud-Hosted Mode with Equivalent Data Sovereignty

## Status

| Field | Value |
| --- | --- |
| Status | <custom data-type="status" data-id="id-0">Accepted</custom> |
| Date | 27 May 2026 |
| Approved by | tech-lead (Reza Jahankohan) |
| Supersedes | None (founding ADR) |
| Superseded by | None |
| Driving artifact | [Section 7 — Portability Story](https://oraclous.atlassian.net/wiki/spaces/OP/pages/753728) |

## Context

Oraclous ships in two deployment modes. **Self-hosted** is the easy case for data sovereignty: the customer runs the entire platform on their own infrastructure, holds all keys, and Oraclous-the-company has no operational access. The harder case is **cloud-hosted**: Oraclous operates the platform on infrastructure it controls, on behalf of customers. The data sovereignty story has to survive this case, or the platform's positioning is hollow whenever the customer chooses managed hosting.

The conventional managed-SaaS model treats operator access as a routine necessity: the operator needs to be able to read customer data for support, debugging, recovery, compliance investigations, and operational improvement. The operator's access is limited by policy and audited, but not by cryptography. This model is reasonable for many SaaS products and unacceptable for Oraclous, because the customers most attracted to the platform's positioning are precisely the ones who do not want to depend on Oraclous-the-company's good behaviour, employee vetting, or legal exposure.

The alternative — promising operator-separation enforced by cryptography — raises immediate questions. How does support work? How do incidents get debugged? How are upgrades performed? What happens when a customer's keys are unavailable? Each question has an answer, but the answers shape the operational design, and the answers must be in writing because the commitment they support is load-bearing for the platform's positioning.

## Decision

Cloud-hosted Oraclous delivers **equivalent data sovereignty** to self-hosted Oraclous. The substance of the commitment:

* Customer state at rest (substrate database rows, OHM documents, prompt assets, audit-log payload bodies, BYOM credentials) is encrypted under key material the customer controls. The customer's keys are not held by Oraclous in any form that Oraclous staff can use to decrypt them unilaterally.
* Customer state in transit between the customer and the platform is TLS-protected with conventional public-key TLS; the keys handled at the substrate (after TLS termination) are envelope-encrypted with customer-controlled material before persistence.
* Customer state in flight inside the platform (in process memory during execution) is decrypted only within ephemeral execution contexts, with structured logging and audit that omits payload bodies unless the customer's audit-level policy explicitly permits them; even then, payload bodies in audit storage are encrypted with customer key material.
* Oraclous staff cannot decrypt customer state by virtue of operating the platform. Decryption requires customer-controlled key material the customer has not provided to Oraclous in a usable form.
* This commitment does not promise the platform will be available; it promises that if it is unavailable, customer data does not become available to anyone who should not have it.

Operational consequences:

* Support and debugging happen with the customer's participation, not in lieu of it. Oraclous staff can see structured metadata (which harness executed, when, with what outcome, what error category) but not payload bodies.
* Recovery from data loss is the customer's responsibility for customer data; Oraclous's responsibility is platform availability and metadata.
* Customers who want operator-accessible debugging can opt into a lower-isolation tier on a per-organisation basis. This is an explicit, audited opt-in — not the default.

## Alternatives considered

### A. Standard managed-SaaS model (operator access by policy, not cryptography)

Operator access is the norm; access is limited by access control and audited. Familiar, well-understood, fits most operations teams. Rejected because it fails the platform's positioning at exactly the customer segments the platform is designed for. If the answer to "can Oraclous staff read my data?" is "yes, but they're not supposed to", the platform has nothing to differentiate it from existing offerings.

### B. Operator-separation only for the most sensitive customers (premium tier)

Make operator-separation a premium tier; the default tier is conventional managed SaaS. Considered as a commercial structure. Rejected because the default tier becomes the platform's centre of gravity, and the centre of gravity ends up with conventional positioning. Operator-separation should be the default; opt-out for customers who want it is acceptable.

### C. Self-hosted only; no cloud-hosted mode in v1

Cleanest data-sovereignty story but a hard sale: many customers (especially smaller ones, especially in early adoption) want managed hosting. Rejected because it forecloses the segment of customers who want the platform's value _and_ managed operations. The two-mode commitment with equivalence is harder than either alone but expresses the platform's actual position.

### D. Cloud-hosted with full encryption but operator-recoverable keys (key escrow)

Customer keys are escrowed with Oraclous; under a documented break-glass procedure, Oraclous can recover and use them. Considered seriously because it solves operational edge cases (customer loses all their keys; legal subpoena addressed to Oraclous). Rejected because the escrow becomes the weak point: any process that can recover keys for any reason is a process that can be compelled, subverted, or accidentally invoked. Equivalence requires that the platform's mechanisms cannot recover customer keys.

## Consequences

### Positive

* The platform's positioning is honest in both deployment modes. A customer can choose cloud-hosted without giving up the data-sovereignty story.
* [Threat T6 (operator-separation breach)](https://oraclous.atlassian.net/wiki/spaces/OP/pages/983129) has a concrete, testable contract: no code path can decrypt customer state with operator-controllable material. [security-architect](https://oraclous.atlassian.net/wiki/spaces/OP/pages/557195)'s credential-and-isolation review skill has a clear pass/fail criterion.
* Regulatory conversations are simpler: the data does not become available to Oraclous, so most data-protection regimes treat Oraclous as a processor in a constrained way rather than a controller.
* The cloud-hosted and self-hosted modes share most of the platform code. The differences are at the operational fringe (deployment, monitoring, billing) rather than at the data path.

### Negative

* Operations are harder. Operator-led debugging without payload access requires customers to participate in incident response with structured information sharing, not "send us your logs". Operations runbooks (devops-implementer + docs-writer) must encode this from day one.
* Some support and improvement workflows become impossible without explicit customer participation. The customer gains sovereignty; they pay for it in operational friction.
* Edge cases (customer keys lost, customer organisation dissolved) have to be answered in writing in the operator-facing guides. The answers are not all comfortable; the platform's position is that comfort and sovereignty are in tension, and the platform prioritises sovereignty.
* The opt-out path (lower-isolation tier) creates a second operational mode the platform must support, with a clear audit trail of which organisations are opted in and why.

## Implementation notes

* Customer KMS integration is foundational. Phase 1 ships with two integrations (a major cloud-provider KMS and a self-managed HSM option) with a documented adapter pattern for additional integrations.
* Audit-log storage encrypts payload bodies (when audit level is `full`) under customer keys. Metadata (principal, action, resource, outcome, organisation_id, timestamp) is stored in a form Oraclous can index for operational queries.
* Substrate code paths touching BYOM credentials or KMS keys are explicitly listed in a documented inventory; security-architect maintains it. New paths require explicit review.
* The opt-out path (lower-isolation tier) is a per-organisation flag on the substrate, audit-logged at every read of that flag, with an explicit ADR-revision process to add new opt-out tiers.
* The conformance contract between cloud-hosted and self-hosted modes is tested as part of every release: the same test suite runs against both modes; divergence is an ADR-level decision.

## References

* [Section 7 — Portability Story](https://oraclous.atlassian.net/wiki/spaces/OP/pages/753728)
* [ADR-007](https://oraclous.atlassian.net/wiki/spaces/OP/pages/720920) — BYOM credential handling, the most sensitive case of operator-separation
* [ADR-006](https://oraclous.atlassian.net/wiki/spaces/OP/pages/393403) — organisation tenancy; the unit at which operator-separation is enforced
* [Structured Threat Catalogue](https://oraclous.atlassian.net/wiki/spaces/OP/pages/983129) — T6 (operator-separation breach), T1 (data exfiltration), T7 (audit-log gap)
* [Structured Governance Taxonomy](https://oraclous.atlassian.net/wiki/spaces/OP/pages/688439) — production policy sets encode the audit and egress constraints that interlock with this ADR

## Revision history

| Date | Change |
| --- | --- |
| 27 May 2026 | Initial publication in uniform ADR template. |
