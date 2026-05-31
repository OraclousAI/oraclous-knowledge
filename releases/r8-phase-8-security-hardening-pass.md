---
confluence_id: "66060"
title: "R8 — Phase 8: Security hardening pass"
---

# R8 — Phase 8: Security hardening pass

| Release ID | R8 |
| --- | --- |
| Status | <custom data-type="status" data-id="id-0">Planned</custom> |
| --- | --- |
| Window | Weeks 33-36 |
| --- | --- |
| Owner | [tech-lead](https://oraclous.atlassian.net/wiki/spaces/OP/pages/983101) |
| --- | --- |
| Briefer | [security-architect](https://oraclous.atlassian.net/wiki/spaces/OP/pages/557195) |
| --- | --- |
| Dependencies | R0–R7 (every layer must be in target shape before the hardening pass; the compiler must exist before consciousness drift can be measured) |
| --- | --- |

## Goal

Implement the Phase 2 (hardening) and Phase 3 (advanced) mitigations from Section 6.5's phased mitigation plan that were not yet covered by earlier releases. Bring the platform's shipped security posture to parity with the architecture's documented commitments. After this release, every Tn-Mn entry from the Structured Threat Catalogue is implemented or has a documented compensating control.

## Scope

### In scope

* Indirect prompt injection sanitization extensions: capability inputs and outputs pass through sanitisation patterns that strip embedded prompt-injection markers
* Output redaction extensions: custom pattern support so customers can declare workspace-specific redaction rules beyond the platform defaults
* Cross-workspace traversal audit reports: scheduled reports that surface federation patterns suggestive of data laundering (T9.2)
* Service account principal type hardening: service accounts cannot delegate to agents; service-account-initiated executions have stricter HITL defaults
* Cache key isolation audits: scheduled checks that no cache key spans organisations; alerts on violation
* Consciousness drift detection: statistical baselines for agent behaviour; automated detection of drift patterns; periodic consciousness audits with anomaly reports
* Federation laundering audit reports: detection of high-volume cross-workspace reads followed by writes to less-restricted workspaces
* Adapter output validation: every adapter (Claude Code, MCP, OpenAPI) validates its output against the OHM spec; malformed output triggers a rejection with structured diagnostics
* Schedule storm protection: per-organisation rate limits on scheduled wake-ups; backoff on repeated failures; jitter on cron firing
* Penetration testing pass on the gateway and MCP server surfaces

### Out of scope

* SOC 2 Type II audit completion (R-Compliance — runs in parallel)
* ISO 27001 certification (R-Compliance)
* New mitigation categories not in Section 6.5 — these would be a v2 architecture revision

## Deliverables

- [ ] **Indirect prompt injection sanitisation live** — verified by integration tests where capability outputs containing embedded prompt-injection markers are sanitised before reaching downstream agents; test corpus from public injection databases passes
- [ ] **Custom output redaction patterns supported** — verified by a workspace declaring a custom regex; the runtime applies it on every dispatched output; provenance captures redaction applications
- [ ] **Cross-workspace traversal audit reports live** — verified by scheduled reports running daily; reports surface federation patterns above a configurable threshold; workspace admins can review
- [ ] **Service account hardening live** — verified by a test that proves a service account cannot mint a delegated token for an agent; service-account-initiated executions trigger HITL on every privileged transition
- [ ] **Cache key isolation audits live** — verified by a scheduled check across Redis and in-memory caches; any cross-org key triggers an alert and is logged for review
- [ ] **Consciousness drift detection live** — verified by behavioural baselines computed per agent over its operational history; drift beyond bounded thresholds surfaces as a security event in the workspace admin's queue
- [ ] **Federation laundering reports live** — verified by reports surfacing the read-then-write-to-less-restricted pattern; false positives bounded by configurable thresholds
- [ ] **Adapter output validation live** — verified by every shipped adapter rejecting malformed output rather than producing invalid OHM; malformed inputs logged with the original payload for review
- [ ] **Schedule storm protection live** — verified by integration tests where a deliberate burst of cron firings is rate-limited per organisation; backoff applied on repeated failures
- [ ] **Penetration testing pass** — verified by external pen-test report against the gateway and MCP server; all critical and high findings remediated before R8 closes

## Architecture references

* [Section 8 — Phase 8](https://oraclous.atlassian.net/wiki/spaces/OP/pages/688329)
* [Section 6.5 — Security Threats and Mitigations](https://oraclous.atlassian.net/wiki/spaces/OP/pages/851990) — the source of every R8 deliverable
* [Structured Threat Catalogue](https://oraclous.atlassian.net/wiki/spaces/OP/pages/983129) — Tn-Mn IDs implemented here

## ADRs implemented

* No new ADRs — R8 closes out implementations of decisions already recorded in [ADR-006](https://oraclous.atlassian.net/wiki/spaces/OP/pages/393403), [ADR-008](https://oraclous.atlassian.net/wiki/spaces/OP/pages/753792), and the threat-driven review patterns documented in security-architect's skill.

## Threats addressed

| Threat | Mitigation IDs implemented | Coverage |
| --- | --- | --- |
| T3 — Prompt injection / capability misuse | T3-M4 (indirect prompt injection sanitisation extensions) | Closes T3 |
| T4 — Resource exhaustion | T4-M2 (schedule storm protection), T4-M3 (per-organisation rate limits) | Closes T4 |
| T6 — Operator-separation breach | T6-M4 (cache key isolation audits as a defence-in-depth backstop) | Closes T6 |
| T7 — Audit-log gap | T7-M3 (cross-workspace traversal audit reports), T7-M4 (federation laundering reports) | Closes T7 with the audit-side reporting |
| T6.2 — Consciousness drift | T6.2-M1 (consciousness drift detection) | Closes T6.2 (Section 6.5 Phase 3 advanced) |
| T9.2 — Federation laundering | T9.2-M1 (federation laundering audit reports) | Closes T9.2 (Section 6.5 Phase 3 advanced) |

## Governance impact

R8 closes the gap between the Governance Taxonomy's documented controls and the platform's shipped enforcement. After R8, every policy set in the taxonomy is enforceable end to end. Workspace admins can declare custom redaction patterns and have them apply uniformly. Cross-workspace traversal is auditable in addition to being permission-gated. The platform's commitments are now demonstrable, not aspirational.

## Risks

| Risk | Likelihood | Mitigation | Owner |
| --- | --- | --- | --- |
| Sanitisation patterns introduce false positives that block legitimate capability outputs | High | Patterns ship in shadow mode first (log but do not block) for a calibration period; thresholds tuned against real workspace traffic before enforcement is enabled. | security-architect |
| Consciousness drift detection produces too many false anomalies and is ignored | High | Baselines require N weeks of operational history before drift is reportable; thresholds are conservative; workspace admins can tune them; anomalies are surfaced with explanatory context not just raw scores. | security-architect |
| Penetration test surfaces critical findings that delay R8 | Medium | R8 has a 4-week window. If pen-test findings require more time than that, the release ships with the implementable mitigations and a follow-up release covers the remainder. R-Compliance can begin observation independently. | security-architect + tech-lead |
| Audit report volume overwhelms workspace admins | Medium | Reports default to weekly aggregates rather than per-event alerts. Workspace admins can subscribe to specific event types. Thresholds tunable. | security-architect |

## Dependencies

**Upstream:** R0–R7 (every prior release; consciousness drift requires the compiler and consciousness primitives from R5/R7).

**Downstream:** R-Compliance (R8 evidence feeds SOC 2 Type II audit). Phase 9 ongoing — post-R8 improvements are continuous, not release-gated.

## Sprint references

Jira epics to be created during Group E.

## Revision history

| Date | Change | Author | Reason |
| --- | --- | --- | --- |
| 27 May 2026 | Page created with the canonical release-page template | tech-lead (via Group D follow-up 3) | Establish R8 as the security hardening pass release; matches Section 8 Phase 8 |
