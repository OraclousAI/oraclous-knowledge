---
confluence_id: "688439"
title: "Structured Governance Taxonomy"
---

# Structured Governance Taxonomy

**Document status:** Accepted · **Version:** 1.0 · **Anchored by:** [Section 6 — Governance Model](https://oraclous.atlassian.net/wiki/spaces/OP/pages/720900), [ADR-004](https://oraclous.atlassian.net/wiki/spaces/OP/pages/131083) (federation via ReBAC), [ADR-006](https://oraclous.atlassian.net/wiki/spaces/OP/pages/393403) (organisation tenancy)

This page is the authoritative catalogue of _policy sets_ that OHM documents reference through `governance.policy_set_ref`. Section 6 of Platform Architecture v1.1 describes the governance model in prose; this page lists the concrete policy sets the substrate ships with, plus the rules by which new ones are added.

## 1. What a policy set is

A policy set is a named, versioned bundle of governance constraints applied to a harness execution. It is the smallest unit that an OHM document can bind to. A policy set declares:

* **Trust tier** — `development`, `staging`, or `production`. The trust tier sets the floor for what the policy set can require (e.g. production policy sets **must** require signatures).
* **Execution budget ceilings** — the maximum `max_tokens`, `max_wall_time_seconds`, `max_tool_calls` the harness may set. Harnesses may set _lower_ budgets than the ceiling; they may not raise above it.
* **Signature requirements** — whether and how the harness must be signed; which trust roots are accepted.
* **BYOM constraints** — which model providers and protocol shapes are permitted; which are forbidden.
* **Capability allowlist or denylist** — which capability registries are reachable; which specific capabilities are forbidden.
* **ReBAC requirements** — which relations must be present on the requesting principal; which must be absent.
* **Audit configuration** — the audit-log emission level for executions bound to this policy set.
* **Egress constraints** — which external destinations capabilities may reach; default-deny posture.

The substrate enforces every policy-set constraint at the appropriate layer (load-time for static constraints, execution-time for dynamic constraints). Violations are `OHMGovernanceError` at load time or audit-logged termination at execution time.

## 2. Policy set catalogue (YAML)

The following YAML is the canonical, machine-readable taxonomy. Implementations **must** use this as the source of truth; the prose elsewhere on this page is for human reading and may lag this catalogue by at most one sprint.

```yaml
# oraclous-governance-taxonomy
# version: 1.0
# anchored: Section 6 of Platform Architecture v1.1
# updated: 2026-05-27

taxonomy_version: "1.0"

policy_sets:

  # ---------------------------------------------------------------
  # Development tier
  # ---------------------------------------------------------------
  - id: "policy-set:development-default@1.0.0"
    name: "Development default"
    trust_tier: "development"
    description: >
      The lowest-friction policy set. Permits unsigned harnesses, all
      BYOM protocol shapes, all core capabilities. Used during agent
      and harness development; not permitted on production harnesses.
    require_signature: false
    trusted_signature_roots: []
    budget_ceilings:
      max_tokens: 200000
      max_wall_time_seconds: 600
      max_tool_calls: 200
    byom:
      allowed_providers: ["anthropic", "openai", "google", "local"]
      allowed_protocol_shapes: ["native", "openai-compatible", "gemini-compatible"]
      forbidden_models: []
    capabilities:
      allowed_registries: ["core", "org:*"]
      forbidden_capabilities: []
    rebac:
      required_relations:
        - { subject: "principal", relation: "is_member_of", object: "owner_organization" }
      forbidden_relations: []
    audit:
      level: "summary"
      retention_days: 30
    egress:
      mode: "allowlist"
      allowed_destinations:
        - "anthropic.com"
        - "api.openai.com"
        - "generativelanguage.googleapis.com"
        - "localhost"
        - "*.local"

  # ---------------------------------------------------------------
  # Staging tier
  # ---------------------------------------------------------------
  - id: "policy-set:staging-default@1.0.0"
    name: "Staging default"
    trust_tier: "staging"
    description: >
      Suitable for pre-production harnesses. Requires signatures from
      the organisation's KMS; otherwise mirrors development with
      slightly tighter budgets and full audit retention.
    require_signature: true
    trusted_signature_roots: ["org:*"]
    budget_ceilings:
      max_tokens: 100000
      max_wall_time_seconds: 300
      max_tool_calls: 100
    byom:
      allowed_providers: ["anthropic", "openai", "google"]
      allowed_protocol_shapes: ["native", "openai-compatible", "gemini-compatible"]
      forbidden_models: []
    capabilities:
      allowed_registries: ["core", "org:*"]
      forbidden_capabilities: []
    rebac:
      required_relations:
        - { subject: "principal", relation: "is_member_of", object: "owner_organization" }
        - { subject: "principal", relation: "has_role", object: "developer_or_above" }
      forbidden_relations: []
    audit:
      level: "detailed"
      retention_days: 90
    egress:
      mode: "allowlist"
      allowed_destinations:
        - "anthropic.com"
        - "api.openai.com"
        - "generativelanguage.googleapis.com"

  # ---------------------------------------------------------------
  # Production tier
  # ---------------------------------------------------------------
  - id: "policy-set:production-default@1.0.0"
    name: "Production default"
    trust_tier: "production"
    description: >
      The default policy set for production harnesses. Requires a
      signed harness, tightens budgets, full audit retention,
      explicit egress allowlist.
    require_signature: true
    trusted_signature_roots: ["org:*", "oraclous-platform"]
    budget_ceilings:
      max_tokens: 50000
      max_wall_time_seconds: 180
      max_tool_calls: 50
    byom:
      allowed_providers: ["anthropic", "openai", "google"]
      allowed_protocol_shapes: ["native", "openai-compatible", "gemini-compatible"]
      forbidden_models: []
    capabilities:
      allowed_registries: ["core", "org:*"]
      forbidden_capabilities: []
    rebac:
      required_relations:
        - { subject: "principal", relation: "is_member_of", object: "owner_organization" }
        - { subject: "principal", relation: "has_role", object: "production_operator_or_above" }
      forbidden_relations:
        - { subject: "principal", relation: "is_suspended", object: "owner_organization" }
    audit:
      level: "full"
      retention_days: 365
    egress:
      mode: "allowlist"
      allowed_destinations:
        - "anthropic.com"
        - "api.openai.com"
        - "generativelanguage.googleapis.com"

  # ---------------------------------------------------------------
  # Production-strict tier
  # ---------------------------------------------------------------
  - id: "policy-set:production-strict@1.0.0"
    name: "Production strict"
    trust_tier: "production"
    description: >
      Hardened production policy set. Smaller budgets, narrower
      provider list, only the most recent vetted model versions,
      stricter ReBAC. Use for harnesses that touch sensitive data
      or are externally exposed.
    require_signature: true
    trusted_signature_roots: ["org:*", "oraclous-platform"]
    budget_ceilings:
      max_tokens: 20000
      max_wall_time_seconds: 60
      max_tool_calls: 20
    byom:
      allowed_providers: ["anthropic"]
      allowed_protocol_shapes: ["native"]
      forbidden_models: []
    capabilities:
      allowed_registries: ["core"]
      forbidden_capabilities:
        - "core/shell-exec@*"
        - "core/arbitrary-http@*"
    rebac:
      required_relations:
        - { subject: "principal", relation: "is_member_of", object: "owner_organization" }
        - { subject: "principal", relation: "has_role", object: "production_operator_or_above" }
        - { subject: "principal", relation: "has_attestation", object: "mfa_within_session" }
      forbidden_relations:
        - { subject: "principal", relation: "is_suspended", object: "owner_organization" }
        - { subject: "principal", relation: "is_externally_invoked", object: "owner_organization" }
    audit:
      level: "full"
      retention_days: 730
    egress:
      mode: "allowlist"
      allowed_destinations:
        - "anthropic.com"

  # ---------------------------------------------------------------
  # Federation-enabled
  # ---------------------------------------------------------------
  - id: "policy-set:production-federated@1.0.0"
    name: "Production federated"
    trust_tier: "production"
    description: >
      Production-tier policy set that permits cross-organisation
      capability references (federated:* registry) gated by ReBAC.
      See ADR-004 for federation semantics.
    require_signature: true
    trusted_signature_roots: ["org:*", "oraclous-platform"]
    budget_ceilings:
      max_tokens: 50000
      max_wall_time_seconds: 180
      max_tool_calls: 50
    byom:
      allowed_providers: ["anthropic", "openai", "google"]
      allowed_protocol_shapes: ["native", "openai-compatible", "gemini-compatible"]
      forbidden_models: []
    capabilities:
      allowed_registries: ["core", "org:*", "federated:*"]
      forbidden_capabilities: []
    rebac:
      required_relations:
        - { subject: "principal", relation: "is_member_of", object: "owner_organization" }
        - { subject: "principal", relation: "has_role", object: "production_operator_or_above" }
        - { subject: "owner_organization", relation: "has_federation_agreement", object: "target_organization" }
      forbidden_relations:
        - { subject: "principal", relation: "is_suspended", object: "owner_organization" }
    audit:
      level: "full"
      retention_days: 365
    egress:
      mode: "allowlist"
      allowed_destinations:
        - "anthropic.com"
        - "api.openai.com"
        - "generativelanguage.googleapis.com"
```

## 3. Field semantics

### 3.1 Trust tier

The trust tier sets a floor for the rest of the policy set's constraints:

| Trust tier | Floor constraints |
| --- | --- |
| `development` | No floor: signature may be optional; budgets may be high; audit may be minimal. |
| `staging` | `require_signature: true`; `audit.level` at least `detailed`; `audit.retention_days` at least 90. |
| `production` | `require_signature: true`; `audit.level: full`; `audit.retention_days` at least 365; `egress.mode: allowlist` (default-deny). |

A production policy set that violates its floor is rejected by the substrate at taxonomy load time, not just at harness load time.

### 3.2 Budget ceilings

These are **ceilings**, not defaults. A harness's `runtime.budget` may set any value at or below the ceiling. The substrate applies the lower of (harness budget, policy-set ceiling) at execution time. Budgets are enforced; exceeding any of them aborts the execution with an audit-logged termination.

### 3.3 Signature requirements

`trusted_signature_roots` is the list of key-root identifiers the substrate trusts. `org:*` means any key in the owning organisation's KMS. `oraclous-platform` means the platform-level signing root (used for capabilities published from the core registry). A harness signed by a root not in this list is treated as unsigned.

### 3.4 BYOM constraints

Constraints layer on top of [ADR-007](https://oraclous.atlassian.net/wiki/spaces/OP/pages/720920). Even if ADR-007 permits a protocol shape globally, a policy set can narrow the set for harnesses bound to it. `forbidden_models` is exact-or-glob match against `<provider>/<model-id>`.

### 3.5 Capability constraints

`allowed_registries` is the registry-prefix allowlist matched against capability `ref` in the OHM (see OHM Section 3.3). `forbidden_capabilities` is a denylist of specific `ref`s evaluated after the allowlist; a forbidden capability blocks even if its registry is allowed.

### 3.6 ReBAC requirements

`required_relations` are relations that must be present on the requesting principal at execution time. `forbidden_relations` are relations whose presence blocks execution. Special pseudo-subjects: `principal` (the requesting principal), `owner_organization` (the harness's owner), `target_organization` (for federation). Resolution semantics follow the substrate ReBAC primitives.

### 3.7 Audit configuration

| Level | What is logged |
| --- | --- |
| `summary` | Start, end, outcome, error category if failed. No payloads. |
| `detailed` | Summary + every capability invocation (capability ref, duration, outcome). No payload bodies. |
| `full` | Detailed + every model request and response, every tool call, every artifact read or write. Payload bodies are stored encrypted under the organisation's KMS; operator separation preserved per [ADR-007](https://oraclous.atlassian.net/wiki/spaces/OP/pages/720920). |

### 3.8 Egress constraints

`mode: allowlist` means default-deny: only listed destinations are reachable. `mode: denylist` means default-allow with explicit blocks. Production-tier policy sets **must** use `allowlist`. Destinations are matched as glob patterns against the destination hostname; IP-literal destinations are forbidden in production policy sets.

## 4. Adding or modifying a policy set

New policy sets and revisions to existing ones follow this process:

1. **Draft as ADR** — a new policy set is a governance decision; it is recorded as an ADR before being added here.
2. **Update the YAML** — once the ADR is accepted, security-architect proposes the YAML change as a separate revision to this page.
3. **Version bump** — any change to a policy set bumps its version. Existing harnesses that pin the prior version continue to bind to the prior policy set until they migrate.
4. **Deprecation, not deletion** — superseded policy sets are marked `deprecated` in this page (a new column in the catalogue when the first deprecation occurs); they remain resolvable until the deprecation window expires, at which point the substrate refuses to bind them.
5. **Audit and announce** — every change is recorded in the Architecture Revision History (sibling page) and announced through the agent team via the Agent and Skill Change Log if it affects how agents enforce governance.

## 5. Enforcement points

| Constraint | Enforcement point |
| --- | --- |
| Trust tier floors | Taxonomy load (substrate startup, taxonomy update) |
| Signature required + trusted roots | Harness load |
| BYOM allowed providers and protocol shapes | Harness load (against the OHM `models` section) |
| Capability registry allowlist and capability denylist | Harness load (against the OHM `capabilities` section) |
| ReBAC required and forbidden relations | Harness load (initial check) + capability invocation (per-call recheck) |
| Budget ceilings | Execution (token accounting, wall-time accounting, tool-call counting) |
| Audit level | Execution (each event filtered through the level) |
| Egress allowlist | Capability invocation (every outbound destination resolved against the allowlist before connect) |

## 6. Relationship to other artifacts

* [Section 6 — Governance Model](https://oraclous.atlassian.net/wiki/spaces/OP/pages/720900) — the architectural narrative for the governance layer. This page is the implementation-level taxonomy.
* [OHM v1.0 Standalone Specification](https://oraclous.atlassian.net/wiki/spaces/OP/pages/393501) — the OHM document references policy sets defined here through `governance.policy_set_ref`.
* [Structured Threat Catalogue](https://oraclous.atlassian.net/wiki/spaces/OP/pages/983129) (sibling page) — threat categories T1, T2, T6, T7 are mitigated in part by policy-set enforcement.
* [ADR-004](https://oraclous.atlassian.net/wiki/spaces/OP/pages/131083) (federation via ReBAC) — the foundation for the `federated:*` capability registry and the `has_federation_agreement` relation.
* [ADR-006](https://oraclous.atlassian.net/wiki/spaces/OP/pages/393403) (organisation tenancy) — establishes `owner_organization` as the substrate's primary tenancy anchor.
* [ADR-007](https://oraclous.atlassian.net/wiki/spaces/OP/pages/720920) (BYOM) — constrains the `byom` section semantics.

## 7. Change history

| Version | Date | Change |
| --- | --- | --- |
| 1.0 | 27 May 2026 | Initial taxonomy. Five policy sets defined: development-default, staging-default, production-default, production-strict, production-federated. |
| 1.0 | 27 May 2026 | Cosmetic revision: ADR-004 and ADR-006 references upgraded to hyperlinks (now-known page IDs 131083 and 393403); sibling Threat Catalogue (983129) linked. No semantic change to the taxonomy or YAML. |

Subsequent changes will appear here and in the Architecture Revision History.
