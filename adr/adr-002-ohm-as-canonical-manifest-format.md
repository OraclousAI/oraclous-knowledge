---
confluence_id: "557058"
title: "ADR-002 — OHM as Canonical Manifest Format"
---

# ADR-002 — OHM as Canonical Manifest Format

## Status

| Field | Value |
| --- | --- |
| Status | <custom data-type="status" data-id="id-0">Accepted</custom> |
| Date | 27 May 2026 |
| Approved by | tech-lead (Reza Jahankohan) |
| Supersedes | None (founding ADR) |
| Superseded by | None |
| Driving artifacts | [Section 4 — Manifest Format Specification](https://oraclous.atlassian.net/wiki/spaces/OP/pages/425993) · [OHM v1.0 Standalone Specification](https://oraclous.atlassian.net/wiki/spaces/OP/pages/393501) |

## Context

A harness on Oraclous is an executable bundle: it binds capabilities, models, prompts, governance, and runtime metadata into something the platform can run. The question is what format the bundle takes on disk and in transit. The v0 system used several ad-hoc formats: capability descriptors as one JSON shape, prompt configurations as another, harness wrappers as a third. Cross-format references were string-based and resolved by ad-hoc lookup code in whichever service happened to need them. The result was that no single document described "what this harness is" — you had to assemble the picture from three or four storage locations.

For v1 the platform commits to harnesses as first-class portable artifacts: a single document that describes everything about a harness, signable as a unit, versionable as a unit, transferable between deployments. This requires a canonical format with a typed schema, deterministic serialisation (for signing), and a clear resolution semantics for references.

The market has nearby formats — OpenAI's assistants config, Anthropic's tool definitions, LangChain's various YAMLs — but none captures all five concerns (capabilities, models, prompts, governance, runtime) in a way that fits Oraclous's substrate-anchored governance model. Adopting an outside format would mean either extending it (forking the spec) or mapping every Oraclous concept through a foreign vocabulary. The format is also the platform's primary public surface for harness portability; what it is shapes how harnesses are discussed, exchanged, and reasoned about. This is a decision worth making explicitly.

## Decision

The Oraclous Harness Manifest (OHM) is the canonical, sole format for describing a harness. The specification is owned by Oraclous and versioned independently. Version 1.0 is the founding spec, captured in the [OHM v1.0 Standalone Specification](https://oraclous.atlassian.net/wiki/spaces/OP/pages/393501).

OHM is a single YAML 1.2 document containing exactly the top-level sections `ohm_version`, `metadata`, `capabilities`, `models`, `prompts`, `governance`, `runtime`, and (when signed) `signatures`. Every reference inside the document — capability, model, prompt asset, policy set, ReBAC binding, signer key — resolves at exactly one point: harness load time, atomically, with partial loads forbidden. The format is descriptor-only: it describes what a harness _is_, never how it _runs_.

## Alternatives considered

### A. Extend OpenAI assistants config

Take the published assistants schema and add Oraclous-specific extensions for governance and ReBAC. Gives some interop, but governance is the central concern of Oraclous and the assistants schema has no slot for it. Extensions would dominate the format, leaving the "interop" benefit largely nominal. Rejected.

### B. Adopt a workflow framework's format (Temporal, Airflow, LangGraph)

Each has a mature execution-graph format. But Oraclous explicitly retires the workflow concept (see [ADR-005](https://oraclous.atlassian.net/wiki/spaces/OP/pages/753772)) — harnesses are not workflows, they are bundles. Workflow formats model edges and nodes; OHM models bindings and references. The vocabulary mismatch is structural. Rejected.

### C. Multi-document split (current v0 approach, formalised)

Keep capability descriptors, prompt configs, governance bindings, and harness wrappers as separate documents that reference each other. Familiar to the v0 codebase; rejected because the entire point of canonical-manifest is single-document portability and atomic signing. Multi-document splits make signing semantics awkward (sign which document?) and resolution semantics expensive (chase pointers at every load).

### D. JSON instead of YAML

Same conceptual format, JSON serialisation. Considered seriously. YAML chosen for human readability of prompt bodies and metadata; JSON's lack of comments matters for ops-facing files. Canonical serialisation rules (OHM v1.0 spec Section 5) constrain YAML to the deterministic subset, addressing the usual "YAML is too loose" critique. The choice is reversible at OHM v2.0 if it proves troublesome; the data model is JSON-compatible.

## Consequences

### Positive

* A harness is a thing — a single artifact that can be signed, transferred, audited, and version-pinned as a unit.
* Reference resolution semantics are uniform: every reference resolves at harness load time, atomically, with typed errors. This makes the substrate the single arbiter of state during load.
* OHM as a published spec becomes the platform's portability story: harnesses authored on one Oraclous deployment can load on another without translation, given matching capability registries and BYOM availability.
* Signing semantics are well-defined: a single canonical serialisation, a single signed payload, a single signature surface. [Threat T5 (manifest tampering)](https://oraclous.atlassian.net/wiki/spaces/OP/pages/983129) has a concrete mitigation surface.

### Negative

* The platform owns a spec. Spec evolution discipline (versioning, deprecation, compatibility commitments) becomes a permanent platform cost. The OHM v1.0 spec already encodes versioning rules to keep this cost bounded.
* Authoring OHM by hand is more demanding than authoring an ad-hoc YAML. Tooling (lint, validation, scaffolding) is required for good authoring UX. Phase 1 includes `ohm-lint` as a planned deliverable.
* External interop is reduced. Importing a harness from another platform requires a translation step; exporting to another platform requires the same. The platform accepts this cost in exchange for a clean internal model.

## Implementation notes

* The spec itself lives in [OHM v1.0 Standalone Specification](https://oraclous.atlassian.net/wiki/spaces/OP/pages/393501); Section 4 of the architecture document is the prose framing.
* The substrate stores OHM documents in their canonical serialisation; storage byte-for-byte preserves the signed payload.
* Phase 1 deliverables driven by this ADR: OHM parser/validator library, `ohm-lint` CLI, OHM signer/verifier integrated with the substrate KMS, OHM canonical-serialisation conformance test suite.
* Future minor versions follow the OHM v1.0 spec's versioning rules (Section 6 of the spec).

## References

* [Section 4 — Manifest Format Specification](https://oraclous.atlassian.net/wiki/spaces/OP/pages/425993)
* [OHM v1.0 Standalone Specification](https://oraclous.atlassian.net/wiki/spaces/OP/pages/393501)
* [Structured Governance Taxonomy](https://oraclous.atlassian.net/wiki/spaces/OP/pages/688439) — provides the policy sets OHM references
* [Structured Threat Catalogue](https://oraclous.atlassian.net/wiki/spaces/OP/pages/983129) — T5 covers manifest tampering, mitigated by OHM signing rules
* [ADR-007](https://oraclous.atlassian.net/wiki/spaces/OP/pages/720920) — constrains the `models[].protocol_shape` enum
* [ADR-005](https://oraclous.atlassian.net/wiki/spaces/OP/pages/753772) — harness-as-unit vs workflow-as-graph framing

## Revision history

| Date | Change |
| --- | --- |
| 27 May 2026 | Initial publication in uniform ADR template. Status set to Accepted, consistent with the published OHM v1.0 spec. |
