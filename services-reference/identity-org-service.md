---
title: "identity-org-service"
---

# identity-org-service

**Layer:** 1 (Substrate) · **Status:** NEW in R3.5 (step 3 of the per-service order). Ported from the legacy `auth-service` human surface + the org-management logic buried in `knowledge-graph-builder`. Does not exist yet.

## Purpose

`identity-org-service` is the platform's **human** identity authority and its organisation/membership authority. It owns everything about a person and everything about an organisation: who someone is, how they log in, which org they belong to, what role they hold, and who they've invited. It is deliberately split from [auth-service](auth-service.md), which after R3.5 owns only machine principals (agents and service accounts).

Two surfaces that exist in legacy were never ported into the new service tree: the legacy `auth-service` human auth (email/password, verification, reset, OAuth) and the org-management endpoints that were sitting inside `knowledge-graph-builder` (`app/api/v1/endpoints/organizations.py`, `organization_service.py`, `org_member_service.py`, `org_invitation_service.py`). R3.5 step 3 lifts **both** into this one service so the knowledge-graph service can shed org concerns entirely — **orgs leave the graph service**.

## Responsibilities

### Users (ported from legacy `auth-service`)

* Email + password registration and login
* Email verification (`verify-email`, `resend-email-verification`)
* Password reset (`forgot-password`, `reset-password`) and `change-password`
* Social OAuth login: **Google**, **GitHub**, **Notion** (login URL build, token exchange, refresh, profile fetch)
* JWT issuance and validation for human principals; refresh-token flow
* `validate` / `me` introspection for human tokens

### Organisations + membership (ported from `knowledge-graph-builder`)

* Organisation CRUD
* Membership: a `:User` connected to an `:Organization` by a `BELONGS_TO` edge carrying an **`org_role`** of `owner | admin | member` (ADR-021 §2)
* Invitations: invite an email at an `org_role`, accept/decline lifecycle, invitation status tracking
* **Subgraph grants:** an invitation (or a direct grant) can pre-select the workspaces an invitee lands in, pairing a per-subgraph ReBAC role with a list of `graph_id`s or `"all"`. The three `org_role`s above are distinct from the five per-subgraph ReBAC roles (`owner | admin | editor | viewer | restricted_viewer`) granted via `HAS_ROLE`.

## What does NOT live here

* **Agent / service-account identity** — [auth-service](auth-service.md)
* **Credential storage / OAuth *token* storage for tool use** — [credential-broker-service](credential-broker-service.md). This service does social-login OAuth (proving *who the human is*); the broker stores provider tokens for *runtime tool calls*.
* **The ReBAC graph itself** — [knowledge-graph-service](knowledge-graph-service.md) owns the `:User`/`:Organization`/`:Subgraph` nodes and edges; this service is the authority that *writes membership and grant intent*, but org domain logic no longer lives inside the graph service.

## Dependencies

* **Upstream:** Postgres (user records, org records, invitations, sessions), Redis (session/verification-token state), email provider (verification + reset + invitation mail), Neo4j (membership + subgraph-grant edges on the ReBAC graph)
* **Downstream consumers:** every human-facing flow; [knowledge-graph-service](knowledge-graph-service.md) and [knowledge-retriever-service](knowledge-retriever-service.md) for ReBAC-scoped access decisions; the frontend (via direct host IP:port until the [application-gateway-service](application-gateway-service.md) exists)

## Security commitments

* Passwords hashed; verification + reset tokens single-use and time-bounded
* OAuth `state` signed; callback validates provider + state before token exchange
* `org_role` checks gate org mutations (only `owner`/`admin` may invite or change roles)
* Subgraph grants are bounded by the granter's own ReBAC scope; no grant can exceed it
* Multi-tenant isolation: every org/membership query carries `organization_id`

## Architecture conformance (ORAA-4 §21)

Package root `services/identity-org-service/src/oraclous_identity_org_service/` with the layered shape: `main.py` (`app = create_app()` only), `app/factory.py` (wire-only), `routes/`, `services/` (all user + org + invitation + OAuth logic), `repositories/(+models.py)` (the only Postgres/Neo4j access), `schema/` (Pydantic DTOs — the legacy `org_member_schemas`, `org_invitation_schemas`, `organization_schemas` port here), `core/{config,dependencies,lifespan}.py`, `migrations/` (the `create_organizations_table`, `create_org_invitations_table`, `org_inv_subgraph_grants` Alembic migrations port here). Three non-negotiable rules apply: no logic in handlers, no non-`BaseModel` classes or DB drivers in `routes/`, repositories are the only DB access.

## Definition of Done (ORAA-4 §22)

Done only when all 8 gates pass: structurally conformant; not hollow (`check_no_stubs` zero findings + `claimed_done` flipped in `service_status.yaml`); runs (`docker compose up` healthy, `GET /health` 200); real endpoints (integration vs real Postgres/Neo4j/Redis + a mock email sink via testcontainers); end-to-end smoke (`tests/smoke/smoke.sh` covering register → verify → login → create-org → invite → accept, run in the `r3_5_gate` job); and Reza personally tests and signs off (`needs-human` held until accepted). Per ORAA-4 §23 this is **one** deliverable in ≤6 coarse vertical slices, not a ticket-per-endpoint.

## Related

* [auth-service](auth-service.md) — machine identity (agents, service accounts); this service is its human counterpart
* [credential-broker-service](credential-broker-service.md) — runtime OAuth *token* storage (distinct from login OAuth)
* [knowledge-graph-service](knowledge-graph-service.md) — sheds org-management to this service in R3.5
* ADR-006 — Organisation as Outermost Tenancy Unit
* ADR-021 — org-role vs per-subgraph ReBAC role distinction (§2)
* Section 2 — Member, Actor, Delegated Identity definitions
