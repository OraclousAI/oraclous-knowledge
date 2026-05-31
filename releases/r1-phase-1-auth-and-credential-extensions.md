# R1 — Phase 1: Auth and credential extensions

| Release ID | R1 |
| --- | --- |
| Status | Done |
| Window | Weeks 5-6 (parallel with end of R0.5) |
| Owner | tech-lead |

## Goal

Extend `auth-service` and `credential-broker-service` with agent identity as a first-class principal type, delegated identity from a member to an agent, and ReBAC graph extensions for delegated relationships.

## Deliverables

- [x] Agent principal type in auth-service
- [x] Delegated identity tokens in credential-broker-service
- [x] ReBAC graph extensions (`delegated_by`, `delegated_to` relations)
- [x] Migration scripts for pre-R1 agents
- [x] Test coverage for adversarial cases (forged delegation, expired delegation, scope creep, revocation race)

## Jira epics

- ORA-25 — Epic A: Agent identity (ORA-30, ORA-31)
- ORA-26 — Epic B: Delegated identity tokens (ORA-32, ORA-33)
- ORA-27 — Epic C: ReBAC delegation (ORA-34, ORA-35)
- ORA-28 — Epic D: Pre-R1 agent migration (ORA-36)
- ORA-29 — Epic E: Adversarial test gate (ORA-37)
