# Structured Threat Catalogue

**Document status:** Accepted · **Version:** 1.1 · **Anchored by:** Section 6.5

This page is the authoritative, structured catalogue of platform threats.

## 1. How the catalogue is used

Every story brief carries threat tags from this catalogue (T1–T7). For each tagged threat: the brief lists threats touched, security-architect verifies mitigations, test-author writes tests against the markers, and Operations monitors detection signals.

## 2. Catalogue

### T1 — Data exfiltration

An attacker reads organisation data they should not have access to, via a misrouted query, ReBAC bypass, or storage misconfiguration.

**Mitigations:**
- T1-M1: Every substrate storage operation parameterised by `organisation_id` from authenticated principal context
- T1-M2: ReBAC check at every cross-organisation traversal boundary; fail-closed default
- T1-M3: Row-level security in the storage layer as defense-in-depth backstop

**Required tests:** `@pytest.mark.isolation`, `@pytest.mark.organization_isolation`

**Severity:** critical

### T2 — Privilege escalation

A principal performs an action that their granted ReBAC relations do not permit.

**Mitigations:**
- T2-M1: Every capability rechecks principal relations at invocation time
- T2-M2: ReBAC relation revocations propagate within seconds
- T2-M3: Capability descriptors declare required relations; runtime refuses absent them

**Required tests:** `@pytest.mark.security`, `@pytest.mark.rebac`

**Severity:** high

### T3 — Model-provider compromise

A BYOM provider returns malicious or manipulated responses.

**Mitigations:**
- T3-M1: TLS-pinned transport to provider endpoints
- T3-M2: BYOM credentials encrypted at rest under the organisation's KMS
- T3-M3: Tool calls validated against the harness's capability allowlist before execution
- T3-M4: Egress allowlist per policy set

**Severity:** high

### T4 — Capability poisoning

A capability published in a registry behaves maliciously when invoked.

**Mitigations:**
- T4-M1: Every capability descriptor is content-hashed; runtime refuses hash mismatches
- T4-M2: Federated capabilities gated by ReBAC federation agreements
- T4-M3: Policy-set egress allowlist enforced regardless of capability declaration

**Severity:** high

### T5 — Manifest tampering

An attacker modifies an OHM document between publication and execution.

**Mitigations:**
- T5-M1: All non-development OHMs require signatures
- T5-M2: Canonical serialisation rules make signature surfaces deterministic
- T5-M3: OHM storage writes require ReBAC relation to the owning organisation

**Required tests:** `@pytest.mark.security`, `@pytest.mark.ohm_signature`

**Severity:** critical

### T6 — Operator-separation breach

Oraclous-the-company staff gain the ability to decrypt customer data in cloud-hosted deployments.

**Mitigations:**
- T6-M1: Customer KMS keys in customer-controlled key material
- T6-M2: BYOM credentials encrypted with customer key material
- T6-M3: Audit-log payload bodies encrypted under the customer's KMS
- T6-M4: Every new code path touching credentials requires explicit security-architect review
- T6-M5: Usage-event `dimensions` structurally constrained to bounded scalar metering metadata (MAX_DIMENSION_KEY_LENGTH=64, MAX_DIMENSION_VALUE_LENGTH=256, MAX_DIMENSIONS=16)

**Required tests:** `@pytest.mark.security`, `@pytest.mark.operator_separation`

**Severity:** critical

### T7 — Audit-log gap

A platform action that should be audit-logged is not.

**Mitigations:**
- T7-M1: Every substrate state change emits a structured audit event
- T7-M2: Every capability invocation emits an audit event
- T7-M3: Every BYOM call emits an audit event
- T7-M4: Audit storage retention follows the policy set's `retention_days`

**Required tests:** `@pytest.mark.audit`

**Severity:** medium (force-multiplier for all other threats)

## 6. Change history

| Version | Date | Change |
| --- | --- | --- |
| 1.0 | 27 May 2026 | Initial catalogue. T1-T7 codified. |
| 1.1 | 31 May 2026 | T6-M5 added — usage-event dimensions as bounded scalar metering metadata. |
