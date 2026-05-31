---
confluence_id: "557283"
title: "R1 — Phase 1: Auth and credential extensions"
---

# R1 — Phase 1: Auth and credential extensions

| Release ID | R1 |
| --- | --- |
| Status | <custom data-type="status" data-id="id-0">In progress</custom> |
| Window | Weeks 5-6 (parallel with the end of R0.5) |
| Owner | [tech-lead](https://oraclous.atlassian.net/wiki/spaces/OP/pages/983101) |
| Briefer | [security-architect](https://oraclous.atlassian.net/wiki/spaces/OP/pages/557195) (lead) with [solution-architect](https://oraclous.atlassian.net/wiki/spaces/OP/pages/164068) |
| Dependencies | R0 (foundation), R0.5 (tenancy substrate the new identities scope into — specifically A1 organisation_id primitive + 0g substrate seam) |

## Goal

Extend the existing `auth-service` and `credential-broker-service` with the identity primitives every later release depends on: agent identity as a first-class principal type, delegated identity from a member to an agent under a specific scope, and the ReBAC graph extensions that make delegated relationships traversable. Every subsequent release assumes agents have their own identities and can be granted delegated scopes; doing this in R1 prevents downstream rework.

## Scope

### In scope

* Agent identity issuance in `auth-service`: agents become principals alongside users and service accounts, with their own credentials and lifecycle
* Delegated identity tokens in `credential-broker-service`: a member can delegate a scope to an agent, the broker issues a token bound to (member, agent, scope, expiry)
* ReBAC graph extensions for delegated relationships: the substrate's relationship vocabulary gains `delegated_by`, `delegated_to`, and scope-bounded variants
* Migration scripts for existing data: agents created before R1 get post-hoc identities issued, so the historical record stays consistent with the new model
* Test coverage for the new identity paths, including adversarial cases (forged delegation, expired delegation, scope creep, revocation race)

### Out of scope

* Capability registry consolidation (R2)
* Any use of agent identity to actually invoke capabilities (R4 - the runtime is where invocation lives)
* The Agent Owner Jira custom field and convention-based identity in Jira/Confluence (handled by the Group D follow-up 3 work and the agent skill pages, not a code release)
* Cross-organisation delegated identity (federation gating is R5/R-Compliance work)
* _Full operator-separation reshape of the credential broker_ (customer-controlled KMS envelope) — R1 does prerequisite-level T6 only; the full reshape is deferred to **R8** (see Migration source map, deliverable 2, and the R8 forward-pointer)

## Deliverables

- [x] **Agent principal type in auth-service** - verified by an agent being able to authenticate with its own credential, distinct from any member, and receive a JWT that identifies it as a principal of type agent
- [x] **Delegated identity tokens in credential-broker-service** - verified by a member being able to mint a delegated token for an agent with a specific scope, the token validating against the broker, and the broker rejecting requests whose action exceeds the delegated scope
- [x] **ReBAC graph extensions** - verified by the substrate accepting `delegated_by` and `delegated_to` relations, queries traversing them correctly, and revocation propagating within the documented stale-relation tolerance (T2-M2)
- [x] **Migration scripts for pre-R1 agents** - verified by the script issuing identities for every existing agent, leaving no agent without a principal entry; idempotent; rollback documented
- [x] **Test coverage for adversarial cases** - verified by passing tests for: forged delegation (signature mismatch rejected at load), expired delegation (token rejected after expiry), scope creep (delegated agent attempts an action beyond declared scope), revocation race (relation revoked mid-execution causes next invocation to fail)

## Migration source map

Per [09. Releases](https://oraclous.atlassian.net/wiki/spaces/OP/pages/164160) Section 7. **Completed 28 May 2026** from a read of the legacy `auth-service`, `credential-broker-service`, and the `knowledge-graph-builder` ReBAC engine: [product-planner](https://oraclous.atlassian.net/wiki/spaces/OP/pages/884840) authored source paths + verdicts, [solution-architect](https://oraclous.atlassian.net/wiki/spaces/OP/pages/164068) signed off target shapes, [security-architect](https://oraclous.atlassian.net/wiki/spaces/OP/pages/557195) flagged threats. **Tech-lead decisions (28 May 2026):** **(A)** the ReBAC engine extract lands in `packages/rebac`, kept _separate_ from R0.5's `packages/substrate` seam (story 0g / [ORA-15](https://oraclous.atlassian.net/browse/ORA-15)), which calls into it; **(B)** R1 does _prerequisite-level_ operator-separation only — the full customer-KMS-envelope reshape of the credential broker is deferred to **R8**. **Dependency:** R1 requires R0.5 deliverable A1 (`organisation_id` primitive) and 0g (substrate seam) — matching the parallel-with-end-of-R0.5 window.

| Deliverable | Source in legacy (confirmed path) | Target shape (solution-architect sign-off) | Verdict | Threat flags (security-architect) |
| --- | --- | --- | --- | --- |
| Agent principal type (auth-service) | `auth-service/app/models/service_account_model.py` + `app/repositories/service_account_repository.py` (osk\_ bcrypt/prefix key pattern), `app/core/jwt_handler.py` (already branches on `principal_type`; SA token carries `tenant_id`/`home_graph_id`), `app/routes/auth_routes.py`. **No agent principal exists today.** | Substrate L1: new `Agent` + `AgentCredential` models mirroring the SA-key pattern; `create_agent_token()` → `principal_type=agent` + `organisation_id`; `/agent-token` + `/internal/agent-credentials`. **Carries the ORA-3 auth-side pairing** (agent JWT optionally stamping `organisation_id`). | <custom data-type="status" data-id="id-1">Lift</custom> (clean extension; new models, no refactor) | <custom data-type="status" data-id="id-2">T2</custom> (new principal must not escalate; `is_superuser` is minted-but-unenforced — flag for hardening) |
| Delegated identity tokens (credential-broker) | `credential-broker-service/app/services/credential_broker_service.py`, `app/routes/credential_routes.py`, `app/models/credential_model.py`, `app/core/security.py` (AES-GCM, single global `ENCRYPTION_KEY`, hardcoded internal key). No token/delegation/scope/org today; **zero tests**. | Substrate L1: new `DelegatedToken` primitive bound to `(member, agent, scope, expiry)`; per-use validation + scope-creep rejection; add org-scoping. **Decision B:** R1 also replaces the hardcoded internal key and adds org-scoping (prerequisite-level T6); the **full customer-KMS-envelope reshape is deferred to R8**. | <custom data-type="status" data-id="id-3">Reshape</custom> | <custom data-type="status" data-id="id-4">T2</custom> (scope creep — core); <custom data-type="status" data-id="id-5">T6</custom> (operator-separation: prerequisite-level here, full reshape R8); <custom data-type="status" data-id="id-6">T3</custom> |
| ReBAC graph extensions | `knowledge-graph-builder/app/services/rebac_service.py` (831L; Phase A CAN_ACCESS + Phase B HAS_ROLE/Permission/SubGraph/INHERITS_FROM/APPLIES_TO; fail-closed; 60s Redis cache; soft-revoke), `app/schemas/permission_schemas.py`, `tests/unit/test_rebac_phase_b.py` + `tests/integration/test_rebac.py` (mocked driver). Scoped by `graph_id` not org; Agent is **not** a subject; no delegation relations. | **Decision A:** **Extract** the engine into `packages/rebac` (the R0.5 0g `packages/substrate` seam calls into it — separate packages); **Reshape** to add `organisation_id` on edges; **Greenfield** Agent-as-subject + `delegated_by`/`delegated_to` + scope-bounded relations + a delegation traversal phase; revocation propagation within the bounded tolerance (T2-M2; 60s cache exists). | <custom data-type="status" data-id="id-7">Extract + Reshape + Greenfield</custom> | <custom data-type="status" data-id="id-8">T2</custom> (transitive-delegation escalation; revocation must invalidate the delegation cache), <custom data-type="status" data-id="id-9">T2-M2</custom>, <custom data-type="status" data-id="id-10">T1</custom> (org_id on edges closes the tenant loop) |
| Migration scripts for pre-R1 agents | Existing agent nodes (`knowledge-graph-builder` `agent_schemas.py`) have no principal identity; idempotent alembic/Neo4j migration patterns (same as R0.5 D1). | Substrate L1: idempotent backfill issuing an Agent principal + credential + ReBAC node for every existing agent; documented rollback; staging rehearsal. Depends on deliverables 1 + 3. | <custom data-type="status" data-id="id-11">Reshape</custom> (pattern exists) | <custom data-type="status" data-id="id-12">T2</custom> (no agent left without a correctly-scoped principal = no implicit-escalation gap) |
| Test coverage for adversarial cases | auth-service: unit only; credential-broker: **zero tests**; ReBAC: unit + integration but **mocked driver** (not real Neo4j). | Real-substrate (R0.5 0d harness) tests for forged delegation, expired delegation, scope creep, and **revocation race** (needs real concurrency — not the legacy mocked pattern); markers `security` + `organization_isolation`. | <custom data-type="status" data-id="id-13">Greenfield</custom> (+ lift existing test patterns) | <custom data-type="status" data-id="id-14">T2</custom> (all four cases are T2 verification); security-architect co-signs |

## Architecture references

* [Section 8 - Phase 1](https://oraclous.atlassian.net/wiki/spaces/OP/pages/688329) - the phase narrative this release operationalises
* [Section 2 - Conceptual Model](https://oraclous.atlassian.net/wiki/spaces/OP/pages/393380) - Member, Agent, Delegated Identity, ReBAC definitions
* [Section 6 - Governance Model](https://oraclous.atlassian.net/wiki/spaces/OP/pages/720900) - the Identity and credentials taxonomy
* [Structured Threat Catalogue](https://oraclous.atlassian.net/wiki/spaces/OP/pages/983129) - T2 mitigations operationalised here

## ADRs implemented

* No new ADRs - R1 is a foundational extension that the existing ADR set (especially [ADR-006](https://oraclous.atlassian.net/wiki/spaces/OP/pages/393403) for tenancy and [ADR-004](https://oraclous.atlassian.net/wiki/spaces/OP/pages/131083) for ReBAC) already covers at the architectural level. R1 is the implementation step.

## Threats addressed

| Threat | Mitigation IDs implemented | Coverage |
| --- | --- | --- |
| T2 - Privilege escalation | T2-M2 (ReBAC relation revocations propagate within seconds with bounded stale-relation tolerance), partial T2-M1 (per-invocation recheck wiring - completion in R4) | Partial - the broker side is complete; the per-invocation recheck at the runtime side lands in R4 when the runtime exists in target shape |
| T6 - Operator-separation breach | T6-M1 prerequisites (customer KMS keys remain customer-controlled across the agent-identity path); R1 replaces the hardcoded internal key and adds org-scoping but does **not** deliver the full KMS envelope (deferred to R8) | Prerequisite-level - R1 does not weaken operator separation; full T6 coverage requires the R8 customer-KMS-envelope reshape and is verified end-to-end in R-Compliance |

## Governance impact

R1 introduces agents as governance principals. Before this release, only members and service accounts could be subjects in ReBAC policies; after R1, an agent can be a subject in its own right, with relations both to members (delegation) and to resources (direct grants). The Governance Taxonomy's `principal` pseudo-subject becomes meaningful for agents. R1 does not yet add any new policy sets - the existing five sets cover the new identity type without modification.

## Risks

| Risk | Likelihood | Mitigation | Owner |
| --- | --- | --- | --- |
| Delegated tokens leak beyond the agent they were minted for | Medium | Tokens are bound to (member, agent, scope, expiry) at the broker. The broker validates the requesting principal's identity against the token's declared agent on every use. Token storage remains in the credential broker, not the runtime. | security-architect |
| Revocation does not propagate fast enough to defend against in-flight escalation | Medium | Stale-relation tolerance is bounded (documented per T2-M2). Revocation events emit a substrate audit entry that downstream layers can subscribe to for fast invalidation. | security-architect |
| Migration of pre-R1 agents introduces inconsistencies | Low | Migration is idempotent and rehearsed on a staging clone. Pre-existing agents are few; verification is mechanical. | devops-implementer |
| The delegated-token model conflicts with OAuth refresh semantics at downstream providers | Low | Delegated tokens are an internal-only primitive; they never reach external providers. External OAuth tokens continue to be resolved by the broker on a per-invocation basis as today. | backend-implementer |

## Dependencies

**Upstream:** R0 (architecture), R0.5 (the tenancy primitive that delegated identities scope into — specifically A1 `organisation_id` ([ORA-16](https://oraclous.atlassian.net/browse/ORA-16)) and the 0g substrate seam ([ORA-15](https://oraclous.atlassian.net/browse/ORA-15))).

**Downstream:** R2 (capability registry uses agent identity for descriptor authorship and credential requirements). R4 (harness runtime uses agent identity and delegated tokens at every capability invocation). R8 inherits the deferred credential-broker customer-KMS-envelope reshape. Every subsequent release assumes agents are principals.

## Sprint references

R1 transitioned **Briefed → In progress** on 28 May 2026 (product-planner created the epics and stories) and **In progress → Done** on 31 May 2026 (all epics and stories delivered; the adversarial test gate is green). The Jira epics executing this release:

* [ORA-25](https://oraclous.atlassian.net/browse/ORA-25) — Epic A: Agent identity ([ORA-30](https://oraclous.atlassian.net/browse/ORA-30), [ORA-31](https://oraclous.atlassian.net/browse/ORA-31))
* [ORA-26](https://oraclous.atlassian.net/browse/ORA-26) — Epic B: Delegated identity tokens ([ORA-32](https://oraclous.atlassian.net/browse/ORA-32), [ORA-33](https://oraclous.atlassian.net/browse/ORA-33))
* [ORA-27](https://oraclous.atlassian.net/browse/ORA-27) — Epic C: ReBAC delegation ([ORA-34](https://oraclous.atlassian.net/browse/ORA-34), [ORA-35](https://oraclous.atlassian.net/browse/ORA-35))
* [ORA-28](https://oraclous.atlassian.net/browse/ORA-28) — Epic D: Pre-R1 agent migration ([ORA-36](https://oraclous.atlassian.net/browse/ORA-36))
* [ORA-29](https://oraclous.atlassian.net/browse/ORA-29) — Epic E: Adversarial test gate ([ORA-37](https://oraclous.atlassian.net/browse/ORA-37))

All five epics (ORA-25–ORA-29) and their eight stories (ORA-30–ORA-37) are **Done**; the cross-release `is blocked by` links to R0.5's [ORA-15](https://oraclous.atlassian.net/browse/ORA-15) (0g) and [ORA-16](https://oraclous.atlassian.net/browse/ORA-16) (A1) cleared as R0.5's substrate landed. The **ORA-3 auth-side pairing** (agent JWT org-claim) is [ORA-31](https://oraclous.atlassian.net/browse/ORA-31); it is closed, completing the auth side of Contract ORA-3.

## Revision history

| Date | Change | Author | Reason |
| --- | --- | --- | --- |
| 27 May 2026 | Page created with the canonical release-page template | tech-lead (via Group D follow-up 3) | Establish R1 as the auth+credential extensions release; matches Section 8 Phase 1 |
| 28 May 2026 | Added the Migration source map (auth-service, credential-broker, KG ReBAC) with verdicts, target-shape sign-off, and threat flags. Recorded tech-lead decisions: **(A)** the ReBAC engine extracts to `packages/rebac`, kept separate from R0.5's `packages/substrate` seam (0g/[ORA-15](https://oraclous.atlassian.net/browse/ORA-15)); **(B)** R1 does prerequisite-level operator-separation only, full customer-KMS-envelope reshape deferred to **R8**. Added the deliverable-2 out-of-scope line + R8 forward-pointer. Status Planned → **Briefed**. | product-planner (coordinator); solution-architect (target shape); security-architect (threats) | Complete the Planned → Briefed gate prerequisite per 09. Releases Section 7; record the cross-release scope decisions for future reference |
| 28 May 2026 | Created the R1 Jira epics and stories (5 epics [ORA-25](https://oraclous.atlassian.net/browse/ORA-25)–ORA-29, 8 stories ORA-30–ORA-37) with briefs, lift-tags, owner assignments (`test-author`), and Blocks dependency links (cross-release to R0.5 [ORA-15](https://oraclous.atlassian.net/browse/ORA-15)/[ORA-16](https://oraclous.atlassian.net/browse/ORA-16) + intra-R1). Stories created in Backlog pending R0.5 substrate. Status → **In progress**. | product-planner (coordinator) | Begin R1 execution per the Migration source map, parallel with the end of R0.5 |
| 31 May 2026 | Reconciled the page to **delivered**: Status In progress → **Done**; all five deliverable checkboxes checked; Sprint references updated to record the In progress → Done transition and that all five epics (ORA-25–ORA-29) and eight stories (ORA-30–ORA-37) are Done with the adversarial gate (ORA-37) green and the cross-release R0.5 blockers cleared. No scope or verdict changes. | docs-writer | Reflect R1 completion now that every R1 epic and story is Done |
