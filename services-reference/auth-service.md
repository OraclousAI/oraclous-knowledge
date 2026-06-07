---
confluence_id: "622756"
title: "auth-service"
---

# auth-service

**Layer:** 1 (Substrate) · **Port:** 8005 · **Status:** **Real — R3.5-complete, §22-signed-off.** The platform's single **identity authority**: human users (email/password + OAuth), organisations/members/invitations, and machine principals (agents + service accounts). Reachable directly by host IP:port until the [application-gateway-service](application-gateway-service.md) fronts it.

## What it is

`auth-service` is the one identity service. R3.5 rebuilt it real, end-to-end, against real Postgres/Redis, and it passed all eight §22 gates with Reza's sign-off. It owns **everything about who a principal is and which organisation they belong to** — human and machine alike.

> **As-built note (supersedes ADR-017's two-service split).** [ADR-017](../adr/adr-017-identity-org-service-split.md) planned a *separate* `identity-org-service` for human identity, distinct from a machine-only `auth-service`. In build, R3.5 **consolidated the whole identity lifecycle into this one service** instead — one deployable, one substrate, one place where users, orgs, members, invitations, OAuth, agents and service accounts live. ADR-017's **core fix was still honored**: org/member/role/invitation **left the graph service** (they no longer live in knowledge-graph-service). Only the split-into-two-services decision was reconsidered. There is no `identity-org-service`.

## Responsibilities

### Human identity

* Email + password registration and login; change-password for an authenticated user (`POST /v1/auth/change-password`). Self-service email-verification and password-reset endpoints are **not yet built** — the schema and `set_email_verified()` exist, but only the OAuth path marks an email verified
* Social OAuth login: **Google**, **GitHub**, **Notion** (login-URL build, token exchange, profile fetch; provider tokens stored encrypted at rest — automatic provider-token refresh is not yet built) — `domain/oauth.py`, `oauth_routes`, `oauth_service`
* JWT issuance/validation for human principals; `validate` / `me` introspection

### Organisations + membership

* Organisation CRUD — `domain/organisations.py`, `org_routes`, `organisation_repository`
* Membership: a user belongs to an organisation with an `org_role` of `owner | admin | member`; `org_member_repository`
* Invitations: invite an email at an `org_role`, accept/decline lifecycle — `domain/invitations.py`, `invitation_routes`, `invitation_service`
* Every org/membership query carries `organisation_id` (ADR-006 tenancy anchor; org-scoping enforced)

### Machine identity

* **agent** identity issuance (agents as first-class principals)
* **service account** identity and key validation
* Append-only audit log of identity events (register, login, switch-org, oauth.login) — `audit_repository`, migration `0006_audit`
* JWT for machine actors — standalone **agent** and **service-account** tokens minted from a credential (`POST /agent-token`; agents created internally via `POST /internal/agent-credentials`). Member→agent delegated-identity tokens are **not issued here** (runtime delegation/OAuth token resolution lives in [credential-broker-service](credential-broker-service.md))

## Dependencies

* **Upstream:** Postgres (users, orgs, members, invitations, agents, service accounts, OAuth records, audit events — 6 migrations, the 6th being `0006_audit`), Redis (token/session/verification state)
* **Downstream consumers:** every service that authenticates a request; [credential-broker-service](credential-broker-service.md) for runtime token resolution; the frontend (via the gateway once it fronts this service)

## Architecture conformance (ORAA-4 §21)

Package root `services/auth-service/src/oraclous_auth_service/` in the canonical layered shape: `main.py` (`app = create_app()` only), `app/factory.py` (wire-only), `routes/` (`auth_routes` — register/login/refresh/switch-org/change-password/me/validate; `org_routes`; `invitation_routes` — incl. token `peek`/`accept`; `oauth_routes` — incl. `providers`) plus an un-prefixed machine surface in `app/factory.py` (`POST /agent-token`, `POST`+`DELETE /internal/agent-credentials`, a second machine `GET /me`, `GET /health`), `services/` (all logic), `domain/` (pure entities: users, organisations, invitations, oauth), `repositories/(+models.py)` (the only DB access: user/organisation/org_member/invitation/oauth repositories), `schema/`, `core/{config,dependencies,lifespan}.py`, `migrations/`. The three non-negotiable rules hold (no logic in handlers, no non-`BaseModel` classes or DB drivers in `routes/`, repositories are the only DB access). `structure_enforced: true` and `claimed_done: true` in `service_status.yaml` — the structure and no-stub checkers fail CI on any regression.

## Definition of Done (ORAA-4 §22) — MET

All 8 gates passed: structurally conformant; not hollow (`check_no_stubs` zero findings, `claimed_done: true`); runs (`docker compose up` healthy, `GET /health` 200); real endpoints (integration vs real Postgres/Redis via testcontainers — `test_user_auth_api`, `test_oauth_api`, `test_invitation_api`, `test_service_account_api`); end-to-end smoke (`tests/smoke/smoke.sh`, `r3_5_gate` job); Reza personally signed off. Org-scoping proven by `tests/organization_isolation/`.

## Related

* [ADR-017](../adr/adr-017-identity-org-service-split.md) — the (superseded) identity/org split; this service is the as-built single identity authority
* [credential-broker-service](credential-broker-service.md) — partner for runtime OAuth *token* resolution (distinct from login OAuth)
* ADR-006 — Organisation as Outermost Tenancy Unit
* [knowledge-graph-service](knowledge-graph-service.md) — shed org/member management to this service in R3.5
* Section 2 — Member, Actor, Delegated Identity definitions
