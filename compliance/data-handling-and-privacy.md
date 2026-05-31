# Data Handling and Privacy

**Status:** Placeholder — formal content lands alongside compliance work in Phase 6+

## Foundational principles

1. **Customer data never leaves customer-isolated infrastructure** — applies in both modes
2. **Same code, same guarantees** — cloud-hosted runs the same enforcement code as self-hosted
3. **Per-organisation isolation** — `organization_id` is the outermost tenancy unit
4. **No training on customer data** — Oraclous-the-company does not use customer data to train any model
5. **Customer-initiated egress only** — model providers receive only the data the customer's harnesses send them

## Data classification

| Class | Examples | Encryption |
| --- | --- | --- |
| Credentials | API keys, OAuth tokens, model provider keys | Per-org KMS; never logged |
| Knowledge artifacts | Knowledge graph nodes/edges, ingested documents | At rest with per-org keys |
| OHM manifests | Harness, agent, skill, tool, capability definitions | At rest with per-org keys |
| Task content | Task board entries, HITL responses | At rest with per-org keys |
| Provenance | The audit trail itself | At rest; immutable; long retention |
| Metering | Per-org usage counters | At rest |
