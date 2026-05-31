# OHM v1.0 — Standalone Specification

**Document status:** Accepted · **Version:** 1.0 · **Anchored by:** ADR-007, ADR-002

This page is the authoritative specification for the Oraclous Harness Manifest (OHM) format, version 1.0.

## 1. Purpose and scope

OHM is the on-disk and in-transit format for describing an Oraclous harness: capability references, governance bindings, model bindings, prompt assets, and runtime metadata. OHM is a _descriptor_ format, never a code format.

## 2. Document structure

```yaml
ohm_version: "1.0"
metadata:
  id: <harness-id>               # UUID v7
  name: <display-name>
  owner_organization_id: <org-id> # UUID v7 — ReBAC anchor
  created_at: <iso8601>
  description: <optional>
  labels: { <key>: <value>, ... }

capabilities:
  - ref: <capability-ref>        # core/<name>@<version> | org:<org-id>/<name>@<version>
    binding: <binding-name>
    config: { ... }

models:
  - role: <role-name>
    binding: <provider>/<model-id>
    protocol_shape: native|openai-compatible|gemini-compatible
    config: { ... }

prompts:
  - role: <role-name>
    source: inline|asset-ref
    body: <string-or-asset-uri>

governance:
  policy_set_ref: <policy-set-ref>
  rebac_bindings: [ ... ]

runtime:
  entrypoint: <capability-binding-name>
  budget: { ... }
  observability_tags: { ... }

signatures:
  - signer: <key-id>
    algorithm: EdDSA|ES256|RS256
    signature: <base64-jws>
```

## 3. Reference resolution semantics

Every reference resolves at **harness load time**, atomically. If any reference fails, the entire load fails. Partial loads are never permitted.

## 5. Canonical serialisation

OHM documents are YAML 1.2, UTF-8. Top-level keys ordered as in Section 2. No anchors or aliases.

## 6. Versioning and compatibility

| Change type | Version bump |
| --- | --- |
| Add new optional field | Minor (1.0 → 1.1) |
| Add new required field | Major (1.x → 2.0) |
| Remove field | Major |
| Change field semantics | Major |

## 7. Error semantics

| Error | When raised |
| --- | --- |
| `OHMParseError` | YAML is malformed |
| `OHMSchemaError` | Missing required field, wrong type |
| `OHMReferenceError` | A reference cannot be resolved |
| `OHMSignatureError` | Signature missing where required; signature invalid |
| `OHMVersionError` | Version outside supported range |
| `OHMGovernanceError` | Harness violates policy-set constraints |

## 8. Minimal valid example

```yaml
ohm_version: "1.0"

metadata:
  id: "01976e3a-7c9b-7b00-9c45-1234567890ab"
  name: "Hello World Harness"
  owner_organization_id: "01976e3a-0000-7000-9c45-000000000000"
  created_at: "2026-05-27T18:00:00Z"

capabilities:
  - ref: "core/echo@1.0.0"
    binding: "echo"

models:
  - role: "primary"
    binding: "anthropic/claude-opus-4-7"
    protocol_shape: "native"

prompts:
  - role: "primary"
    source: "inline"
    body: "You are a helpful assistant. When asked anything, respond briefly."

governance:
  policy_set_ref: "policy-set:development-default@1.0.0"
  rebac_bindings:
    - subject: "organization:01976e3a-0000-7000-9c45-000000000000"
      relation: "owns"
      object: "harness:01976e3a-7c9b-7b00-9c45-1234567890ab"

runtime:
  entrypoint: "echo"
```

## 10. Change history

| Version | Date | Change |
| --- | --- | --- |
| 1.0 | 27 May 2026 | Initial spec extracted from Section 4 of Platform Architecture v1.1 |
