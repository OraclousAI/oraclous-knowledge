# Section 4 — Manifest Format Specification

**Related structured artifact:** [OHM v1.0 — Standalone Specification](../ohm-v1.0-standalone-specification.md)

OHM is **YAML with embedded Markdown blocks**. File extension: `.ohm.yaml`.

## Versioning model

Every artifact has a **content hash** (always present, automatic, immutable) and an optional **semver tag** (human-assigned, mutable).

## The OHM document structure

```yaml
ohm: 1                          # Format version
kind: harness                   # harness | tool | skill | agent | capability_pack
id: <stable-identifier>
version:
  hash: sha256:abc123...
  tags: ["1.2.0", "stable"]

workspace: <workspace-id>

metadata:
  name: <human-readable-name>
  description: <one-line>
  authors: [...]
  created_at: <iso8601>
  updated_at: <iso8601>

spec:
  ...
```

## The two zones, made concrete

**Structured zone** — everything in YAML fields: `kind`, `id`, `version`, `workspace`, `actors[]`, `capabilities[]`, `scope`, `task_board.columns`, `triggers[]`, `policies`.

**Prose zone** — everything inside Markdown block scalars (`|`): `role`, `goal`, `orchestration`, `instructions`, `description_for_compiler`.

**A prose instruction that contradicts a structured policy never overrides the policy.** The runtime enforces the structured zone regardless of prose content.
