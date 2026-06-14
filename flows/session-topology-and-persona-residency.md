---
confluence_id: "1736705"
title: "Session topology and persona residency"
---

**Document status:** <custom data-type="status" data-id="id-0">Active</custom> · **Parent:** [10. Engineering Flows](https://oraclous.atlassian.net/wiki/spaces/OP/pages/1212418) · **Owned by:** [tech-lead](https://oraclous.atlassian.net/wiki/spaces/OP/pages/983101)

This page is the canonical record of **which Claude Code session runs where, and which agent personas each session may load**. It is the structure that makes the work-breakdown flow conflict-free: every persona lives in exactly one session, so two sessions can never act as the same `Agent Owner` on the same ticket.

## 1. Three sessions

| Session | Base repo | Role |
| --- | --- | --- |
| **Coordinator** | `/Users/reza/workspace/OraclousAI/` (workspace root) | Planning, architecture, cross-cutting agreement, infra, documentation. Produces Confluence pages and Jira tickets; never application code. |
| **Backend** | `/Users/reza/workspace/OraclousAI/oraclous-backend/` | Backend execution: tests, implementation, review, QA. |
| **Frontend** | `/Users/reza/workspace/OraclousAI/oraclous-frontend/` | Frontend execution: implementation. Tests deferred; review is manual by the human. |

Each run executes in its own git worktree at `<base-repo>/.worktrees/<run-id>/`; runs within the same session do not share a working tree.

The human `tech-lead` (Reza) operates across all three and is the final sign-off on every human gate.

## 2. Persona residency — every persona lives in exactly one session

| Persona | Session | What it does there |
| --- | --- | --- |
| product-planner | Coordinator | Epics, Contracts, Stories, briefs, migration source maps, backlog |
| experience-architect | Coordinator | End-user personas, IA/navigation model, user journeys, UI/UX design; directs FE product-surface work (opens the GitHub issue with the design) and reviews/validates the PR from the user's perspective (approving via the `johnkennII` identity, paired with the CTO); backend-gap Contracts |
| solution-architect | Coordinator | Architecture review, Contract drafting, target-shape sign-off on source maps |
| security-architect | Coordinator | Threat modelling, threat tagging, security review of Contracts |
| devops-implementer | Coordinator (operates _on_ both repos) | `[impl-infra]` PRs against either repo: CI, containers, deployment, contract-test fixtures. Never application code. |
| docs-writer | Coordinator (operates _on_ both repos) | Confluence reconciliation; `[docs]` PRs against either repo for CLAUDE.md, READMEs, service refs. Never application code. |
| test-author | Backend | Authors `[tests]` PRs |
| be-test-reviewer | Backend | Reviews `[tests]` PRs at the Tests Review gate (the narrow BE-only architecture+security verification persona) |
| backend-implementer | Backend | Authors `[impl]` PRs |
| code-reviewer | Backend | Reviews `[impl]` PRs |
| qa-engineer | Backend | Verifies suite, coverage, regressions |
| frontend-implementer | Frontend | Authors frontend `[impl]` PRs |
| tech-lead (human) | All three | Final sign-off; FE code review; release acceptance |

## 3. How dual residency was avoided

The two architecture personas (`solution-architect`, `security-architect`) are needed both for coordinator-level planning _and_ for the backend Tests Review gate. Rather than letting them reside in two sessions — which would let two sessions act as the same `Agent Owner` — the backend Tests Review gate is owned by a **distinct narrow persona**, [be-test-reviewer](https://oraclous.atlassian.net/wiki/spaces/OP/pages/1703937), that lives only in the backend session. It verifies tests against architecture decisions the root architects have already made, and escalates decision-level problems back to the root `solution-architect` / `security-architect`. No persona is dual-resident; no custom "who is acting now" rule is needed.

## 4. Coordinator persona routing

The coordinator session can load six personas. It chooses by task:

| Task | Load |
| --- | --- |
| Decompose a release; author epics/stories/briefs; fill a migration source map; groom backlog | product-planner |
| Design a user journey / IA / UI-UX for a product surface; build the capability-surface inventory; author end-user personas; review an FE build from the user lens; file a journey→backend-gap Contract | experience-architect |
| Review a brief's architecture; draft a Contract; sign off a source map's target-shape column; answer a be-test-reviewer escalation | solution-architect |
| Threat-model; tag threats on a brief; review a security-touching Contract | security-architect |
| CI, container, deployment, or contract-test-fixture work on either repo | devops-implementer |
| Confluence reconciliation; repo-level docs (CLAUDE.md, README, service refs) | docs-writer |

The coordinator **never** loads test-author, be-test-reviewer, backend-implementer, frontend-implementer, code-reviewer, or qa-engineer — those need a specific repo's filesystem and live in the repo sessions.

## 5. Cross-session coordination protocol

* **Single source of coordination state is Jira.** The `Agent Owner` field tells every session who currently holds a ticket. Before any session claims a ticket, it checks `Agent Owner`; if another session's persona owns it, it does not claim.
* **Handoffs cross sessions through the field.** When the coordinator's `product-planner` moves a story to READY and sets `Agent Owner = test-author`, the backend session picks it up on its next `claim_next`. Neither session needs to talk to the other directly — the board is the channel.
* **Escalations travel up to the coordinator.** A repo session that hits an architecture or contract question sets `Agent Owner` to the relevant root persona (`solution-architect` / `security-architect` / `product-planner`); the coordinator picks it up.
* **Human escalations go to BLOCKED.** Any session's `escalate_to_human` sets `Agent Owner = human`, ticks `needs-human`, and transitions to BLOCKED. See [Jira board and workflow mapping](https://oraclous.atlassian.net/wiki/spaces/OP/pages/1671170).

## 6. The frontend asymmetry

The frontend session currently loads only `frontend-implementer`. FE tests, test review, and code review are deferred; FE craft review is manual by the human `tech-lead`. FE invariants (gateway-only API, no token in `localStorage`, WCAG AA) are enforced by CI, not by a review agent. Re-evaluate at R-Frontend Phase B. See [Jira board and workflow mapping](https://oraclous.atlassian.net/wiki/spaces/OP/pages/1671170) Section 4.

For **product-surface** FE work, the Coordinator-resident `experience-architect` adds two touchpoints that do not change FE session residency, and **no process gate**: (a) it **designs and directs** — opens the GitHub issue to the frontend agent with the journey+IA+UX design as the brief; and (b) it **reviews/validates the PR** from the user's perspective and approves via the `johnkennII` GitHub identity, parallel to the CTO's craft review (surface-drift or a non-negotiable violation is a request-changes even when the code is correct). Those two agent reviews are the whole check on a product-surface PR; the automated FE invariant CI runs on its own.

## 11. Session residency — AGENTS.md §11 template

The following block is the canonical §11 injected into every persona's AGENTS.md bundle during assembly. The `<session>` and `<base-repo>` placeholders are substituted from the persona's row in Section 1 and Section 2.

```
- Resides in the **<session>** session. Base repo: `<base-repo>`.
- Each run is isolated in its own git worktree at `<base-repo>/.worktrees/<run-id>/`; runs do not share a working tree.
- Every persona lives in exactly one session; two sessions never act as the same Agent Owner.
- Single source of coordination state is Jira. Check the `Agent Owner` field before claiming any ticket; if another session's persona owns it, do not claim.
- Handoffs cross sessions through the `Agent Owner` field, not direct messaging — the board is the channel.
- Escalations travel up to the coordinator personas (solution-architect / security-architect / product-planner). Human escalations go to BLOCKED with `Agent Owner = human` and the `needs-human` tag.
```

## 12. Related references

* [10. Engineering Flows](https://oraclous.atlassian.net/wiki/spaces/OP/pages/1212418) — the work-breakdown hierarchy
* [Jira board and workflow mapping](https://oraclous.atlassian.net/wiki/spaces/OP/pages/1671170) — columns, owners, BLOCKED semantics
* [be-test-reviewer](https://oraclous.atlassian.net/wiki/spaces/OP/pages/1703937) — the narrow BE Tests Review persona
* [Cross-cutting agreement protocol](https://oraclous.atlassian.net/wiki/spaces/OP/pages/1245185)
* [Agent Skills Catalogue](https://oraclous.atlassian.net/wiki/spaces/OP/pages/753852)
