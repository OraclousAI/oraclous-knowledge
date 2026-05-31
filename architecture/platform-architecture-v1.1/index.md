# Platform Architecture v1.1

**Version:** v1.1 | **Status:** LOCKED | **Last revised:** 27 May 2026

This is the canonical architecture document for the Oraclous platform. It describes the platform as it will be — the contract every implementation decision conforms to.

## How to read this document

| Section | What it covers |
| --- | --- |
| **Section 1 — Platform Overview** | What Oraclous is, the thesis, the problem it solves, the deployment modes, the four-layer shape |
| **Section 2 — Conceptual Model** | The dictionary — every term defined precisely |
| **Section 3 — Layered Architecture** | The four layers in detail |
| **Section 4 — Manifest Format Specification** | OHM format definition |
| **Section 5 — Flows** | Eight platform behaviours end-to-end |
| **Section 6 — Governance Model** | What's enforced by code vs. interpreted by prose |
| **Section 6.5 — Security Threats and Mitigations** | Ten threat families |
| **Section 7 — Portability Story** | OHM as canonical hub; adapters |
| **Section 8 — Consolidation and Migration Plan** | The current codebase, target service set |
| **Section 9 — Deferred and Out-of-Scope** | What v1 deliberately doesn't include |

## Foundational principles

1. **Open Source** — every layer is open source; no black boxes
2. **No Vendor Lock-in** — all artifacts portable through OHM
3. **Data Sovereignty** — customer data never leaves customer-isolated infrastructure
4. **Honest Documentation** — the platform documents what it does, including limitations

## The recursion principle

The platform is code; the actors and orchestration on top are harnesses. Everything that _enforces or executes_ is platform code. Everything that _reasons and acts_ is a harness running on top of that platform.

## Architecture revision history

| Version | Date | Status | Key changes |
| --- | --- | --- | --- |
| v1.0 | May 2026 | Superseded by v1.1 | Initial architecture — locked |
| v1.1 | 27 May 2026 | Current | Added BYOM; cloud-hosted deployment mode; organisation tenancy; metering and billing; Section 6.5 threat family 10 |
