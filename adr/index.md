---
confluence_id: "589826"
title: "02. ADRs — Architecture Decision Records"
---

# 02. ADRs — Architecture Decision Records

This hub indexes every Architecture Decision Record for the Oraclous Platform. Each ADR captures a single material decision with its context, the decision itself, and the consequences. ADRs supersede the architecture document where they are newer and explicitly named as superseding; otherwise the architecture document is canonical.

## ADR registry

| ID | Title | Status | Date |
| --- | --- | --- | --- |
| ADR-001 | [Four-Layer Architecture](https://oraclous.atlassian.net/wiki/spaces/OP/pages/753752) | Accepted | 2026-05-27 |
| ADR-002 | [OHM as Canonical Manifest Format](https://oraclous.atlassian.net/wiki/spaces/OP/pages/557058) | Accepted | 2026-05-27 |
| ADR-003 | [Platform-as-Code, Actors-as-Harnesses](https://oraclous.atlassian.net/wiki/spaces/OP/pages/884737) | Accepted | 2026-05-27 |
| ADR-004 | [Federation via ReBAC Traversal](https://oraclous.atlassian.net/wiki/spaces/OP/pages/131083) | Accepted | 2026-05-27 |
| ADR-005 | [Workflow Concept Retirement; Harness as Replacement](https://oraclous.atlassian.net/wiki/spaces/OP/pages/753772) | Accepted | 2026-05-27 |
| ADR-006 | [Organisation as Outermost Tenancy Unit](https://oraclous.atlassian.net/wiki/spaces/OP/pages/393403) | Accepted | 2026-05-27 |
| ADR-007 | [BYOM with Three Protocol Shapes for v1](https://oraclous.atlassian.net/wiki/spaces/OP/pages/720920) | Accepted | 2026-05-27 |
| ADR-008 | [Cloud-Hosted Mode with Equivalent Data Sovereignty](https://oraclous.atlassian.net/wiki/spaces/OP/pages/753792) | Accepted | 2026-05-27 |
| ADR-009 | [Metering at Substrate, Billing as Separable](https://oraclous.atlassian.net/wiki/spaces/OP/pages/393423) | Accepted | 2026-05-27 |
| ADR-010 | [Test-Driven Development with Test-Author Agent](https://oraclous.atlassian.net/wiki/spaces/OP/pages/557078) | Accepted | 2026-05-27 |
| ADR-011 | [External Jira and Confluence (Not Local Wiki)](https://oraclous.atlassian.net/wiki/spaces/OP/pages/393443) | <custom data-type="status" data-id="id-0">Superseded by ADR-014</custom> | 2026-05-27 |
| ADR-012 | [Substrate Tenancy Enforcement Seam and RLS Backstop Preconditions](https://oraclous.atlassian.net/wiki/spaces/OP/pages/2490396) | <custom data-type="status" data-id="id-1">Proposed</custom> | 2026-05-29 |
| ADR-013 | [Fail-Closed Authority Placement at the Substrate ReBAC Seam](https://oraclous.atlassian.net/wiki/spaces/OP/pages/3702787) | Accepted | 2026-05-31 |
| ADR-014 | [Repo-canonical knowledge base; Confluence as mirror; PaperClip as master board](https://oraclous.atlassian.net/wiki/spaces/OP/pages/4685826) | <custom data-type="status" data-id="id-2">Accepted</custom> | 2026-05-31 |
| ADR-015 | [Gateway Incremental Contract and Versioning (R5→R8)](adr-015-gateway-incremental-contract-and-versioning.md) | Proposed | 2026-06-01 |

## ADR conventions

* **One decision per ADR.** If a decision is compound, it gets split into multiple ADRs that may reference each other.
* **Status lifecycle:** `Proposed` → `Accepted` → optionally `Superseded by ADR-NNN`. Rejected ADRs are kept (as `Rejected`) for the historical record.
* **No silent supersession.** When a new ADR overrides an existing one, the new ADR names it explicitly and the old ADR's status is updated.
* **Numbering is monotonic.** ADR-016 is the next number; numbers are not reused even if an ADR is rejected.

## When to write an ADR

Write an ADR when:

* A decision is being made that future contributors will need to understand the reasoning behind
* A decision overrides or refines something in the architecture document
* A decision is contested and the resolution should be recorded so it isn't re-litigated
* A decision is non-obvious in retrospect — "why did we do it this way?" deserves an answer

Do not write an ADR for:

* Implementation details that follow naturally from an architecture commitment
* Decisions that are fully covered by an existing ADR or architecture section
* Routine engineering choices (library selection, code style) — those belong in Engineering docs, not ADRs

## Template

Every ADR follows the same structure:

* **Status** — Proposed / Accepted / Rejected / Superseded
* **Context** — what situation is being addressed
* **Decision** — what is being decided (with concrete commitments)
* **Consequences** — what changes downstream as a result
* **See also** — related architecture sections, ADRs, or external references
