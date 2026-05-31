---
confluence_id: "622756"
title: "auth-service"
---

# auth-service

**Layer:** 1 (Substrate) · **Port:** 8000 · **Status:** Production-grade (extension pending Phase 1)

## Purpose

`auth-service` is the platform's identity authority. It issues credentials, validates them on every authenticated request, and exposes the principal-type model the rest of the platform relies on for authorisation decisions.

## Responsibilities

* User authentication (email/password, OAuth flows for social login)
* JWT issuance and validation
* OAuth client registration for external integrations
* Principal-type discrimination: **user**, **service account**, **agent** (the third added in Phase 1)
* Delegated identity token issuance (Phase 1 extension, working with `credential-broker-service`)

## Dependencies

* **Upstream:** infrastructure only (Postgres for user records, Redis for session state)
* **Downstream consumers:** every other service that authenticates requests

## Current state

Production-grade. Well-scoped, single-responsibility, clean API. Handles members and service accounts cleanly today. The Phase 1 extension adds agent identity issuance alongside delegated identity tokens; the rest of the service stays as-is.

## Phase 1 deliverables

* Agent identity issuance (agents as principals alongside users and service accounts)
* ReBAC graph extensions for delegated relationships
* Migration scripts for existing agents to gain post-hoc identities

## Related

* ADR-006 — Organisation as Outermost Tenancy Unit
* Section 2 — Member, Actor, Delegated Identity definitions
* Section 6.5 — Threat 4 (identity confusion)
