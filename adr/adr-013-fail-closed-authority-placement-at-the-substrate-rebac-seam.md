---
confluence_id: "3702787"
title: "ADR-013 — Fail-Closed Authority Placement at the Substrate ReBAC Seam"
---

# ADR-013 — Fail-Closed Authority Placement at the Substrate ReBAC Seam

## Status

| Field | Value |
| --- | --- |
| Status | Accepted |
| Date | 31 May 2026 |
| Proposed by | solution-architect |
| Approved by | tech-lead (Reza Jahankohan) |
| Supersedes | None |
| Refines | [ADR-012 — Substrate Tenancy Enforcement Seam and RLS Backstop Preconditions](https://oraclous.atlassian.net/wiki/spaces/OP/pages/2490396) §1 (substrate enforcement seam); [ADR-004 — Federation via ReBAC Traversal](https://oraclous.atlassian.net/wiki/spaces/OP/pages/131083) |
| Superseded by | None |
| Driving artifact | [ORA-46](https://oraclous.atlassian.net/browse/ORA-46) — wire `ReBACEngine` into the substrate `AccessDecisionClient` seam |

## Context

[ADR-012](https://oraclous.atlassian.net/wiki/spaces/OP/pages/2490396) names the substrate access seam (`oraclous_substrate.access`) as the single fail-closed chokepoint every tenant-scoped storage path traverses. The ReBAC slice of that seam — `oraclous_substrate.rebac.AccessDecisionClient` — was pinned by the [ORA-15](https://oraclous.atlassian.net/browse/ORA-15) tests in `packages/substrate/tests/unit/test_rebac_client.py` against a resolver protocol `async def resolve(AccessRequest) -> bool | None` that may raise. The contract those tests pin distinguishes **four denial conditions**:

1. Resolver returns `True` → ALLOW.
2. Resolver returns `False` → DENY (definitive: the relation is known-absent).
3. Resolver returns `None` → DENY with reason (ambiguous / indeterminate; T1-M2).
4. Resolver raises → DENY with reason (backend error).

`AccessDecisionClient.check()` returns an `AccessDecision(allowed, reason)` where `reason` is non-empty on every denial — load-bearing for incident response, auditability (T7), and security-architect review of T1.

[ORA-34](https://oraclous.atlassian.net/browse/ORA-34) has now extracted the legacy ReBAC engine into a standalone package (`packages/rebac`, `ReBACEngine`). [ORA-46](https://oraclous.atlassian.net/browse/ORA-46) is the next step: wire `ReBACEngine` into the seam as a production resolver via a thin adapter that satisfies `async def resolve(AccessRequest) -> bool | None` by dispatching to `ReBACEngine.check_graph_permission(...)`.

But the legacy engine carries a convention the seam contract rejects. Per the seam-test docstring (`test_rebac_client.py` lines 90-95), legacy `check_graph_permission` returns `False` on a Neo4j error — fail-closed _at the engine_. That convention conflates three substrate-distinguishable conditions (known-absent, ambiguous, backend-error) into one boolean. The seam tests already separate them; the question is where the separation lives:

* **A (engine self-denies):** the resolver collapses ambiguity and backend error into `False`, mirroring legacy. Simpler; preserves the legacy convention end-to-end.
* **B (seam-owns-fail-closed):** the resolver returns `bool | None` and may raise; `AccessDecisionClient` is the sole site that performs fail-closed translation into a typed `AccessDecision` with a reason.

The seam tests are currently RED-defining B; the ORA-46 brief lists B as a load-bearing acceptance criterion. This ADR ratifies that choice so the [ORA-35](https://oraclous.atlassian.net/browse/ORA-35) delegation work and any future R3/R6 resolvers inherit a stable contract.

## Decision

The substrate seam — `AccessDecisionClient` — is the **single authority** for fail-closed translation in the ReBAC slice. Resolvers, including the `ReBACEngine` adapter delivered by ORA-46, MUST NOT collapse ambiguity or backend error into a bare boolean.

### 1. Resolver return-value contract

A resolver implementing `async def resolve(AccessRequest) -> bool | None` returns:

* `True` — the relation is definitively present for `(organisation_id, subject, resource, relation)`.
* `False` — the relation is definitively absent.
* `None` — the resolver cannot answer: the inputs map to a domain the resolver does not own (e.g. unknown relation, non-graph resource), the store returned an indeterminate result, or any other ambiguity. `None` is the resolver's signal to the seam that fail-closed translation is required.
* Or it raises. A raised exception signals backend failure; the seam catches it and translates to deny with reason.

The resolver MUST NOT:

* Catch its own backend errors and return `False`.
* Map an unknown relation, unknown subject domain, or unknown resource domain to `False` — those are `None`.
* Return `None` for a definitive absence — that conflates ambiguity with knowledge.

### 2. Seam translation contract

`AccessDecisionClient.check(request) -> AccessDecision` performs **all** fail-closed translation in exactly one place:

* `True` → `AccessDecision(allowed=True, …)`.
* `False` → `AccessDecision(allowed=False, reason="<definitive-deny>")`.
* `None` → `AccessDecision(allowed=False, reason="<ambiguous>")`.
* Raised → `AccessDecision(allowed=False, reason="<backend-error>")`; the seam catches at this boundary; the exception MUST NOT propagate to the caller.

`reason` is non-empty on every denial (preserves `test_deny_decision_is_explicit_not_falsy`) and SHOULD encode at least three denial families — definitive deny, ambiguous, backend error — as a recorded class, not a free-form message, so audit and incident response can distinguish them at log-read time.

### 3. Bounds on adapter logic

The `ReBACEngine` resolver adapter (ORA-46) is **thin**. Its responsibilities:

* Map `AccessRequest` → engine call arguments via a **defined lookup**: `organisation_id → organisation_id`, `subject → user_id`, `resource → graph_id`, `relation → required_level` against a closed set (e.g. `{read, write, admin}`).
* Return `None` whenever an input maps to a value the engine does not own (unknown relation, non-user subject, non-graph resource) — never a best-effort engine call.
* Translate engine output: `True/False` for a definitive in-domain answer; `None` for engine-side ambiguity; let exceptions propagate to the seam.

The adapter MUST NOT pre-empt the seam — no catching engine errors and returning `False`; no caching, logging, or retry (engine or seam responsibilities, not adapter's).

### 4. Scope

This ADR governs the substrate ReBAC seam and any resolver wired into it. It does NOT govern:

* Identity-store credential validation in `auth-service`, which is the _producer_ of organisation context, not a consumer ([ADR-012](https://oraclous.atlassian.net/wiki/spaces/OP/pages/2490396) §1a).
* In-engine caching, retry, revocation, or expiry semantics — those remain `ReBACEngine`'s responsibility per the lift-tag in ORA-34.
* Downstream consumers' interpretation of `decision.reason` (consumers free to ignore it if only `allowed` is needed).

## Consequences

### Positive

* **One fail-closed chokepoint, not two.** ADR-012 §1's "single substrate surface that fails closed" extends cleanly to ReBAC: the seam is the only place where ambiguity-or-error becomes deny, regardless of which resolver is wired in. Future R3/R6 resolvers (or a federated-registry resolver per [ADR-004](https://oraclous.atlassian.net/wiki/spaces/OP/pages/131083)) inherit this contract for free.
* **Distinguishability preserved.** The four substrate-distinguishable denial conditions remain distinguishable in `decision.reason`. T7 (audit-log gap) is structurally addressed at the substrate boundary rather than relying on each resolver to log context before returning `False`.
* **Adapter testing simplifies.** ORA-46's `[tests]` PR pins the **resolver-side** contract: argument mapping; `relation` lookup against a closed set returning `None` for unknowns; `None` for out-of-domain subject/resource; raises propagate. The seam-side translation is already pinned in `packages/substrate/tests/unit/test_rebac_client.py` and does NOT need to be re-pinned in the adapter suite. The seam's existing T1-M2 tests apply to every new resolver.
* **No silent regression on legacy lift.** When the engine signals an error, the resolver layer surfaces it via raise (and the seam records the engine-error reason) instead of silently producing the legacy bare `False`.

### Negative

* **The legacy convention is not preserved.** `ReBACEngine` as lifted in ORA-34 may still catch Neo4j errors and return `False`. Under this ADR, the adapter MUST distinguish the engine's "definitive absent" from "backend error"; the cleanest path is to stop catching backend exceptions inside the engine and let the seam catch them. See implementation notes.
* **Two-test-surface temptation.** Tempting to also test fail-closed translation in the adapter suite. Don't. The seam owns that contract; the adapter tests only its mapping and out-of-domain returns. Duplicating tests reproduces the failure pattern ADR-012 alternative D rejected.
* **Adapter must return** `None`, not raise, for unknown relations. Unknown relation isn't an error — it's a domain mismatch. The adapter returns `None`; the seam decides.

## Alternatives considered

### A. Engine self-denies (engine returns bool, swallows errors)

The legacy convention: engine catches backend exceptions and maps ambiguity to `False`. **Rejected.** Erases the distinction between known-absent and not-knowable: (i) defeats T7 distinguishability at audit, (ii) makes a backend outage indistinguishable from widespread genuine denials, (iii) directly conflicts with already-RED-pinned seam tests (`test_check_denies_on_ambiguous_resolution`, `test_check_denies_when_backend_errors`, `test_deny_decision_is_explicit_not_falsy`).

### B. Hybrid — engine self-denies AND seam also detects ambiguity

Engine returns bool, seam also has heuristics. **Rejected.** Two enforcement points for the same property — exactly the failure ADR-012 alternative D names. The seam is either the chokepoint or it isn't.

### C. Adapter performs the translation (not engine, not seam)

A thicker adapter catches engine errors and presents a clean `AccessDecision`. **Rejected.** Every future resolver (ORA-35 delegation, R5 federation, R6 gateway) would re-implement the same translation. The seam's role is to be the one place that knows fail-closed; adapters are replaceable thin wrappers, not policy.

## Implementation notes

* ORA-46's `[tests]` PR pins the **resolver-side** contract: argument mapping; `relation` lookup against a closed set returning `None` for unknowns; `None` for out-of-domain subject/resource; raises propagate. The seam-side translation is already pinned in `packages/substrate/tests/unit/test_rebac_client.py` and does NOT need to be re-pinned in the adapter suite.
* ORA-34's `ReBACEngine` should be reviewed: if backend errors are still caught and returned as `False` (legacy convention), ORA-46 must either (a) require an engine API for distinguishing error-from-absent, or (b) raise a coordinator-tier follow-up to remove the legacy catch. The ADR position is that the engine should let backend exceptions propagate; coordinator chooses path at ORA-46 Tests Review when the contract is reviewed.
* ORA-35 (R1-C2, delegation) extends the resolver domain to agent-as-subject; the protocol does not change — agent-as-subject becomes a recognised subject type, not a separate code path.
* security-architect co-signs ORA-46 at Tests Review per its T1 tag.

## References

* [ADR-012 — Substrate Tenancy Enforcement Seam and RLS Backstop Preconditions](https://oraclous.atlassian.net/wiki/spaces/OP/pages/2490396) (refined here for the ReBAC slice)
* [ADR-006 — Organisation as Outermost Tenancy Unit](https://oraclous.atlassian.net/wiki/spaces/OP/pages/393403)
* [ADR-004 — Federation via ReBAC Traversal](https://oraclous.atlassian.net/wiki/spaces/OP/pages/131083)
* [Structured Threat Catalogue](https://oraclous.atlassian.net/wiki/spaces/OP/pages/983129) — T1-M2 (ReBAC fail-closed on ambiguous), T7 (audit-log gap)
* [ORA-15](https://oraclous.atlassian.net/browse/ORA-15) (0g, substrate seam, Done), [ORA-34](https://oraclous.atlassian.net/browse/ORA-34) (engine extract, Done), [ORA-46](https://oraclous.atlassian.net/browse/ORA-46) (driving artifact)
* `packages/substrate/tests/unit/test_rebac_client.py` — the contract this ADR ratifies

## Revision history

| Date | Change |
| --- | --- |
| 31 May 2026 | Initial draft (Proposed) from the ORA-46 brief and the ORA-15 substrate seam tests. |
| 31 May 2026 | Accepted by tech-lead (Reza Jahankohan). Status → Accepted; downstream propagation (ADRs registry entry + ADR-012 back-reference) actioned same day; ORA-46 transitioned Backlog → Ready and handed to test-author. |
