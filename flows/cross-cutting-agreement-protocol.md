---
confluence_page_id: "1245185"
title: "Cross-cutting agreement protocol"
---

**Document status:** Active · **Parent:** [10. Engineering Flows](https://oraclous.atlassian.net/wiki/spaces/OP/pages/1212418) · **Owned by:** [solution-architect](https://oraclous.atlassian.net/wiki/spaces/OP/pages/164068)

This page documents how two or more team members agree on a **shared shape** — a data structure, an API response, an OHM field, a ReBAC relation, an error envelope — and how that agreement is recorded so it cannot drift. It is the flow that prevents the failure mode where the frontend session and the backend session each invent their own incompatible version of the same thing.

The governing principle is **record once, link many**. An agreed shape is written to exactly one canonical home. Every ticket and every repository that depends on it links to that home. The shape is never copied into two places, because two copies are two sources of truth and they drift.

## 1. Three tiers of agreement

Not every decision needs the same weight of process. Agreements fall into three tiers, escalating by how much they bind.

### Tier 1 — Internal to one repository

A data structure that lives entirely inside one repository and crosses no service boundary — a private helper's return type, a component's local state shape, an internal enum — is the implementer's decision, constrained by the brief and the code style guide. No agreement protocol applies. It is reviewed at the normal PR gate like any other code.

### Tier 2 — A contract between two repositories or two services

A shape that binds two parties working in separate sessions — the usage-report object the gateway returns and the console consumes, the request/response shape of a gateway endpoint, an OHM field two services both read — needs a real protocol, because no single repository session has the authority to bind the other. This is the **Contract flow**, detailed in Section 2.

### Tier 3 — A platform-wide principle

A decision that binds everything, not just two parties — "all timestamps are UTC ISO-8601 with explicit offset", "all monetary values are integer minor units", "all IDs are ULIDs" — is an **ADR**. [solution-architect](https://oraclous.atlassian.net/wiki/spaces/OP/pages/164068) proposes; the human tech-lead accepts; it lands in the [ADR set](https://oraclous.atlassian.net/wiki/spaces/OP/pages/589826). This flow already exists and is documented on the solution-architect skill page and the ADR template; it is named here only for completeness.

## 2. The Contract flow (Tier 2)

This is the flow that was previously undocumented. Six steps.

### 2.1 Surfacing

Whichever session first hits the need for a cross-repository shape **stops** and raises it. It does not invent the shape locally and proceed. It raises the need as a **Contract** issue in Jira (issue type `Contract`; see Section 4), with `Agent Owner = solution-architect`, describing the need and a proposed shape. The surfacing session then continues with other work or waits; it does not block on the contract unless the contract is its only path forward.

A repository session that needs a cross-repository shape and proceeds to define it locally — without opening a Contract issue — is committing a process violation of the same class as an implementer who edits tests to make them pass. The whole point of the protocol is that inventing-in-isolation is not allowed for shapes that bind two parties.

### 2.2 Ownership

[solution-architect](https://oraclous.atlassian.net/wiki/spaces/OP/pages/164068) owns the Contract issue. It is the only persona with the authority to bind two repositories to a shared shape, because a cross-service boundary is an architectural decision by definition. This is one of the reasons solution-architect belongs in the coordinator layer rather than inside a single repository session.

### 2.3 Drafting and review

solution-architect drafts the exact shape: field names, types, nullability, enumerated values, versioning, and the error envelope. If the shape touches security — authentication tokens, credentials, any field that could carry PII, anything crossing the operator-separation boundary — it routes to [security-architect](https://oraclous.atlassian.net/wiki/spaces/OP/pages/557195) for review before it is agreed. If the shape is an OHM field, it is an OHM change and follows the OHM Spec's own versioning rather than this page's canonical-home rule.

### 2.4 Recording — the canonical home

The agreed shape is written to **exactly one** canonical home, chosen by what kind of shape it is:

| Kind of shape | Canonical home |
| --- | --- |
| Cross-repo API request/response (HTTP, between frontend and gateway) | [10. Engineering Flows](https://oraclous.atlassian.net/wiki/spaces/OP/pages/1212418) → Interface Contracts page (interim). Migrates into the gateway's OpenAPI spec when the gateway exists at R6. |
| OHM manifest field | [OHM v1.0 Standalone Specification](https://oraclous.atlassian.net/wiki/spaces/OP/pages/393501) (with a version bump per its own versioning section) |
| ReBAC relation or governance shape | [Structured Governance Taxonomy](https://oraclous.atlassian.net/wiki/spaces/OP/pages/688439) |
| A new platform-wide principle | An [ADR](https://oraclous.atlassian.net/wiki/spaces/OP/pages/589826) (this is Tier 3, not a contract) |

The Contract issue _links to_ the canonical home. It does not contain the shape itself once agreed, because then the Jira issue and the canonical page would be two sources of truth.

### 2.5 Propagation as linked stories

Once the shape is agreed and recorded, [product-planner](https://oraclous.atlassian.net/wiki/spaces/OP/pages/884840) creates the implementing stories — typically one per repository ("gateway returns X per \[contract link\]", "console consumes X per \[contract link\]"). Both stories link the same canonical home. Each story is then executed independently under normal TDD, but because they test against the same agreed shape, they cannot drift apart.

### 2.6 Enforcement at the boundary

An agreement that is written down but not enforced will still drift six weeks later when someone changes one side. The contract becomes _executable_ through a shared artifact:

* Once the gateway exists (R6), it publishes an OpenAPI spec; the frontend's `api-client` is generated or validated against that spec; a contract test in CI fails if either side diverges.
* Before R6, the interim enforcement is a shared fixture: the agreed shape is encoded as a test fixture that both repositories' tests import (via a shared package or a copied-with-checksum fixture), so a divergence breaks a test.

The CI contract test is the difference between an agreement that is recorded and one that is enforced. A Contract issue is not Done until its enforcement mechanism exists.

## 3. The flow as a schematic

```
A shared-shape need is discovered (any session)
   |
   v
Internal to one repo?  --yes-->  implementer decides; PR review gates it (Tier 1)
   | no
   v
Platform-wide principle?  --yes-->  ADR flow: solution-architect proposes,
   | no                              tech-lead accepts, recorded in ADR set (Tier 3)
   v
CONTRACT flow (Tier 2):
   1. Surfacing session opens a Contract issue, Agent Owner = solution-architect
   2. solution-architect drafts the shape (coordinator session)
   3. security-architect reviews if security-touching
   4. Agreed shape recorded ONCE in its canonical home
        - API shape       -> Interface Contracts page (then OpenAPI at R6)
        - OHM field       -> OHM v1.0 Spec (version bump)
        - ReBAC relation  -> Governance Taxonomy
   5. product-planner creates linked implementing stories (one per repo),
      each pointing at the canonical home -- never duplicating it
   6. CI contract test enforces the boundary so neither side can drift;
      Contract issue is not Done until enforcement exists
```

## 4. The Contract Jira issue type

Cross-repository contracts are tracked with a dedicated Jira issue type, `Contract`, sitting between Epic and Story in the hierarchy. An Epic can spawn Contracts; a Contract spawns the paired implementing Stories.

* `Agent Owner` starts at `solution-architect`.
* The issue is **Done** when: the shape is agreed, recorded in its canonical home, the implementing stories are created and linked, and the enforcement mechanism (contract test or shared fixture) exists.
* Find all open contracts with: `project = ORA AND issuetype = Contract AND status != Done`. This single query answers "what shared shapes are we still negotiating?" — the legibility this whole system is built around.

If the `Contract` issue type has not yet been created in Jira, the interim is a Story labelled `contract` with the same ownership and Done criteria; the dedicated type is preferred because it makes the query above clean.

## 5. Worked example

The console needs to display per-organisation usage. The gateway will expose it. Neither session may invent the shape alone.

1. The frontend session, scoping the usage view, discovers it needs a usage-report shape from the gateway. It opens `Contract` issue "UsageReport response shape", `Agent Owner = solution-architect`, with a proposed shape, and continues other work.
2. solution-architect (coordinator) drafts the shape: organisation_id, period, per-metric aggregates with explicit units, nullability, the error envelope for an unauthorised caller.
3. security-architect reviews because the payload is ReBAC-gated and must not leak cross-organisation data; confirms the shape carries no field that bypasses the gate.
4. The agreed shape is recorded on the Interface Contracts page. The Contract issue links it.
5. product-planner creates two stories: one in the backend repo ("gateway returns UsageReport per \[contract\]"), one in the frontend repo ("console consumes UsageReport per \[contract\]"), both linking the contract.
6. A shared fixture encodes the agreed shape; both repos' tests import it. When the gateway exists at R6, the shape migrates into the OpenAPI spec and the api-client is validated against it. The Contract issue moves to Done.

## 6. Related references

* [10. Engineering Flows](https://oraclous.atlassian.net/wiki/spaces/OP/pages/1212418) — the hub
* Interface Contracts — the canonical home for API shapes (child of this hub)
* [OHM v1.0 Standalone Specification](https://oraclous.atlassian.net/wiki/spaces/OP/pages/393501) — canonical home for manifest fields
* [Structured Governance Taxonomy](https://oraclous.atlassian.net/wiki/spaces/OP/pages/688439) — canonical home for ReBAC relations
* [02. ADRs](https://oraclous.atlassian.net/wiki/spaces/OP/pages/589826) — Tier 3 platform-wide decisions
* [solution-architect](https://oraclous.atlassian.net/wiki/spaces/OP/pages/164068) — the persona that owns Contract decisions
