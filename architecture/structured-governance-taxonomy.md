# Structured Governance Taxonomy

**Document status:** Accepted · **Version:** 1.0 · **Anchored by:** Section 6, ADR-004, ADR-006

This page is the authoritative catalogue of _policy sets_ that OHM documents reference through `governance.policy_set_ref`.

## 1. What a policy set is

A policy set is a named, versioned bundle of governance constraints applied to a harness execution. It declares: trust tier, execution budget ceilings, signature requirements, BYOM constraints, capability allowlist/denylist, ReBAC requirements, audit configuration, egress constraints.

## 2. Policy set catalogue (YAML)

```yaml
taxonomy_version: "1.0"

policy_sets:

  - id: "policy-set:development-default@1.0.0"
    name: "Development default"
    trust_tier: "development"
    require_signature: false
    budget_ceilings:
      max_tokens: 200000
      max_wall_time_seconds: 600
      max_tool_calls: 200
    byom:
      allowed_providers: ["anthropic", "openai", "google", "local"]
      allowed_protocol_shapes: ["native", "openai-compatible", "gemini-compatible"]
    capabilities:
      allowed_registries: ["core", "org:*"]
    audit:
      level: "summary"
      retention_days: 30

  - id: "policy-set:staging-default@1.0.0"
    name: "Staging default"
    trust_tier: "staging"
    require_signature: true
    budget_ceilings:
      max_tokens: 100000
      max_wall_time_seconds: 300
      max_tool_calls: 100
    audit:
      level: "detailed"
      retention_days: 90

  - id: "policy-set:production-default@1.0.0"
    name: "Production default"
    trust_tier: "production"
    require_signature: true
    budget_ceilings:
      max_tokens: 50000
      max_wall_time_seconds: 180
      max_tool_calls: 50
    audit:
      level: "full"
      retention_days: 365

  - id: "policy-set:production-strict@1.0.0"
    name: "Production strict"
    trust_tier: "production"
    require_signature: true
    budget_ceilings:
      max_tokens: 20000
      max_wall_time_seconds: 60
      max_tool_calls: 20
    byom:
      allowed_providers: ["anthropic"]
      allowed_protocol_shapes: ["native"]
    capabilities:
      allowed_registries: ["core"]
      forbidden_capabilities:
        - "core/shell-exec@*"
        - "core/arbitrary-http@*"
    audit:
      level: "full"
      retention_days: 730

  - id: "policy-set:production-federated@1.0.0"
    name: "Production federated"
    trust_tier: "production"
    require_signature: true
    budget_ceilings:
      max_tokens: 50000
      max_wall_time_seconds: 180
      max_tool_calls: 50
    capabilities:
      allowed_registries: ["core", "org:*", "federated:*"]
    audit:
      level: "full"
      retention_days: 365
```

## 7. Change history

| Version | Date | Change |
| --- | --- | --- |
| 1.0 | 27 May 2026 | Initial taxonomy. Five policy sets defined. |
