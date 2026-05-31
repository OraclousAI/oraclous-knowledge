---
confluence_page_id: "1671170"
title: "Jira board and workflow mapping"
---

**Document status:** Active · **Parent:** [10. Engineering Flows](https://oraclous.atlassian.net/wiki/spaces/OP/pages/1212418) · **Owned by:** [product-planner](https://oraclous.atlassian.net/wiki/spaces/OP/pages/884840) with [tech-lead](https://oraclous.atlassian.net/wiki/spaces/OP/pages/983101) sign-off

This page is the canonical mapping between the work-breakdown flow ([10. Engineering Flows](https://oraclous.atlassian.net/wiki/spaces/OP/pages/1212418)) and the actual ORA Jira board. It records the eight columns, which workflow status each represents, which agent owns a ticket sitting in each column, and how the orthogonal signals (`needs-human`, issue type) surface on the board.

## 1. The eight columns

The ORA board (team-managed) has eight columns. Seven are the linear flow; BLOCKED is orthogonal.

| Column | WIP limit | Flow state | Owning agent while a ticket sits here |
| --- | --- | --- | --- |
| BACKLOG | — | Briefed but not yet ready; or unbriefed | product-planner (or unowned) |
| READY | — | Brief approved, architecture + threat review passed, awaiting pickup | test-author (BE work); frontend-implementer (FE work, since FE tests are deferred — see §4) |
| TESTS AUTHORING | 3 | Failing tests being authored | test-author |
| TESTS REVIEWS | 3 | The `[tests]` PR under review | be-test-reviewer |
| IMPLEMENTATION | 5 | Code being written to turn tests green | backend-implementer (BE); frontend-implementer (FE) |
| CODE REVIEW | 5 | The `[impl]` PR under review | code-reviewer + qa-engineer (BE); human tech-lead (FE — manual, see §4) |
| DONE | — | Shipped, all gates passed | — (transitioned to Done by the human tech-lead) |
| BLOCKED | — | Cannot proceed — human action required | `human` (see §2) |

The WIP limits on the four middle columns are deliberate: test authoring and review are kept narrow (3) because they are the quality bottleneck; implementation and code review run wider (5). An agent that would exceed a WIP limit waits rather than starting new work in that column.

## 2. BLOCKED means "human, you are the unblock"

BLOCKED is reserved for tickets that cannot proceed **without human action**. A ticket enters BLOCKED only via the `escalate_to_human` operation: `Agent Owner` is set to `human`, the `needs-human` checkbox (`customfield_10075`, option id `10032`) is ticked, a structured escalation comment is posted, _and_ the ticket is transitioned to BLOCKED. All four happen together.

A ticket that is merely waiting on another ticket (an unmerged dependency, a Contract not yet agreed) does **not** go to BLOCKED. It stays in its current column, keeps its agent owner, and links the blocker via a Jira "is blocked by" link. This keeps BLOCKED meaning exactly one thing — _Reza needs to act_ — rather than becoming a generic stuck-pile. Dependency pressure is already visible through the issue links and the WIP limits.

Exit from BLOCKED: the human acts, unticks `needs-human`, sets `Agent Owner` back to the appropriate agent, and transitions the ticket back to the column it came from (recorded in the escalation comment's `from_status` trailer).

## 3. Orthogonal signals are not columns

* `needs-human` is a flag (`customfield_10075`), not a column. It is ticked on tickets in BLOCKED. A board quick-filter `cf[10075] = "needs-human"` highlights all human-blocked tickets at a glance.
* **Issue type** (Epic, Story, Task, Bug, Spike, ADR, Contract, Feature, Subtask) is orthogonal to column. A `Contract` (id `10049`) and an `ADR` (id `10016`) both flow through the same columns; their distinguishing property is that their real output is a Confluence page and the Jira issue is the workflow tracker. A `Spike` (id `10015`) likewise outputs Confluence documentation, not code.

## 4. The frontend asymmetry (deliberate, temporary)

Frontend work currently has **no test-authoring, test-review, or code-review agent**. FE tests are deferred and FE code review is performed manually by the human tech-lead. This is a deliberate, temporary asymmetry to be re-evaluated at the R-Frontend Phase B milestone. Until then, FE tickets move READY → IMPLEMENTATION → CODE REVIEW (human) → DONE, skipping the two test columns. The FE invariants that would otherwise be caught at review (gateway-only API rule, no token in `localStorage`, WCAG AA via axe-core) are enforced by CI gates in the FE repo, so the asymmetry removes _agents_, not _enforcement_.

## 5. Agent Owner field and issue types — recorded IDs

* `Agent Owner` = `customfield_10074`, single-select, **13 options**: the 11 original personas, plus `human` (option id `10031`), plus `be-test-reviewer` (the BE-only Tests Review persona — see its [skill page](https://oraclous.atlassian.net/wiki/spaces/OP/pages/753852)).
* `needs-human` = `customfield_10075`, multi-checkbox, option id `10032`.
* `Contract` issue type = id `10049`; `ADR` = `10016`; `Spike` = `10015`.

## 6. Related references

* [10. Engineering Flows](https://oraclous.atlassian.net/wiki/spaces/OP/pages/1212418) — the work-breakdown hierarchy this board realises
* [09. Releases](https://oraclous.atlassian.net/wiki/spaces/OP/pages/164160) Section 6 — the Agent Identity Convention and the operation set (including the updated `escalate_to_human` that transitions to BLOCKED)
* [Cross-cutting agreement protocol](https://oraclous.atlassian.net/wiki/spaces/OP/pages/1245185) — the Contract flow
