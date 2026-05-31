# auth-service

**Layer:** 1 (Substrate) · **Port:** 8000 · **Status:** Production-grade (extension pending Phase 1)

## Purpose

`auth-service` is the platform's identity authority. It issues credentials, validates them on every authenticated request, and exposes the principal-type model the rest of the platform relies on for authorisation decisions.

## Responsibilities

- User authentication (email/password, OAuth flows)
- JWT issuance and validation
- OAuth client registration for external integrations
- Principal-type discrimination: **user**, **service account**, **agent** (agent added in Phase 1)
- Delegated identity token issuance (Phase 1 extension)

## Dependencies

- **Upstream:** Postgres (user records), Redis (session state)
- **Downstream consumers:** every other service that authenticates requests

## Related

- ADR-006 — Organisation as Outermost Tenancy Unit
- Section 2 — Member, Actor, Delegated Identity definitions
