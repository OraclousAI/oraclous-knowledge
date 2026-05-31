---
confluence_id: "393501"
title: "OHM v1.0 — Standalone Specification"
---

# OHM v1.0 — Standalone Specification

**Document status:** <custom data-type="status" data-id="id-0">Accepted</custom> · **Version:** 1.0 · **Anchored by:** [ADR-007](https://oraclous.atlassian.net/wiki/spaces/OP/pages/720920), ADR-002 (OHM canonical manifest)

This page is the authoritative specification for the Oraclous Harness Manifest (OHM) format, version 1.0. [Section 4 of Platform Architecture v1.1](https://oraclous.atlassian.net/wiki/spaces/OP/pages/425993) describes _why_ OHM exists and how it fits the four-layer model; this page describes _what OHM is_ in implementation-ready form. When the two disagree, this page is authoritative for the format itself; Section 4 is authoritative for the architectural rationale.

## 1. Purpose and scope

OHM is the on-disk and in-transit format for describing an Oraclous harness: the bundle of capability references, governance bindings, model bindings, prompt assets, and runtime metadata that the harness runtime executes. OHM is a _descriptor_ format, never a code format — it describes _what a harness is_, not _how it runs_. The harness runtime (in the platform's substrate-adjacent layer) consumes OHM documents and produces executions.

This specification covers:

* The top-level document structure
* Every required and optional field, with type, semantics, and validation rules
* Reference resolution semantics (how capability and model references are resolved at runtime)
* Versioning and forward/backward compatibility commitments
* The canonical serialisation format (YAML 1.2, UTF-8) and signature surface
* Error semantics for malformed or partially-valid documents

Out of scope for this page:

* The harness runtime's execution semantics (covered by Section 5 — Flows)
* Capability descriptor format (the capability registry has its own format)
* Governance taxonomy semantics (the [Section 6 governance model](https://oraclous.atlassian.net/wiki/spaces/OP/pages/720900) and the structured governance taxonomy artifact)

## 2. Document structure

An OHM document is a single YAML document with the following top-level shape:

```yaml
ohm_version: "1.0"
metadata:
  id: <harness-id>
  name: <display-name>
  owner_organization_id: <organisation-id>
  created_at: <iso8601-timestamp>
  description: <optional-free-text>
  labels: { <key>: <value>, ... }

capabilities:
  - ref: <capability-ref>
    binding: <binding-name>
    config: { ... }   # optional, capability-specific

models:
  - role: <role-name>
    binding: <model-binding>
    protocol_shape: <native|openai-compatible|gemini-compatible>
    config: { ... }   # optional

prompts:
  - role: <role-name>
    source: <inline|asset-ref>
    body: <string-or-asset-uri>

governance:
  policy_set_ref: <policy-set-ref>
  rebac_bindings: [ ... ]

runtime:
  entrypoint: <capability-binding-name>
  budget: { ... }                  # optional execution budget
  observability_tags: { ... }      # optional

signatures:
  - signer: <key-id>
    algorithm: <jws-alg>
    signature: <base64-jws>
```

Every top-level key except `signatures` is required. `signatures` is required only for harnesses bound to a published policy set; unsigned harnesses are accepted only in the substrate's `development` trust tier.

## 3. Field specifications

### 3.1 `ohm_version`

| Property | Value |
| --- | --- |
| Type | String |
| Required | Yes |
| Format | Semantic version, exactly `major.minor` |
| v1.0 values | `"1.0"` (only) |
| Forward compat | Runtime accepts `1.x` documents where `x > 0` with new optional fields ignored; rejects `2.x` documents |

### 3.2 `metadata`

| Field | Type | Required | Semantics |
| --- | --- | --- | --- |
| `id` | String (UUID v7) | Yes | Globally unique identifier; immutable across the harness lifecycle. UUID v7 chosen for time-ordering. Implementations **must** reject non-v7 UUIDs in v1.0 documents. |
| `name` | String | Yes | Human-readable display name. 1–200 UTF-8 characters. Not unique; `id` is the unique key. |
| `owner_organization_id` | String (UUID v7) | Yes | The organisation that owns this harness. **This field is the substrate's ReBAC anchor** — every read and write of this OHM is parameterised by this value. See [Section 6 Governance Model](https://oraclous.atlassian.net/wiki/spaces/OP/pages/720900). |
| `created_at` | String (ISO 8601 with timezone) | Yes | Document creation timestamp. Immutable. Used by the runtime for audit-trail anchoring. |
| `description` | String | No | Free text, up to 4000 UTF-8 characters. Operator-facing. |
| `labels` | Map<string, string> | No | Key-value labels for organisational tagging. Keys: 1–63 characters, lowercase ASCII, digits, `-`, `.`, `/`. Values: 0–255 UTF-8 characters. Maximum 64 labels per document. |

### 3.3 `capabilities`

A list of capability references the harness uses. Each entry binds an abstract capability (resolved through the capability registry) to a local binding name that the entrypoint and runtime reference.

| Field | Type | Required | Semantics |
| --- | --- | --- | --- |
| `ref` | String | Yes | Capability reference. Format: `<registry>/<capability-name>@<version>` where `<registry>` is either `core` (built-in capabilities), `org:<org-id>` (organisation-private), or `federated:<federation-id>` (cross-organisation via ReBAC). `<version>` is a semver pin; `latest` is not permitted in published harnesses. |
| `binding` | String | Yes | Local binding name used by the entrypoint and prompts. Must be unique within the harness. Format: lowercase, snake_case, 1–64 characters. |
| `config` | Map | No | Capability-specific configuration. The capability descriptor declares the schema for this object; the harness runtime validates the harness's `config` against that schema at load time. |

**Resolution semantics:** at harness load time, the harness runtime calls the capability registry to resolve every `ref` into a concrete capability descriptor. Resolution failures (capability not found, version not found, ReBAC denied) cause the entire harness load to fail; partial-load is never permitted. See [Section 5 — Flows](https://oraclous.atlassian.net/wiki/spaces/OP/pages/426016) for the full load sequence.

### 3.4 `models`

A list of model bindings. Each entry binds an abstract model role (used by prompts) to a concrete model and its BYOM protocol shape.

| Field | Type | Required | Semantics |
| --- | --- | --- | --- |
| `role` | String | Yes | Role name. Prompts reference this. Format: lowercase, snake_case, 1–64 characters. Reserved roles: `primary` (the default role; required if no other role is named in the entrypoint), `summariser`, `router`. |
| `binding` | String | Yes | Concrete model binding. Format: `<provider>/<model-id>`. The model binding resolves against the organisation's BYOM credential envelope; see [ADR-007](https://oraclous.atlassian.net/wiki/spaces/OP/pages/720920). |
| `protocol_shape` | Enum | Yes | One of `native`, `openai-compatible`, `gemini-compatible`. Determines how the harness runtime serialises requests to the model. Must match a protocol shape the provider supports for this model. |
| `config` | Map | No | Provider-and-shape-specific config (temperature, max_tokens, tool_choice, etc.). Validated against the protocol shape's schema at load time. |

### 3.5 `prompts`

A list of prompt assets. Each prompt is bound to a model role; the harness runtime feeds these to the model when the role is invoked.

| Field | Type | Required | Semantics |
| --- | --- | --- | --- |
| `role` | String | Yes | The model role this prompt is for. Must match a `role` declared in the `models` section. |
| `source` | Enum | Yes | One of `inline` or `asset-ref`. `inline` means the prompt body lives in this document; `asset-ref` means it lives in the substrate's asset store and is referenced by URI. |
| `body` | String | Yes | For `inline`: the prompt text, up to 64 KiB UTF-8. For `asset-ref`: a URI of the form `ohm-asset://<org-id>/<asset-id>@<version>`; the runtime resolves it via the substrate's asset store. Assets are immutable per version; new prompt text requires a new asset version. |

### 3.6 `governance`

| Field | Type | Required | Semantics |
| --- | --- | --- | --- |
| `policy_set_ref` | String | Yes | Reference to a policy set in the governance taxonomy. Format: `policy-set:<name>@<version>`. Resolved against the structured governance taxonomy at harness load time. |
| `rebac_bindings` | List<Object> | Yes | ReBAC bindings the harness asserts for its execution. Each binding is `{ subject: <subject-ref>, relation: <relation-name>, object: <object-ref> }`. The runtime validates that the requesting principal has the necessary relations before execution begins. See [Section 6 Governance Model](https://oraclous.atlassian.net/wiki/spaces/OP/pages/720900). |

### 3.7 `runtime`

| Field | Type | Required | Semantics |
| --- | --- | --- | --- |
| `entrypoint` | String | Yes | The capability `binding` name (from the `capabilities` list) that the runtime invokes when the harness is executed. Must reference an existing binding. |
| `budget` | Object | No | Execution budget: `{ max_tokens: int, max_wall_time_seconds: int, max_tool_calls: int }`. Defaults are set by the organisation's policy set; values here override downward only (cannot exceed policy-set limits). |
| `observability_tags` | Map<string, string> | No | Tags attached to execution traces, metrics, and audit logs for this harness. Same key/value constraints as `metadata.labels`. |

### 3.8 `signatures`

| Field | Type | Required | Semantics |
| --- | --- | --- | --- |
| `signer` | String | Yes (if present) | Key identifier. Format: `<org-id>/<key-id>`. The org's KMS resolves this to a public key for verification. |
| `algorithm` | Enum | Yes (if present) | JWS algorithm. v1.0 supports: `EdDSA` (Ed25519, preferred), `ES256`, `RS256`. `none` is forbidden. |
| `signature` | String | Yes (if present) | Detached JWS signature, base64url encoded. The signed payload is the canonical YAML serialisation (see Section 5 below) of the document with the `signatures` field removed. |

**Signature requirement:** harnesses bound to a policy set with `require_signature: true` (any production policy set) **must** carry at least one valid signature from a key trusted by the policy set. Signature absence on a required-signature harness is a load-time error.

## 4. Reference resolution semantics

Every reference in an OHM document is resolved at exactly one point: **harness load time**. The runtime resolves all references atomically — if any reference fails to resolve, the entire load fails and the runtime does not execute the harness.

| Reference type | Resolved via | Failure modes |
| --- | --- | --- |
| Capability `ref` | Capability registry | Not found; version mismatch; ReBAC denied; capability deprecated past retirement date |
| Model `binding` | BYOM credential envelope (per ADR-007) | Provider not configured for organisation; credential expired; protocol shape mismatch |
| Prompt `asset-ref` | Substrate asset store | Not found; version mismatch; ReBAC denied |
| `policy_set_ref` | Structured governance taxonomy | Not found; version mismatch; policy set deprecated |
| ReBAC binding `subject`/`object` | Substrate ReBAC primitives | Subject not found; object not found; relation undefined |
| Signer `signer` | Organisation KMS | Key not found; key revoked; algorithm not trusted |

**Caching:** the runtime may cache resolutions for the duration of a single execution. It **must not** cache resolutions across executions; each load is a fresh resolution. This preserves the substrate's authority over the current state of every referenced artifact.

## 5. Canonical serialisation and signing

OHM documents are canonically serialised as YAML 1.2, UTF-8 encoded, with the following constraints:

* Top-level keys ordered exactly as in Section 2 (`ohm_version`, `metadata`, `capabilities`, `models`, `prompts`, `governance`, `runtime`, `signatures`)
* Within each object, keys ordered lexicographically
* Within each list, elements preserve authored order (lists are semantically ordered in v1.0 wherever order matters: `capabilities`, `models`, `prompts`, `rebac_bindings`, `signatures`)
* Strings: double-quoted, with YAML 1.2 escape rules. No literal block scalars (`|`, `>`) for prompt bodies; if a prompt body needs multi-line content with preserved newlines, use the `asset-ref` source
* Numbers: integers as integers, no floats in v1.0 (durations are integer seconds, tokens are integer counts)
* Maps: no anchors or aliases (`&`, `*`) — references go through the explicit reference fields described above
* UTF-8 byte order mark (BOM) is forbidden
* Trailing whitespace on lines is forbidden
* Document ends with a single newline

The signed payload is the canonical serialisation with the `signatures` top-level key and its entire value removed. Signing implementations **must** compute the signed payload by serialising the document with `signatures` omitted, not by removing the field from a previously-serialised document.

## 6. Versioning and compatibility

OHM follows semantic versioning at the major.minor level (no patch level — the spec is the artifact):

| Change type | Version bump | Compatibility |
| --- | --- | --- |
| Add new optional field | Minor (1.0 → 1.1) | Forward-compatible: v1.0 runtimes ignore the new field; v1.1 documents work in v1.0 runtimes (without the new feature) |
| Add new required field | Major (1.x → 2.0) | Not compatible: v1.x runtimes reject v2.x documents and vice versa |
| Remove field | Major | Not compatible |
| Change field semantics | Major | Not compatible |
| Add new enum value | Minor | Forward-compatible if old runtimes can safely reject; otherwise major |
| Tighten validation rule (narrower accepted set) | Major | Existing documents may become invalid |
| Loosen validation rule (wider accepted set) | Minor | Forward-compatible |

The runtime declares its supported `ohm_version` range in its capability descriptor; the substrate refuses to load a harness whose version is outside the runtime's range.

## 7. Error semantics

The runtime's OHM loader produces typed errors. Implementations **must** use these error categories:

| Error | When raised | Observable |
| --- | --- | --- |
| `OHMParseError` | YAML is malformed; canonical serialisation rules violated | Audit log; harness load fails |
| `OHMSchemaError` | YAML is valid but does not match the OHM schema (missing required field, wrong type, value out of range) | Audit log; harness load fails; specific field path included in error |
| `OHMReferenceError` | A reference (capability, model, asset, policy set, ReBAC subject/object, signer key) cannot be resolved | Audit log; harness load fails; specific reference and resolution-failure reason included |
| `OHMSignatureError` | Signature missing where required; signature invalid; algorithm not trusted; signer key revoked | Audit log with elevated severity; harness load fails; security-architect-monitored |
| `OHMVersionError` | `ohm_version` is outside the runtime's supported range | Audit log; harness load fails |
| `OHMGovernanceError` | Policy set resolves but the harness violates its constraints (budget exceeds policy-set ceiling, ReBAC binding asserts a relation the principal lacks) | Audit log; harness load fails; security-architect-monitored if pattern recurs |

Partial loads are never permitted — an error in any phase aborts the whole load.

## 8. Minimal valid example

A minimal OHM v1.0 document that loads successfully:

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

This document carries no signatures, which is acceptable because `policy-set:development-default` sets `require_signature: false`. A production-bound harness would carry at least one signature and reference a policy set that requires signing.

## 9. Relationship to other specifications

* [Section 4 — Manifest Format Specification](https://oraclous.atlassian.net/wiki/spaces/OP/pages/425993) — the architectural narrative for why OHM exists and how it fits the four-layer model. Section 4 may reference this page for the canonical format; this page references Section 4 for the rationale.
* [ADR-007 — BYOM with Three Protocol Shapes for v1](https://oraclous.atlassian.net/wiki/spaces/OP/pages/720920) — constrains the `models[].protocol_shape` enum.
* ADR-002 — OHM canonical manifest (proposed) — the decision record for OHM-as-canonical-format.
* **Structured Governance Taxonomy** (sibling page) — defines the policy sets that `governance.policy_set_ref` resolves against.
* **Structured Threat Catalogue** (sibling page) — T5 (manifest tampering) covers the threat model for unsigned or malformed OHM documents.
* [Section 5 — Flows](https://oraclous.atlassian.net/wiki/spaces/OP/pages/426016) — the harness load and execution flow that consumes OHM documents.

## 10. Change history

| Version | Date | Change |
| --- | --- | --- |
| 1.0 | 27 May 2026 | Initial spec extracted from Section 4 of Platform Architecture v1.1. Establishes the v1.0 baseline. |

Future revisions of this spec will appear here with version bumps per Section 6.
