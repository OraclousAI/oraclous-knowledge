---
confluence_id: "688523"
title: "R-Compliance — Cloud-mode compliance track"
---

# R-Compliance — Cloud-mode compliance track

| Release ID | RC |
| --- | --- |
| Status | <custom data-type="status" data-id="id-0">Planned</custom> |
| --- | --- |
| Window | Parallel from R0.5 onward; first certifications expected after R8 closes, with the SOC 2 Type II audit window extending past R8 by the auditor's required observation period (typically 6-12 months) |
| --- | --- |
| Owner | [tech-lead](https://oraclous.atlassian.net/wiki/spaces/OP/pages/983101) |
| --- | --- |
| Briefer | [security-architect](https://oraclous.atlassian.net/wiki/spaces/OP/pages/557195) |
| --- | --- |
| Dependencies | R0.5 (organisation tenancy is the cloud-mode prerequisite — the audit window cannot open before tenancy enforcement exists) |
| --- | --- |

## Goal

Achieve ISO 27001 and SOC 2 Type II certifications for the cloud-hosted deployment mode. The engineering work in R0 through R8 produces _evidence_ for these certifications; this release tracks the audit engagement, the operational controls documentation, the observation period, and the customer-facing attestation reports. Self-hosted customers do not require this work — they operate their own deployment and their own compliance posture; cloud customers receive the certifications as evidence of Oraclous-the-company's operational commitments.

## Scope

### In scope

* Audit firm selection and engagement (begins during R0.5)
* ISO 27001 scope agreement and gap assessment
* SOC 2 Type II observation period — typically 6-12 months from the time controls are mature
* Security controls documentation as formal policies (the Section 6.5 mitigations expressed in the auditor's required format)
* Operational controls implementation that engineering does not directly produce: access management, change management, incident response, business continuity, supplier management, vulnerability management
* Internal audit programme: scheduled reviews, evidence collection, remediation tracking
* Customer-facing attestation reports: SOC 2 Type II report shareable under NDA, ISO 27001 certificate publishable
* Trust centre setup: a public-facing page describing the platform's compliance posture and how to request attestation reports

### Out of scope

* Engineering deliverables — those are R0 through R8
* HIPAA, FedRAMP, or other certifications beyond ISO 27001 and SOC 2 Type II — deferred to future releases driven by customer demand
* Self-hosted compliance — that is the customer's concern

## Deliverables

- [ ] **Audit firm engaged** — verified by signed engagement letter; firm has SOC 2 and ISO 27001 expertise and is acceptable to enterprise customer base
- [ ] **Gap assessment complete** — verified by firm-produced gap report against ISO 27001 Annex A controls and SOC 2 Trust Services Criteria; remediation plan documented and prioritised
- [ ] **Security policies documented** — verified by a complete policy set covering access control, change management, incident response, business continuity, supplier management, vulnerability management, secure development, data handling, and acceptable use; policies reviewed and approved by tech-lead
- [ ] **Operational controls implemented** — verified by every control in the policy set having a documented procedure, an owner, and evidence of execution; access reviews run quarterly, change tickets follow approval workflow, incident response procedures rehearsed
- [ ] **Internal audit programme live** — verified by quarterly internal audits against the policy set; findings logged with owner and due date; remediation tracked to closure
- [ ] **SOC 2 Type II observation window opened** — verified by audit firm confirming controls are mature enough to begin observation; observation period running
- [ ] **ISO 27001 certification achieved** — verified by certification body issuing certificate; certificate is publishable on the trust centre
- [ ] **SOC 2 Type II report delivered** — verified by signed Type II report covering the full observation window; report shareable with enterprise customers under NDA
- [ ] **Trust centre live** — verified by a public page on oraclous.com describing the compliance posture, the certifications held, and how to request attestation reports under NDA

## Architecture references

* [Section 8 — Parallel track: Cloud-mode compliance work](https://oraclous.atlassian.net/wiki/spaces/OP/pages/688329)
* [Section 6.5 — Security Threats and Mitigations](https://oraclous.atlassian.net/wiki/spaces/OP/pages/851990) — the engineering evidence base for the auditor
* [ADR-008](https://oraclous.atlassian.net/wiki/spaces/OP/pages/753792) — Cloud-Hosted Mode with Equivalent Data Sovereignty

## ADRs implemented

* [ADR-008](https://oraclous.atlassian.net/wiki/spaces/OP/pages/753792) — R-Compliance is the operationalisation of ADR-008's compliance commitments

## Threats addressed

R-Compliance does not directly implement Tn-Mn mitigations from the Structured Threat Catalogue. Instead, it produces auditable evidence that the mitigations implemented in R0 through R8 are operationally effective. The engineering releases satisfy "the control exists"; R-Compliance satisfies "the control has operated over the audit window with documented evidence."

## Governance impact

R-Compliance does not change the Governance Taxonomy — it adds external attestation of the taxonomy's operational effectiveness. Cloud customers can rely on the certifications as third-party evidence of platform commitments. Self-hosted customers continue to operate their own compliance posture; the platform makes self-hosted compliance easier by providing the same controls infrastructure but does not certify the customer's self-hosted deployment.

## Risks

| Risk | Likelihood | Mitigation | Owner |
| --- | --- | --- | --- |
| Audit firm finds material gaps that delay certification by quarters | Medium | Gap assessment runs early (during R0.5) so remediation has time to land alongside engineering. Pre-audit readiness review by the firm before observation opens. | tech-lead + security-architect |
| Engineering releases slip and push the observation window start past the engineering window close | Medium | Observation can begin on a defined subset of controls; subsequent controls join the observation window as they mature. Auditor consulted on partial observation models acceptable to enterprise customers. | tech-lead |
| Operational controls (change management, incident response, access reviews) are documented but not actually followed | High | Internal audit programme runs quarterly and produces findings. Findings track to closure. Lack of evidence is treated as a release-blocking issue for subsequent observation periods. | security-architect |
| A customer requires HIPAA, FedRAMP, or another framework not in v1 scope | Medium | Customer requirements are documented as inputs to future release planning. The R-Compliance work establishes the controls foundation; additional frameworks build on it rather than starting over. | tech-lead |
| An incident during the observation window invalidates evidence and forces re-observation | Medium | Incident response procedures include audit-evidence preservation. Some incidents reset specific control evidence; others (with documented remediation) are acceptable to auditors. Auditor consulted on edge cases. | tech-lead + security-architect |

## Dependencies

**Upstream:** R0.5 (cloud-mode prerequisite). R1, R3, R4, R6, R8 produce direct evidence for specific controls.

**Downstream:** None — R-Compliance is the terminal release in this cycle. Future compliance work (HIPAA, FedRAMP, regional certifications) builds on the foundation established here.

## Sprint references

R-Compliance is not Jira-ticket-shaped in the same way as the engineering releases. Audit milestones, policy reviews, gap remediation, and observation-window evidence collection are tracked in a parallel Confluence subspace (to be created when R-Compliance enters active work). Engineering work that contributes evidence is tracked via the engineering releases as usual.

## Revision history

| Date | Change | Author | Reason |
| --- | --- | --- | --- |
| 27 May 2026 | Page created with the canonical release-page template | tech-lead (via Group D follow-up 3) | Establish R-Compliance as the parallel cloud-mode compliance track; matches Section 8 "Parallel track: Cloud-mode compliance work" |
