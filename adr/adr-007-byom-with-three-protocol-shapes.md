---
confluence_id: "720920"
title: "ADR-007 — BYOM with Three Protocol Shapes for v1"
---

# ADR-007 — BYOM with Three Protocol Shapes for v1

## Status

| Field | Value |
| --- | --- |
| Status | <custom data-type="status" data-id="id-0">Accepted</custom> |
| Date | 27 May 2026 |
| Approved by | tech-lead (Reza Jahankohan) |
| Supersedes | None (founding ADR) |
| Superseded by | None |
| Driving artifact | [Section 6 — Governance Model](https://oraclous.atlassian.net/wiki/spaces/OP/pages/720900) |

## Context

Oraclous's positioning relies on data sovereignty: customers run harnesses using model providers _they_ contract with, not providers Oraclous resells. The customer's relationship with the model provider is direct; the platform mediates the request but does not own the credential or the data flow. This is the BYOM (bring your own model) commitment.

The implementation question is how broad the BYOM commitment is. Supporting one provider (the easiest) lets the platform ship faster but locks customers in. Supporting _every_ provider with a fully provider-agnostic abstraction is the maximalist commitment but ships much later and requires the platform to track every provider's protocol changes indefinitely. Neither extreme matches the platform's needs at v1.

The market also presents a usable structure: most production providers expose one of three protocol shapes. Anthropic native, OpenAI-compatible (used by OpenAI itself and by many open-source servers, e.g. vLLM, llama.cpp's server, Ollama, LiteLLM), and Gemini-compatible (used by Google's Gemini API and a small number of others). Committing to these three shapes for v1 covers a very large fraction of production use cases without forcing the platform into per-provider work.

The other dimension is credential handling. The "customer's relationship is direct" claim is honoured only if Oraclous-the-company staff cannot decrypt the customer's BYOM credentials in cloud-hosted mode. The platform must store the credentials (to use them) but must not be able to read them in cleartext — an operator-separation requirement that interlocks with [ADR-008](https://oraclous.atlassian.net/wiki/spaces/OP/pages/753792).

## Decision

For v1, Oraclous supports **three** BYOM protocol shapes, and only three:

1. **Anthropic native** — the Anthropic Messages API shape. The platform's default and the protocol shape used by every platform-agent in the agent team.
2. **OpenAI-compatible** — the OpenAI Chat Completions API shape. Used by OpenAI itself and by many self-hosted servers that emulate it.
3. **Gemini-compatible** — the Google Generative Language API shape.

Each shape has a precise wire-format specification: which fields are mandatory, how tool calls are serialised, how streaming is structured, how errors are typed. The harness runtime ships an adapter per shape, with no third "compatibility" layer; a harness binds a model to exactly one shape via OHM's `models[].protocol_shape` field.

Credentials are envelope-encrypted: the BYOM credential is stored encrypted under the organisation's KMS-controlled wrapping key, which itself lives in customer-controlled key material in cloud-hosted mode. The substrate code paths that touch BYOM credentials are explicit, minimal, and reviewed line-by-line by security-architect per [Threat T6 mitigations](https://oraclous.atlassian.net/wiki/spaces/OP/pages/983129).

## Alternatives considered

### A. Single protocol shape (Anthropic native only)

Smallest implementation surface. Rejected because it forecloses customers who prefer or must use providers in the other shapes (regulated industries, sovereign-cloud customers, customers with existing OpenAI-compatible deployments).

### B. Provider-agnostic abstraction (one canonical shape, every provider via adapter)

The maximalist option. Considered seriously. Rejected for v1 because the canonical shape is itself a design problem (every provider's tool-calling, streaming, and error semantics differ subtly enough that the canonical shape either drops fidelity or grows to mirror every provider's quirks). Three explicit shapes is a more honest decision for v1.

### C. Two shapes (Anthropic native + OpenAI-compatible)

Covers the largest providers and is materially easier to ship than three. Rejected because Gemini's market position and Google's developer ecosystem are significant enough that excluding the shape excludes use cases the platform's positioning needs to cover. Three is the minimum that delivers credible breadth.

### D. Plugin protocol model (customers contribute adapters)

The platform ships the runtime; customers contribute adapters for additional providers. Considered as a future direction. Rejected for v1 because plugin security and governance are themselves complex problems; v1 commits to three shapes maintained by the platform team, with a future ADR considering pluggable adapters.

## Consequences

### Positive

* The platform covers the dominant provider patterns in the market with a bounded, maintainable adapter set.
* BYOM is real, not nominal: customers contract directly with providers, the platform mediates, the platform cannot decrypt their credentials in cloud-hosted mode.
* The `protocol_shape` enum in OHM has exactly three values, simplifying the OHM spec, the validator, and downstream tooling.
* Agent-team coordination is easier: every platform-agent uses Anthropic native (the documented default), no agent has to know all three shapes.

### Negative

* Providers using shapes outside the three are not supported in v1. Customers wanting them must wait for a future ADR or use a provider gateway (e.g. LiteLLM) that fronts their preferred provider behind an OpenAI-compatible interface.
* The three adapters are platform code that must track upstream protocol changes. The maintenance cost is real and bounded; agent team allocates time per release to keep adapters current.
* The "shape" abstraction is not perfect — some provider features (e.g. provider-specific tool-result formats) require shape-specific handling in capability descriptors. This is documented as a known cost rather than a bug.

## Implementation notes

* The harness runtime ships three adapter modules, one per shape. Each module declares the wire-format mapping, error type mapping, and streaming semantics.
* OHM's `models[].protocol_shape` field validates as an enum against exactly the three accepted values; v1 OHM documents with other values fail load.
* BYOM credential storage uses envelope encryption: credential ciphertext + wrapped DEK + key reference. The wrapping key lives in customer-controlled material; substrate code paths decrypting credentials are explicitly listed and security-architect-reviewed.
* The [Structured Governance Taxonomy](https://oraclous.atlassian.net/wiki/spaces/OP/pages/688439) permits policy sets to narrow the allowed shapes further (e.g. `production-strict` permits Anthropic native only).
* Every platform-agent's model selection (documented in each agent page) is Anthropic native.

## References

* [Section 6 — Governance Model](https://oraclous.atlassian.net/wiki/spaces/OP/pages/720900)
* [OHM v1.0 Standalone Specification](https://oraclous.atlassian.net/wiki/spaces/OP/pages/393501) — `models[].protocol_shape` enum constrained here
* [Structured Governance Taxonomy](https://oraclous.atlassian.net/wiki/spaces/OP/pages/688439) — policy sets layer additional BYOM constraints
* [Structured Threat Catalogue](https://oraclous.atlassian.net/wiki/spaces/OP/pages/983129) — T3 (model-provider compromise), T6 (operator-separation breach)
* [ADR-008](https://oraclous.atlassian.net/wiki/spaces/OP/pages/753792) — cloud-hosted operator-separation; the interlocking commitment for BYOM credential safety
* [ADR-006](https://oraclous.atlassian.net/wiki/spaces/OP/pages/393403) — organisation tenancy; BYOM credentials are organisation-scoped

## Revision history

| Date | Change |
| --- | --- |
| 27 May 2026 | Rewritten to uniform ADR template. Decision unchanged; references to [OHM v1.0](https://oraclous.atlassian.net/wiki/spaces/OP/pages/393501), [Governance Taxonomy](https://oraclous.atlassian.net/wiki/spaces/OP/pages/688439), and [Threat Catalogue](https://oraclous.atlassian.net/wiki/spaces/OP/pages/983129) added. |
