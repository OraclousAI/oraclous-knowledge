---
confluence_id: "983129"
title: "Structured Threat Catalogue"
---

# Structured Threat Catalogue

**Document status:** <custom data-type="status" data-id="id-0">Accepted</custom> · **Version:** 1.2 · **Anchored by:** [Section 6.5 — Security Threats and Mitigations](https://oraclous.atlassian.net/wiki/spaces/OP/pages/851990)

This page is the authoritative, structured catalogue of platform threats. Section 6.5 of Platform Architecture v1.1 describes the threat model in prose; this page encodes the same threats in a machine-readable shape that [security-architect](https://oraclous.atlassian.net/wiki/spaces/OP/pages/557195) resolves against during threat-driven review. When the two disagree, the architecture document is authoritative for taxonomy and risk framing; this page is authoritative for the concrete mitigation, test, and detection contracts.

## 1. How the catalogue is used

Every story brief carries one or more threat tags from this catalogue (T1–T7). For each tagged threat:

1. The brief lists the threats touched.
2. security-architect verifies the listed mitigations are present in the proposed work.
3. test-author writes tests against the test markers named in the catalogue entry.
4. Operations monitors the detection signals named in the entry; an unexpected signal triggers incident response.

If a change introduces a new attack surface not covered by an existing category, security-architect updates this catalogue (with tech-lead sign-off) _before_ the change merges. See [security-architect](https://oraclous.atlassian.net/wiki/spaces/OP/pages/557195) Section 3.2 for the threat-catalogue maintenance skill.

## 2. Catalogue (YAML)

The canonical, machine-readable threat catalogue:

```yaml
# oraclous-threat-catalogue
# version: 1.2
# anchored: Section 6.5 of Platform Architecture v1.1
# updated: 2026-06-04

catalogue_version: "1.2"

threats:

  # ---------------------------------------------------------------
  - id: "T1"
    name: "Data exfiltration"
    one_line: >
      An attacker (external or internal) reads organisation data they
      should not have access to, via a misrouted query, ReBAC bypass,
      or storage misconfiguration.
    attack_chain:
      - "Attacker obtains a principal in organisation A"
      - "Attacker triggers a path that reads from substrate without organisation_id parameterisation, or with an attacker-controlled organisation_id"
      - "Substrate returns rows belonging to organisation B"
    prerequisites:
      - "A code path exists where organisation_id is missing, defaulted, or attacker-supplied"
      - "ReBAC enforcement is absent at that path"
    mitigations:
      - id: "T1-M1"
        description: "Every substrate storage operation is parameterised by organisation_id, sourced from the authenticated principal context, never from request body"
        enforcement_point: "substrate"
      - id: "T1-M2"
        description: "ReBAC check at every cross-organisation traversal boundary; fail-closed default on ambiguous resolution"
        enforcement_point: "substrate ReBAC layer"
      - id: "T1-M3"
        description: "Row-level security in the storage layer as a defense-in-depth backstop"
        enforcement_point: "substrate storage"
    required_tests:
      - markers: ["isolation", "organization_isolation"]
        scope: "every storage read and write path"
        assertion: "principal in organisation A cannot read rows owned by organisation B, regardless of request shape"
      - markers: ["isolation", "rebac"]
        scope: "every cross-organisation reference path"
        assertion: "absent a valid ReBAC relation, traversal returns fail-closed"
    detection_signals:
      - "Substrate query without organisation_id parameter (logged as warning)"
      - "ReBAC denial spike for a single principal (potential probing)"
      - "Storage read returns rows whose owner_organization_id mismatches the requesting context (terminate request, alert)"
    severity: "critical"
    blast_radius: "platform-wide if structural; single-organisation if local"

  # ---------------------------------------------------------------
  - id: "T2"
    name: "Privilege escalation"
    one_line: >
      A principal performs an action that their granted ReBAC relations
      do not permit, via a policy-evaluation bug, role-assignment race,
      or capability-permission mismatch; or a compromised container
      process escalates to root at the OS layer.
    attack_chain:
      - "Attacker has a low-privilege principal in their target organisation"
      - "Attacker invokes a capability that does not recheck the principal's relations at invocation time"
      - "Capability performs an action requiring higher privilege than the principal has"
    prerequisites:
      - "A capability that does not enforce per-invocation ReBAC"
      - "Or: a load-time check that does not refresh against revoked relations"
    mitigations:
      - id: "T2-M1"
        description: "Every capability rechecks principal relations at invocation time, not only at harness load time"
        enforcement_point: "harness runtime"
      - id: "T2-M2"
        description: "ReBAC relation revocations propagate within seconds; stale-relation tolerance is bounded and audited"
        enforcement_point: "substrate ReBAC layer"
      - id: "T2-M3"
        description: "Capability descriptors declare required relations; runtime refuses to invoke a capability against a principal lacking them"
        enforcement_point: "capability registry + harness runtime"
      - id: "T2-M4"
        description: "Service containers run as non-root system user `svc` in the runtime stage; root is unavailable at container runtime, limiting OS-layer privilege escalation if a container process is compromised (ORAA-234, PR #125)"
        enforcement_point: "container runtime (all service Dockerfiles)"
    required_tests:
      - markers: ["security", "rebac"]
        scope: "every capability invocation"
        assertion: "principal lacking a required relation is denied at invocation, not only at load"
      - markers: ["security", "rebac", "race"]
        scope: "relation-revocation race"
        assertion: "a relation revoked mid-execution causes the next capability invocation to fail"
    detection_signals:
      - "Capability invocation succeeds for a principal that lacks the declared required relation (alert)"
      - "Audit-log records principal performing actions inconsistent with their relation set"
    severity: "high"
    blast_radius: "single-organisation"

  # ---------------------------------------------------------------
  - id: "T3"
    name: "Model-provider compromise"
    one_line: >
      A BYOM provider returns malicious or manipulated responses,
      either via the provider being compromised, a man-in-the-middle on
      the transport, or a stolen credential being used to inject responses.
    attack_chain:
      - "Attacker compromises the provider channel (provider itself, transport, or credential)"
      - "Attacker returns responses crafted to manipulate the harness (prompt injection, tool-call injection, data exfiltration via tool args)"
      - "Harness acts on the malicious response"
    prerequisites:
      - "Lack of response validation"
      - "Or: lack of egress / tool-call restrictions on what the model can request"
    mitigations:
      - id: "T3-M1"
        description: "TLS-pinned transport to provider endpoints; certificate rotation handled via the BYOM credential envelope"
        enforcement_point: "harness runtime egress"
      - id: "T3-M2"
        description: "BYOM credentials encrypted at rest under the organisation's KMS; operator separation preserved per ADR-007 and ADR-008"
        enforcement_point: "substrate KMS integration"
      - id: "T3-M3"
        description: "Tool calls returned by the model are validated against the harness's capability allowlist before execution"
        enforcement_point: "harness runtime tool-call dispatch"
      - id: "T3-M4"
        description: "Egress allowlist per policy set restricts which destinations capabilities can reach, limiting exfiltration if a tool call is malicious"
        enforcement_point: "capability invocation"
    required_tests:
      - markers: ["security", "byom"]
        scope: "every BYOM credential path"
        assertion: "credential cannot be decrypted by Oraclous-the-company staff in cloud-hosted mode"
      - markers: ["security", "byom", "tool_dispatch"]
        scope: "tool-call dispatch"
        assertion: "model-returned tool call referencing a capability outside the harness's allowlist is rejected"
    detection_signals:
      - "Provider response containing tool calls for capabilities not in the harness allowlist (terminate, alert)"
      - "Provider response causing egress to a destination outside the allowlist (block, alert)"
      - "Sudden change in provider response statistical profile (length, structure) for a given harness (flag for review)"
    severity: "high"
    blast_radius: "single-harness if provider scoped; single-organisation if credential reused"

  # ---------------------------------------------------------------
  - id: "T4"
    name: "Capability poisoning"
    one_line: >
      A capability published in a registry behaves maliciously when
      invoked, either because the capability was always malicious, was
      compromised after publication, or was substituted via a registry
      lookup race.
    attack_chain:
      - "Attacker publishes a capability to a registry the target organisation trusts (or compromises an existing one)"
      - "Target harness references the capability and loads it"
      - "Capability performs malicious actions during invocation: exfiltration, side-channel, manipulation"
    prerequisites:
      - "A capability registry where unverified publishers are trusted"
      - "Or: missing integrity verification on capability descriptor retrieval"
    mitigations:
      - id: "T4-M1"
        description: "Every capability descriptor is content-hashed; harness load pins the hash; runtime refuses to load a descriptor whose hash mismatches"
        enforcement_point: "capability registry + harness runtime"
      - id: "T4-M2"
        description: "Capabilities from federated registries are gated by ReBAC federation agreements (ADR-004); cross-organisation capability invocation is never implicit"
        enforcement_point: "harness runtime federation gate"
      - id: "T4-M3"
        description: "Capability descriptors declare their egress requirements; the policy-set egress allowlist is enforced regardless of capability declaration"
        enforcement_point: "policy-set enforcement"
      - id: "T4-M4"
        description: "Capability behaviour anomalies (duration, error rate, egress pattern) are monitored; sustained anomalies surface in the security review queue"
        enforcement_point: "observability + security-architect review"
    required_tests:
      - markers: ["security", "capability_integrity"]
        scope: "capability descriptor retrieval"
        assertion: "a tampered descriptor (hash mismatch) is rejected at load"
      - markers: ["security", "federation"]
        scope: "federated capability invocation"
        assertion: "absent a federation agreement, federated:* capability resolution fails"
    detection_signals:
      - "Descriptor hash mismatch on retrieval (block, alert)"
      - "Capability egress to a destination outside its declared list (block, alert)"
      - "Capability invocation anomaly metric exceeds threshold (flag for review)"
    severity: "high"
    blast_radius: "every harness that loads the poisoned capability"

  # ---------------------------------------------------------------
  - id: "T5"
    name: "Manifest tampering"
    one_line: >
      An attacker modifies an OHM document between publication and
      execution, changing its capabilities, models, prompts, or
      governance bindings.
    attack_chain:
      - "Attacker gains write access to the substrate's OHM storage, or intercepts an OHM in transit"
      - "Attacker modifies the OHM (adds a capability, weakens governance, swaps a prompt)"
      - "Runtime loads the tampered OHM and executes it under its forged identity"
    prerequisites:
      - "Lack of signature requirement, or trust in a signing root the attacker controls"
      - "Or: ability to write to OHM storage without ReBAC enforcement"
    mitigations:
      - id: "T5-M1"
        description: "All non-development OHMs require signatures from the policy set's trusted_signature_roots (see Structured Governance Taxonomy)"
        enforcement_point: "harness load"
      - id: "T5-M2"
        description: "OHM canonical serialisation rules (see OHM v1.0 Spec Section 5) make signature surfaces deterministic; signature verification is exact-match"
        enforcement_point: "harness load OHMSignatureError"
      - id: "T5-M3"
        description: "OHM storage writes require ReBAC relation to the owning organisation; cross-organisation OHM writes are denied"
        enforcement_point: "substrate ReBAC layer"
      - id: "T5-M4"
        description: "Signed OHMs are stored alongside their signatures; storage integrity is verified on read"
        enforcement_point: "substrate OHM storage"
    required_tests:
      - markers: ["security", "ohm_signature"]
        scope: "OHM load on signed harness"
        assertion: "tampered OHM (any field altered) fails signature verification"
      - markers: ["security", "ohm_signature"]
        scope: "OHM load on unsigned harness against a require_signature policy set"
        assertion: "load fails with OHMSignatureError"
      - markers: ["security", "isolation"]
        scope: "OHM storage write"
        assertion: "principal cannot write OHM owned by another organisation"
    detection_signals:
      - "OHMSignatureError on a previously-loaded OHM (alert: storage may be corrupted)"
      - "Unsigned OHM loaded under a production policy set (block, alert; should be impossible)"
      - "OHM storage write attempt across organisations (block, alert)"
    severity: "critical"
    blast_radius: "every execution of the tampered harness until detected"

  # ---------------------------------------------------------------
  - id: "T6"
    name: "Operator-separation breach"
    one_line: >
      Oraclous-the-company staff gain the ability to decrypt customer
      data, read customer BYOM credentials, or otherwise access
      customer state in cloud-hosted deployments, breaching the
      operator-separation guarantee from ADR-008.
    attack_chain:
      - "Code path is added (or existing path is modified) that places customer KMS keys, BYOM credentials, or plaintext customer data in a context Oraclous staff can access"
      - "Staff member (malicious or compelled) accesses the path"
      - "Customer data exposed to the operator"
    prerequisites:
      - "A code path where customer-encrypted data is decrypted with a key controllable by Oraclous staff"
      - "Or: logs / metrics / audit records that contain unencrypted customer payloads"
    mitigations:
      - id: "T6-M1"
        description: "Customer KMS keys live in customer-controlled key material; Oraclous KMS holds wrapping keys only when explicitly authorised by the customer per ADR-008"
        enforcement_point: "substrate KMS integration"
      - id: "T6-M2"
        description: "BYOM credentials encrypted with customer key material; substrate code paths that touch them are explicit, audited, and minimal"
        enforcement_point: "substrate BYOM envelope"
      - id: "T6-M3"
        description: "Audit-log payload bodies are encrypted under the customer's KMS; full-level audit (per Governance Taxonomy) is not staff-readable plaintext"
        enforcement_point: "substrate audit storage"
      - id: "T6-M4"
        description: "Every new code path touching customer credentials or KMS keys requires explicit security-architect review per the credential-and-isolation review skill"
        enforcement_point: "Tests Review + Code Review gates"
      - id: "T6-M5"
        description: "Usage-event `dimensions` (the ADR-009 substrate metering stream) are structurally constrained to bounded scalar metering metadata — bounded key length (MAX_DIMENSION_KEY_LENGTH = 64), bounded value length (MAX_DIMENSION_VALUE_LENGTH = 256), bounded cardinality (MAX_DIMENSIONS = 16), and a restricted key character class (no whitespace, newlines, or control characters). The per-organisation usage stream is operator-readable by design (ADR-009 cross-refs ADR-008) only because dimensions cannot carry plaintext customer payload; this mitigation is the structural enforcement of that property"
        enforcement_point: "substrate usage-event stream (`oraclous_substrate.usage.UsageEventStream.emit`)"
    required_tests:
      - markers: ["security", "operator_separation", "byom"]
        scope: "BYOM credential path"
        assertion: "credential ciphertext cannot be decrypted without customer-controlled key material"
      - markers: ["security", "operator_separation", "audit"]
        scope: "audit payload storage"
        assertion: "audit payload at-rest is encrypted under customer key; staff principal cannot decrypt"
      - markers: ["security", "operator_separation"]
        scope: "usage-event dimensions emission (`oraclous_substrate.usage`)"
        assertion: "nested mappings/lists, over-long values, over-long keys, whitespace/control-character keys, and over-cardinality maps are each rejected fail-closed — nothing is written to the usage stream. Reference tests: `test_dimensions_rejects_nested_customer_payload`, `test_dimension_value_length_is_bounded`, `test_dimension_key_length_is_bounded`, `test_dimension_key_rejects_whitespace_and_control_characters`, `test_dimensions_entry_count_is_capped`"
    detection_signals:
      - "New code path imports a KMS decryption call against customer-keyed material (review required at Code Review)"
      - "Audit payload retrieval by a staff principal (should be impossible; if observed, alert)"
      - "Plaintext customer payload in any log, metric, or trace output (block, alert; treat as incident) — this signal also covers T6-M5 (usage-event dimensions): the usage stream is included in the 'log, metric, or trace output' surface that must never carry customer payload"
    severity: "critical"
    blast_radius: "every cloud-hosted customer"

  # ---------------------------------------------------------------
  - id: "T7"
    name: "Audit-log gap"
    one_line: >
      A platform action that should be audit-logged is not, leaving no
      evidence trail for incident response, compliance review, or
      after-the-fact detection of any other threat.
    attack_chain:
      - "An attacker exploits any of T1-T6"
      - "The exploitation path does not emit the audit events needed to reconstruct it"
      - "Incident response or detection signals fire too late or not at all"
    prerequisites:
      - "A code path with state change or security-relevant action that does not emit a structured audit event"
      - "Or: audit events emitted but at the wrong level for the bound policy set"
    mitigations:
      - id: "T7-M1"
        description: "Every substrate state change emits a structured audit event with principal, action, resource, outcome, and organisation_id"
        enforcement_point: "substrate"
      - id: "T7-M2"
        description: "Every capability invocation emits an audit event at the policy set's audit level (summary / detailed / full)"
        enforcement_point: "harness runtime"
      - id: "T7-M3"
        description: "Every BYOM call emits an audit event with provider, model, outcome, token usage, latency"
        enforcement_point: "harness runtime model dispatch"
      - id: "T7-M4"
        description: "Audit storage retention follows the policy set's retention_days; expired events are deleted, not retained beyond retention"
        enforcement_point: "substrate audit storage lifecycle"
      - id: "T7-M5"
        description: "Audit completeness is verified by qa-engineer as a routine review concern; gaps surface as bugs"
        enforcement_point: "qa-engineer test-suite validation"
    required_tests:
      - markers: ["audit", "isolation"]
        scope: "every substrate state change"
        assertion: "an audit event is emitted with the expected fields"
      - markers: ["audit", "byom"]
        scope: "every BYOM call"
        assertion: "an audit event captures the provider, model, and outcome"
      - markers: ["audit"]
        scope: "audit retention"
        assertion: "events outside the retention window are removed; events inside are retrievable"
    detection_signals:
      - "Substrate state change without a corresponding audit event (test failure)"
      - "Capability invocation without corresponding audit event at expected level (test failure)"
      - "Audit-event volume drops significantly without a corresponding traffic drop (alert: pipeline failure)"
    severity: "medium when standalone; force-multiplier for all other threats"
    blast_radius: "depends on the underlying threat that is now untraceable"
```

## 3. Field semantics

| Field | Semantics |
| --- | --- |
| `id` | Stable threat identifier. T1–T7 are the founding categories. Future threats may extend (T8, T9, …) or sub-categorise (T1.1, T1.2, …) without renumbering the existing ones. |
| `name` | Short human-readable name. Used in brief tagging and review comments. |
| `one_line` | One-sentence summary; what an agent skim-reading the catalogue takes away. |
| `attack_chain` | Step-by-step description of how the threat realises in practice. Each step should be concrete enough that a tester can construct a failing test from it. |
| `prerequisites` | Conditions that must hold for the threat to be exploitable. Mitigations break the prerequisites. |
| `mitigations` | Concrete countermeasures, each with a stable id (Tn-Mn), a description, and an enforcement point. Review comments cite mitigations by id. |
| `required_tests` | The tests that must exist for any change touching this threat. Each lists pytest markers, scope, and assertion. test-author writes them; qa-engineer verifies they actually exercise the threat. |
| `detection_signals` | Runtime signals that indicate the threat is being attempted or has succeeded. Operations monitors these; security-architect tunes them. |
| `severity` | One of `low`, `medium`, `high`, `critical`. Drives incident-response urgency. |
| `blast_radius` | Free-form description of how far the threat can spread when exploited. |

## 4. Adding or modifying a threat

The threat catalogue is amended through the threat-catalogue maintenance skill (security-architect Section 3.2). Process summary:

1. **Discovery** — via incident, external research, or implementation review.
2. **Draft** — security-architect drafts the new or revised entry, with mitigations and required tests.
3. **Atomic landing** — the catalogue entry, the mitigation implementations, and the required tests land together (or the entry lands first, ahead of remediation work, when a vulnerability is being mitigated).
4. **Tech-lead approval** — required for any catalogue revision.
5. **Architecture Revision History** — every catalogue change is recorded in the sibling Revision History page.

## 5. Relationship to other artifacts

* [Section 6.5 — Security Threats and Mitigations](https://oraclous.atlassian.net/wiki/spaces/OP/pages/851990) — the architectural narrative. This page is the implementation-level enforcement contract.
* [OHM v1.0 Standalone Specification](https://oraclous.atlassian.net/wiki/spaces/OP/pages/393501) — T5 (manifest tampering) covers the threat model for OHM documents.
* [Structured Governance Taxonomy](https://oraclous.atlassian.net/wiki/spaces/OP/pages/688439) (sibling page) — policy sets enforce many of the mitigations in this catalogue.
* [security-architect](https://oraclous.atlassian.net/wiki/spaces/OP/pages/557195) — the agent that resolves this catalogue against every brief and PR.
* [Test Strategy](https://oraclous.atlassian.net/wiki/spaces/OP/pages/720940) — defines the marker conventions referenced in `required_tests`.
* [ADR-008](https://oraclous.atlassian.net/wiki/spaces/OP/pages/753792) (cloud-hosted equivalence) — foundation for T6 (operator separation).
* [ADR-009](https://oraclous.atlassian.net/wiki/spaces/OP/pages/393423) (metering at substrate, billing as separable) — the architecture cross-reference that T6-M5 codifies the structural enforcement for.

## 6. Change history

| Version | Date | Change |
| --- | --- | --- |
| 1.0 | 27 May 2026 | Initial catalogue. Seven founding threats codified: T1 data exfiltration, T2 privilege escalation, T3 model-provider compromise, T4 capability poisoning, T5 manifest tampering, T6 operator-separation breach, T7 audit-log gap. |
| 1.0 | 27 May 2026 | Cosmetic revision: sibling Governance Taxonomy (688439) and ADR-008 (753792) references upgraded to hyperlinks. No semantic change to the catalogue or YAML. |
| 1.1 | 31 May 2026 | **T6-M5 added — Accepted by tech-lead (Reza Jahankohan).** Codifies the structural constraint that makes ADR-009's "metering events are operator-readable metadata" safe across implementation drift: usage-event `dimensions` is bounded scalar metering metadata — bounded key length (64), value length (256), cardinality (16), key character-class restriction. T6's `required_tests` gains an entry pinning the ORA-21 implementation tests (`test_dimensions_rejects_nested_customer_payload`, `test_dimension_value_length_is_bounded`, `test_dimension_key_length_is_bounded`, `test_dimension_key_rejects_whitespace_and_control_characters`, `test_dimensions_entry_count_is_capped`). T6's existing "plaintext customer payload in any log/metric/trace output" detection signal was clarified to name the usage stream explicitly. Driving artifact: [ORA-42](https://oraclous.atlassian.net/browse/ORA-42). |
| 1.2 | 04 Jun 2026 | **T2-M4 added — docs-writer (ORAA-241).** T2-M4 codifies the non-root container mitigation shipped in [ORAA-234](https://oraclous.atlassian.net/browse/ORAA-234) (PR #125): service containers run as system user `svc` in the runtime stage, making root unavailable at container runtime and limiting OS-layer privilege escalation if a container process is compromised. T2's `one_line` scope extended to cover OS-layer escalation alongside the existing ReBAC application-layer. Driving artifacts: [ORAA-234](https://oraclous.atlassian.net/browse/ORAA-234), PR #125. |

Subsequent changes appear here and in the Architecture Revision History.
