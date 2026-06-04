---
confluence_id: "622756"
title: "auth-service"
---

# auth-service

**Layer:** 1 (Substrate) · **Port:** 8000 · **Status:** Agent-only today (R2/R3 dropped human/email/OAuth). Human identity is NOT here — it moves to the new [identity-org-service](identity-org-service.md) in R3.5 step 3. After that, `auth-service` is the machine-identity service.

## Honest current reality

What shipped through R2/R3 is **agent-identity only**. The new `services/auth-service` is `agent_model` + `agent_repository` + `agent_identity_backfill` and a JWT handler — it issues and validates **agent** principals and nothing else. The legacy `auth-service` had real human auth (email/password, email verification, password reset, OAuth Google/GitHub/Notion, JWT) and that surface was **not** ported; it was dropped on the floor. So the platform today has machine identity but no human login.

R3.5 does not rebuild human auth *here*. Per ORAA-4 §R3.5 the human/email/OAuth/org surface lands in a **new** service, [identity-org-service](identity-org-service.md), built as step 3 of the per-service order. This page's service stays the **agent / service-account / machine-identity authority** and is the cleaner boundary for it.

## Scope after R3.5

`auth-service` issues and validates **non-human** principals:

* **agent** identity issuance (agents as first-class principals)
* **service account** identity and key validation
* JWT issuance and validation for machine actors
* delegated-identity token issuance (the agent half of member→agent delegation; the member half originates in [identity-org-service](identity-org-service.md))

Human users, email/password, email verification, password reset, social OAuth (Google/GitHub/Notion), and org/member/role management are **not** here — they are [identity-org-service](identity-org-service.md).

## Dependencies

* **Upstream:** Postgres (agent + service-account records), Redis (token/session state)
* **Downstream consumers:** every service that authenticates an agent or service-account request; [identity-org-service](identity-org-service.md) cross-checks delegated relationships

## Architecture conformance (ORAA-4 §21)

Package root `services/auth-service/src/oraclous_auth_service/` with the layered shape: `main.py` (app = `create_app()` only), `app/factory.py` (wire-only), `routes/`, `services/` (all logic), `repositories/(+models.py)` (the only DB access), `schema/`, `core/{config,dependencies,lifespan}.py`, `migrations/`. The three non-negotiable rules apply: no logic in handlers, no non-`BaseModel` classes or DB drivers in `routes/`, repositories are the only DB access.

## Definition of Done (ORAA-4 §22)

Done only when all 8 gates pass: structurally conformant, not hollow (`check_no_stubs` zero findings + `claimed_done` flipped in `service_status.yaml`), runs (`docker compose up` healthy, `GET /health` 200), real endpoints (integration vs real Postgres/Redis via testcontainers), end-to-end smoke (`tests/smoke/smoke.sh` in the `r3_5_gate` job), and Reza personally tests and signs off (issue carries `needs-human` until accepted).

## Related

* [identity-org-service](identity-org-service.md) — the NEW human identity + org service (human auth lives there, not here)
* ADR-006 — Organisation as Outermost Tenancy Unit
* [credential-broker-service](credential-broker-service.md) — partner for runtime token resolution
* Section 2 — Member, Actor, Delegated Identity definitions
* Section 6.5 — Threat 4 (identity confusion)
