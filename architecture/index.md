# 01. Architecture

The architectural source of truth for the Oraclous platform. Everything in this section is the contract that implementation conforms to.

If you are designing a feature, reviewing a PR, or making any decision that touches platform structure — read the relevant section here first.

## What's here

- **Platform Architecture v1.1** — the canonical architecture document, split into navigable sections
- **OHM v1.0 Specification** — the Oraclous Harness Manifest format, extracted from Section 4 as a standalone reference for adapter authors and manifest writers
- **Governance Taxonomy** — the structured (YAML-shaped) representation of Section 6's governance rules, queryable by tools and agents
- **Threat Catalogue** — the structured representation of Section 6.5's security threats, used by the test-author agent to generate adversarial test cases
- **Architecture Revision History** — append-only log of revisions from v1.0 onward, with rationale for each change

## How to read this section

If you're new: read **Section 1 — Platform Overview** and **Section 2 — Conceptual Model** first.

If you're implementing: read the section most relevant to your work, then the related ADRs.

If you're reviewing for architectural compliance: the architecture document is the contract.

## Status

Architecture is locked at v1.1. Future revisions will be tracked as v1.2, v2.0, etc.
