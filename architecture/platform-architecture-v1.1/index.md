---
confluence_id: "753707"
title: "Platform Architecture v1.1"
---

# Platform Architecture v1.1

**Version:** v1.1  |  **Status:** <custom data-type="status" data-id="id-0">LOCKED</custom>  |  **Last revised:** 27 May 2026

This is the canonical architecture document for the Oraclous platform. It describes the platform as it will be — the contract every implementation decision conforms to. When code and document disagree, the response is either to change the code or to deliberately revise the document; silent drift is the failure mode this discipline prevents.

## How to read this document

The nine sections (plus Section 6.5) build on each other. For a complete understanding, read in order. For targeted reference, jump to the relevant section.

| Section | What it covers | Read first if you... |
| --- | --- | --- |
| **Section 1 — Platform Overview** | What Oraclous is, the thesis, the problem it solves, the deployment modes, the four-layer shape | ...are new to the project |
| **Section 2 — Conceptual Model** | The dictionary — every term defined precisely: organisation, workspace, actor, member, agent, capability, harness, manifest, runtime, etc. | ...encounter an unfamiliar term |
| **Section 3 — Layered Architecture** | The four layers in detail (Substrate, Capability Registry, Harness Runtime + Execution Engine, Application Gateway); customisation surfaces; multi-modal commitments | ...are designing a feature or reviewing layer boundaries |
| **Section 4 — Manifest Format Specification** | OHM (Oraclous Harness Manifest) format definition; YAML structure; worked examples for tools, skills, agents, harnesses | ...are working with manifests or building adapters |
| **Section 5 — Flows** | Eight platform behaviours end-to-end: compile, execute, schedule, traverse, round-table, learn, HITL, bootstrap update | ...want to understand how the platform behaves at runtime |
| **Section 6 — Governance Model** | What's enforced by code vs. interpreted by prose; the foundational governance taxonomy; adversarial scenarios | ...are implementing access controls or policy enforcement |
| **Section 6.5 — Security Threats and Mitigations** | Ten threat families covering prompt injection, tool poisoning, exfiltration, identity confusion, manifest tampering, consciousness poisoning, DoS, side channels, federation attacks, cloud-mode threats | ...are implementing security-relevant code or running a security review |
| **Section 7 — Portability Story** | OHM as canonical hub; bidirectional adapters; MCP server + client; honest limits | ...are working on import/export or portability features |
| **Section 8 — Consolidation and Migration Plan** | The current codebase, the target service set, what lifts/stays/collapses/retires, phased migration | ...are migrating code from the legacy codebase |
| **Section 9 — Deferred and Out-of-Scope** | What v1 deliberately doesn't include; what's deferred to v2; what's permanently out of scope | ...wonder whether something is in scope |

## Foundational principles

1. **Open Source** — every layer of the platform is open source; no black boxes
2. **No Vendor Lock-in** — all artifacts portable through OHM
3. **Data Sovereignty** — customer data never leaves customer-isolated infrastructure, in both deployment modes
4. **Honest Documentation** — the platform documents what it does, including limitations and trade-offs

## The recursion principle

Thread through every section: **the platform is code; the actors and orchestration on top are harnesses.** Everything that _enforces or executes_ is platform code. Everything that _reasons and acts_ is a harness running on top of that platform. The compiler, consciousness agents, self-modification agents, FTOps, digital twins — all of these are harnesses, not platform layers.

## Architecture revision history

| Version | Date | Status | Key changes |
| --- | --- | --- | --- |
| v1.0 | May 2026 | <custom data-type="status" data-id="id-1">Superseded by v1.1</custom> | Initial architecture — locked |
| v1.1 | 27 May 2026 | <custom data-type="status" data-id="id-2">Current</custom> | Added BYOM as first-class commitment; added cloud-hosted deployment mode; added organisation as outermost tenancy; added metering and billing concepts; added Section 6.5 threat family 10 (cloud-mode threats) |
