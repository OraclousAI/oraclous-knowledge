# Cross-cutting agreement protocol

**Document status:** Active · **Owned by:** solution-architect

This page documents how two or more team members agree on a **shared shape** and how that agreement is recorded so it cannot drift.

**Governing principle: record once, link many.** An agreed shape is written to exactly one canonical home. Every ticket and repository that depends on it links to that home.

## Three tiers of agreement

### Tier 1 — Internal to one repository

A data structure that lives entirely inside one repository. The implementer's decision, constrained by the brief and code style guide. No agreement protocol applies.

### Tier 2 — A contract between two repositories or two services

Needs the **Contract flow** (Section 2 below).

### Tier 3 — A platform-wide principle

An **ADR**. solution-architect proposes; tech-lead accepts; lands in the ADR set.

## The Contract flow (Tier 2)

1. **Surfacing:** whichever session first hits the need for a cross-repository shape **stops** and opens a `Contract` issue in Jira with `Agent Owner = solution-architect`. The surfacing session does not invent the shape locally.

2. **Ownership:** solution-architect owns the Contract issue.

3. **Drafting and review:** solution-architect drafts the exact shape. If security-touching, routes to security-architect first.

4. **Recording — the canonical home:**

| Kind of shape | Canonical home |
| --- | --- |
| Cross-repo API request/response | Interface Contracts page (→ gateway OpenAPI at R6) |
| OHM manifest field | OHM v1.0 Standalone Specification |
| ReBAC relation or governance shape | Structured Governance Taxonomy |

5. **Propagation as linked stories:** product-planner creates one implementing story per repository, each pointing at the canonical home.

6. **Enforcement:** a shared fixture or (at R6) the OpenAPI spec enforces the boundary. The Contract issue is not Done until enforcement exists.

## The Contract Jira issue type

`Contract` issue type id: `10049`. Find all open contracts with: `project = ORA AND issuetype = Contract AND status != Done`.
