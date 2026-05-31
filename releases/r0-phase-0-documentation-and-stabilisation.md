---
confluence_id: "622878"
title: "R0 — Phase 0: Documentation and stabilisation"
---

# R0 — Phase 0: Documentation and stabilisation

| Release ID | R0 |
| --- | --- |
| Status | <custom data-type="status" data-id="id-0">Released</custom> |
| --- | --- |
| Window | Weeks 1-2 (effectively complete with Architecture v1.1 lock + Group B + Group C) |
| --- | --- |
| Owner | [tech-lead](https://oraclous.atlassian.net/wiki/spaces/OP/pages/983101) |
| --- | --- |
| Briefer | [solution-architect](https://oraclous.atlassian.net/wiki/spaces/OP/pages/164068) |
| --- | --- |
| Dependencies | None (this is the foundation release) |
| --- | --- |

## Goal

Lock the platform architecture before any code reorganisation begins, so every subsequent release has a stable contract to execute against. Without this release's outputs, downstream agents would design against a moving target and the migration would accumulate silent drift.

## Scope

### In scope

* Platform Architecture document v1.1 (Sections 1-9) locked and published
* The eleven founding Architecture Decision Records (ADR-001 through ADR-011) drafted, accepted, and uniformly templated
* Three structured artifacts extracted from prose into machine-readable form: OHM v1.0 Standalone Specification, Structured Governance Taxonomy, Structured Threat Catalogue
* The eleven agent skill pages (Group A) establishing the working team
* The Agent Skills Catalogue and Agent and Skill Change Log
* The Architecture Revision History
* This Releases hub establishing how subsequent phases are planned and tracked

### Out of scope

* Any code reorganisation (deferred to R0.5 onward)
* Any new platform features (deferred to R7 for the compiler harness; everything else is pre-existing functionality being reorganised)
* External agent integrations beyond Jira and Confluence (deferred indefinitely — see [Section 9](https://oraclous.atlassian.net/wiki/spaces/OP/pages/65988))

## Deliverables

- [x] **Architecture v1.1 locked** — verified by all nine sections published under [Platform Architecture v1.1](https://oraclous.atlassian.net/wiki/spaces/OP/pages/753707) with tech-lead sign-off recorded in the Revision History
- [x] **11 founding ADRs accepted and uniformly templated** — verified by all eleven pages under [02. ADRs](https://oraclous.atlassian.net/wiki/spaces/OP/pages/589826) carrying `Accepted` status and the standard template (Status / Context / Decision / Alternatives / Consequences / Implementation notes / References / Revision history)
- [x] **OHM v1.0 Standalone Specification published** — verified by the spec at [page 393501](https://oraclous.atlassian.net/wiki/spaces/OP/pages/393501) containing field-by-field semantics, canonical serialisation rules, reference resolution semantics, versioning commitments, and typed error categories
- [x] **Structured Governance Taxonomy published** — verified by the catalogue at [page 688439](https://oraclous.atlassian.net/wiki/spaces/OP/pages/688439) containing the five founding policy sets in YAML with field semantics and enforcement points
- [x] **Structured Threat Catalogue published** — verified by the catalogue at [page 983129](https://oraclous.atlassian.net/wiki/spaces/OP/pages/983129) containing T1-T7 with attack chains, mitigations with stable IDs, required tests with markers, and detection signals
- [x] **Agent team established** — verified by 11 agent skill pages published under [Agent Skills Catalogue](https://oraclous.atlassian.net/wiki/spaces/OP/pages/753852) with the standard skill structure
- [x] **Architecture Revision History established** — verified by the audit-trail page at [page 426111](https://oraclous.atlassian.net/wiki/spaces/OP/pages/426111) with all foundational entries recorded
- [x] **Releases hub established** — verified by this hub ([09. Releases](https://oraclous.atlassian.net/wiki/spaces/OP/pages/164160)) and its child pages existing with the release-page template applied
- [x] **Agent identity convention established** — verified by Section 6 of the Releases hub documenting `Agent Owner` and the comment-prefix protocol, and each agent skill page including an Agent Identity Convention section

## Architecture references

* [Platform Architecture v1.1](https://oraclous.atlassian.net/wiki/spaces/OP/pages/753707) — the document this release locks
* [02. ADRs](https://oraclous.atlassian.net/wiki/spaces/OP/pages/589826) — the parallel decision-record audit trail
* [OHM v1.0 Standalone Specification](https://oraclous.atlassian.net/wiki/spaces/OP/pages/393501)
* [Structured Governance Taxonomy](https://oraclous.atlassian.net/wiki/spaces/OP/pages/688439)
* [Structured Threat Catalogue](https://oraclous.atlassian.net/wiki/spaces/OP/pages/983129)

## Threats addressed

None directly — this release establishes the threat-mitigation _infrastructure_ (the Threat Catalogue, the security-architect agent, the threat-driven review skill) that subsequent releases use to address specific threats. R0's contribution to the threat surface is structural, not behavioural.

## Governance impact

Establishes the Structured Governance Taxonomy with its five founding policy sets. No policy enforcement happens in R0 — that begins in R0.5 (organisation tenancy enforcement) and R2 (capability-registry-level enforcement). R0 publishes the catalogue against which later releases enforce.

## Risks

| Risk | Likelihood | Mitigation | Owner |
| --- | --- | --- | --- |
| Architecture document drifts from intent before code work begins | Low (R0 is short) | All material changes go through the Architecture Revision History; tech-lead sign-off required on every section revision | tech-lead |
| ADRs are inconsistent in template or framing across the eleven | Medium | All 11 templated uniformly during Group C; deviations are revision entries, not silent edits | solution-architect |
| Structured artifacts are written in a way that drifts from the prose sections | Medium | Each Section that has an artifact gets a callout block linking to the artifact and framing narrative-vs-contract authority; Sections 4, 6, 6.5 already done in Group C, Sections 2/3/5/7/8 done in Group D follow-up (2) | solution-architect |

## Dependencies

**Upstream:** None (foundation release).

**Downstream:** Every other release in this hub depends on R0 being complete. No release should proceed past Planned until R0 is Released.

## Sprint references

R0 was executed before the Releases hub existed. The work is recorded retrospectively here. Jira ticket creation was not used for R0 itself — the work was tracked directly in the Confluence pages produced. From R0.5 onward, every release generates Jira epics.

## Revision history

| Date | Change | Author | Reason |
| --- | --- | --- | --- |
| 27 May 2026 | Page created as retrospective record of R0; status set to Released | tech-lead (via Group D follow-up 3) | Establish the release-page record for the foundation work so the Releases hub has a complete history from R0 onward |
