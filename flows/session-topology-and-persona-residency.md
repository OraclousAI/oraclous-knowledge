# Session topology and persona residency

**Document status:** Active · **Owned by:** tech-lead

This page is the canonical record of which Claude Code session runs where, and which agent personas each session may load.

## Three sessions

| Session | Working directory | Role |
| --- | --- | --- |
| **Coordinator** | `/Users/reza/workspace/OraclousAI/` | Planning, architecture, cross-cutting agreement, infra, documentation. Never application code. |
| **Backend** | `/Users/reza/workspace/OraclousAI/oraclous-backend/` | Backend execution: tests, implementation, review, QA. |
| **Frontend** | `/Users/reza/workspace/OraclousAI/oraclous-frontend/` | Frontend execution: implementation. |

## Persona residency

| Persona | Session |
| --- | --- |
| product-planner | Coordinator |
| solution-architect | Coordinator |
| security-architect | Coordinator |
| devops-implementer | Coordinator (operates on both repos) |
| docs-writer | Coordinator (operates on both repos) |
| test-author | Backend |
| be-test-reviewer | Backend |
| backend-implementer | Backend |
| code-reviewer | Backend |
| qa-engineer | Backend |
| frontend-implementer | Frontend |
| tech-lead (human) | All three |

## How dual residency was avoided

The backend Tests Review gate is owned by `be-test-reviewer` — a distinct narrow persona that lives only in the backend session. No persona is dual-resident.

## Cross-session coordination protocol

- **Single source of coordination state is Jira.** `Agent Owner` field tells every session who holds a ticket.
- **Handoffs cross sessions through the field.** When coordinator sets `Agent Owner = test-author`, the backend session picks it up.
- **Escalations travel up to the coordinator.** A repo session that hits an architecture question sets `Agent Owner` to the relevant root persona.
