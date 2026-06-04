---
confluence_id: "164160"
title: "09. Releases"
---

# 09. Releases

**Document status:** <custom data-type="status" data-id="id-0">Active</custom> · **Maintained by:** [tech-lead](https://oraclous.atlassian.net/wiki/spaces/OP/pages/983101) with input from [solution-architect](https://oraclous.atlassian.net/wiki/spaces/OP/pages/164068) and [product-planner](https://oraclous.atlassian.net/wiki/spaces/OP/pages/884840)

This is the home of **release-level planning**. Each child page is the execution contract for one release — what it delivers, what success looks like, which architectural commitments it implements, and how it relates to the Jira tickets that execute it. Release pages are the input to ticket creation, not the output.

## 1. What a release is in Oraclous

A **release** is a coherent slice of platform work with a defined goal, a measurable set of deliverables, and a status that can be checked at any point. Releases are the unit of _strategic_ planning. Tickets are the unit of _tactical_ execution. The relationship is one-to-many:

* One release produces many Jira tickets
* One ticket belongs to exactly one release
* Release status is derived from ticket status, but release scope is defined here, not in Jira

The release pages under this hub correspond to the phases described in [Section 8 — Consolidation and Migration Plan](https://oraclous.atlassian.net/wiki/spaces/OP/pages/688329). Section 8 is the _narrative_ describing why the migration is phased the way it is; the release pages are the _contracts_ against which each phase is executed and judged complete.

## 2. Why releases live in Confluence, not Jira

Three reasons this matters:

**Jira tickets are atomic; releases are not.** A ticket answers "what does someone do next?" A release answers "what does this slice of work deliver, why does it matter, and how do we know it shipped?" These are different documents with different audiences and different lifecycles. Conflating them loses the strategic intent and makes re-planning painful.

**Acceptance criteria are per-release, not per-ticket.** A release succeeds when its _deliverables_ are met, not when every ticket is closed. Tickets can be cancelled, deferred, split, or added without changing the release's acceptance criteria. The release page is the stable anchor.

**Re-planning is versioned.** When real-world feedback says a release's scope needs to change, the change is documented in this page's version history. The architectural reasoning behind the change is preserved. Doing the same thing across many tickets' descriptions loses that audit trail.

## 3. Standard release-page structure

Every page under this hub follows the same template. New release pages copy this structure verbatim and fill it in.

### Sections every release page must have

| Section | Purpose |
| --- | --- |
| **Header** | Release ID, status lozenge, target window (weeks), owner, dependencies |
| **Goal** | One paragraph: what this release achieves at the platform level. Not a list of tickets, not implementation detail. The reason this release exists. |
| **Scope** | Two sub-lists: what is in scope and what is explicitly out of scope. Out-of-scope items reference where they will be addressed (a later release, or out-of-scope per Section 9). |
| **Deliverables** | Bulleted list of concrete, measurable artifacts or behaviours. Each deliverable has an acceptance criterion. Format: _"Deliverable X — verified by Y"_. |
| **Migration source map** | Per-deliverable: what exists in the legacy codebase, the target shape, and the lift-vs-rewrite verdict. See Section 7 for the convention. Required for every release that touches code with a legacy precursor. |
| **Architecture references** | Links to the sections, ADRs, and structured artifacts this release implements. Bidirectional: this release page should be referenced from the architecture sections it executes. |
| **Threats addressed** | Tn-Mn mitigation IDs from the [Structured Threat Catalogue](https://oraclous.atlassian.net/wiki/spaces/OP/pages/983129) this release implements. Empty list is acceptable for non-security releases but must be explicit. |
| **Governance impact** | Which policy sets from the [Structured Governance Taxonomy](https://oraclous.atlassian.net/wiki/spaces/OP/pages/688439) this release enforces, modifies, or depends on. Often empty for early releases; populated as governance work lands. |
| **Risks** | Release-specific risk register. Each risk: description, likelihood, mitigation, owner. |
| **Dependencies** | Upstream (other releases that must complete first) and downstream (releases blocked by this one). |
| **Status** | One of: Planned · Briefed · In progress · Released · Superseded. Updated as the release moves. |
| **Sprint references** | Back-pointers to the Jira epics that execute this release. Populated by [product-planner](https://oraclous.atlassian.net/wiki/spaces/OP/pages/884840) after the release is briefed. |
| **Revision history** | Date · change · author · reason. Every scope change gets an entry. |

## 4. Release lifecycle

Every release moves through the same stages. The owning agent at each stage is named in brackets.

1. **Planned** \[tech-lead\] — page exists with goal and high-level scope. Deliverables may be placeholder.
2. **Briefed** \[solution-architect + tech-lead\] — deliverables, threats, governance, risks, _and the migration source map_ are filled in. Tech-lead has signed off. Ready for ticket creation.
3. **In progress** \[product-planner\] — Jira epics and stories have been created from this release. The sprint references section is populated. Tickets are being worked.
4. **Released** \[tech-lead\] — all deliverables met, all acceptance criteria ticked, tech-lead has accepted the release. Page status is updated, retrospective notes (if any) are added.
5. **Superseded** \[tech-lead\] — only used if a release is materially restructured. The original page is marked superseded with a forward-pointer; a new release page is created for the new shape. Used sparingly.

Tech-lead approval is required at the transitions _Planned → Briefed_ and _In progress → Released_. The other transitions are agent-driven. The migration source map (Section 7) must be complete before the Planned → Briefed transition.

## 5. How releases relate to Jira

The contract between this page and Jira:

| Concern | Where it lives |
| --- | --- |
| Release goal, scope, deliverables, threats, governance | Here, in the release page |
| Acceptance criteria for the release as a whole | Here, in the Deliverables section |
| Lift-vs-rewrite verdict per deliverable | Here, in the Migration source map (Section 7) |
| Epic-level breakdown of work | Jira — epics linked to one release via a custom field |
| Cross-repo shared shapes (Contracts) | Jira `Contract` issues + canonical home; see [Cross-cutting agreement protocol](https://oraclous.atlassian.net/wiki/spaces/OP/pages/1245185) |
| Story-level work units | Jira — stories under epics |
| Per-ticket acceptance criteria | Jira — story description |
| Which agent owns a ticket | Jira — `Agent Owner` custom field (see Section 6 below) |
| Status of individual work | Jira — ticket status |
| Status of the release as a whole | Here, in the release page Status field |

The release page's sprint references section is the bridge. It lists the Jira epic keys (e.g., `ORA-100: Phase 0.5 — organisation tenancy and metering`) that execute this release. Beyond that, the release page does not duplicate Jira state — it points to it.

## 6. Agent identity convention

All agents share a single Atlassian account (tech-lead's) when interacting with Jira and Confluence. To make agent actions targetable, auditable, and reviewable despite this, several conventions are enforced.

**This section is the canonical source of truth for the agent identity convention.** Section 11 of each agent skill page references this section. If this section disagrees with any agent skill page, this section wins; the skill page has drifted and a `docs-writer` ticket should be opened to reconcile it. Which session each agent runs in is recorded in [Session topology and persona residency](https://oraclous.atlassian.net/wiki/spaces/OP/pages/1736705); the board columns the operations move tickets between are in [Jira board and workflow mapping](https://oraclous.atlassian.net/wiki/spaces/OP/pages/1671170).

### 6.1 The `Agent Owner` Jira custom field

Every Jira issue in project `ORA` carries a single-select custom field named `Agent Owner`. Its values are the agent names from the [Agent Skills Catalogue](https://oraclous.atlassian.net/wiki/spaces/OP/pages/753852), plus `human` for tickets that require a human owner — **13 options in total**:

* `solution-architect`
* `security-architect`
* `product-planner`
* `tech-lead` _(the agent persona, distinct from the human tech-lead — used when an agent is preparing tech-lead-flavoured work for human review)_
* `test-author`
* `backend-implementer`
* `frontend-implementer`
* `devops-implementer`
* `code-reviewer`
* `qa-engineer`
* `be-test-reviewer` _(the narrow BE-only Tests Review verification persona; see its_ [_skill page_](https://oraclous.atlassian.net/wiki/spaces/OP/pages/1703937)_)_
* `docs-writer`
* `human` _(reserved for tickets that explicitly require human action — usually approval gates or strategic decisions)_

`Agent Owner` is the _current_ owner. It changes as the ticket moves through hands. The history of who owned the ticket when is preserved in comments (see 6.2) and in Jira's built-in change history.

**Implementation note (Jira field IDs):** The `Agent Owner` field is `customfield_10074` on this project's Jira instance. Each persona value is an option with its own option ID; the option for `human` is id `10031`. Agents that need to write the field via the Atlassian MCP should set it as `customfield_10074: {id: "OPTION_ID"}` rather than by display name. Field and option IDs are stable for this project; if they change, this page is the canonical place to record the change.

### 6.2 The `needs-human` attention flag

When an agent escalates a ticket because it requires human judgment, three things happen in addition to setting `Agent Owner = human`: the `needs-human` flag is set, the ticket is transitioned to **BLOCKED**, and a structured escalation comment is posted (see 6.3 and the `escalate_to_human` operation in 6.4).

**Implementation note (Jira field ID):** `needs-human` is implemented as a **multi-checkbox custom field** on this project's Jira instance — not as a plain Jira label. The field is `customfield_10075`; the option for `needs-human` is id `10032`. Agents tick the checkbox by setting `customfield_10075: [{id: "10032"}]` via the Atlassian MCP. Removing the flag is done by setting the field to `[]`.

The multi-checkbox shape is deliberate. It is controlled (you cannot typo it), it cannot be removed by someone unfamiliar with the convention, and it is more queryable on boards than free-form labels. Queries that find tickets needing human attention use:

```
project = ORA AND cf[10075] = "needs-human"
```

or, equivalently, the JQL `"Needs Human" = "needs-human"` if the field display name is configured. Agents should prefer the field-ID form because it is unambiguous.

**BLOCKED means "human, you are the unblock."** The BLOCKED column is reserved for human-escalated tickets. A ticket that is merely waiting on another ticket (a dependency, an unagreed Contract) does _not_ go to BLOCKED — it stays in its current column, keeps its agent owner, and links the blocker via an "is blocked by" link. See [Jira board and workflow mapping](https://oraclous.atlassian.net/wiki/spaces/OP/pages/1671170) Section 2.

### 6.3 The agent comment-prefix convention

Every comment, worklog, and Confluence inline comment posted by an agent **must** begin with the line:

```
[agent:NAME]
```

where `NAME` is the agent persona writing the comment. The same prefix applies to GitHub commit messages and PR descriptions written by an agent.

When a comment closes with a meaningful action (status change, hand-off, escalation, completion, observation, review request), it ends with a structured trailer:

```
---\nagent: NAME\naction: handoff_to | status_change | escalation | observation | review_request | complete\nto: AGENT_NAME (for handoff_to)\nfrom_status: STATUS (for status_change)\nto_status: STATUS (for status_change)
```

This makes agent actions parseable from comment history without relying on Jira's actor field (which always reflects the human Atlassian account the agents share). The `from_status` trailer on an escalation is what lets the human return a BLOCKED ticket to the column it came from.

### 6.4 The agent-Jira operation set

The conventions in 6.1, 6.2, and 6.3 are codified as operations every agent skill page documents. The operations are:

| Operation | What it does |
| --- | --- |
| `my_tasks` | JQL: `project = ORA AND "Agent Owner" = $self AND status != Done ORDER BY priority DESC` |
| `claim_next` | Find the highest-priority unassigned ticket where the role matches the agent, set `Agent Owner = $self`, transition to In Progress, post a claim comment with the `[agent:NAME]` prefix |
| `handoff_to` | Set `Agent Owner` to the target agent, transition status as appropriate, post a handoff comment naming the target and including the `action: handoff_to` trailer |
| `escalate_to_human` | (1) Set `Agent Owner = human`. (2) Tick the `needs-human` checkbox (set `customfield_10075: [{id: "10032"}]`). (3) **Transition the ticket to BLOCKED** (recording the originating column in the comment's `from_status` trailer so it can be returned). (4) Post a structured escalation comment with the `action: escalation` trailer and the specific reason. All four writes happen together; partial escalations are bugs. |
| `complete` | Transition to Done, post a completion comment summarising what was delivered against the ticket's acceptance criteria, with the `action: complete` trailer |
| `observe` | Post a comment with the `action: observation` trailer — used to record findings or context without changing ownership or status |
| `review_request` | Set `Agent Owner` to the appropriate reviewer (`be-test-reviewer` for the BE Tests Review gate, `code-reviewer` for craft, `qa-engineer` for QA), transition to the matching review column, post a structured review-request comment with the `action: review_request` trailer. Decision-level architecture/security questions escalate up to `solution-architect`/`security-architect` in the coordinator session rather than being reviewed in the repo. |
| `open_contract` | When a cross-repo shared shape is needed, create a `Contract` issue (type id `10049`) with `Agent Owner = solution-architect` and stop; do not define the shape locally. See [Cross-cutting agreement protocol](https://oraclous.atlassian.net/wiki/spaces/OP/pages/1245185). |

For v1, these operations are implemented as _skill instructions_ — each agent skill page documents the exact JQL query, comment format, and field updates the agent uses. From R7 onward they become Capability Registry entries (the small standalone agent-MCP server listed as an R7 deliverable) and the skill instructions point at them.

### 6.5 Known drift in agent skill pages — to be reconciled

The Section 11 inserts on the original 11 agent skill pages currently describe `needs-human` as a plain Jira label rather than the multi-checkbox custom field, and predate the BLOCKED-transition addition to `escalate_to_human`. This is documentation drift; the Jira reality (and this section) is correct. A `docs-writer` ticket reconciles the skill pages in the first sprint of normal loop operation. Until that ticket lands, agents reading their own Section 11 should follow this section's description (6.2 + 6.4 `escalate_to_human`) over their skill page's wording on this point. (The `be-test-reviewer` page, authored later, already reflects the BLOCKED transition.)

Tracking: the reconciliation work is captured by Architecture Revision History (page [426111](https://oraclous.atlassian.net/wiki/spaces/OP/pages/426111)).

## 7. Migration source maps: the lift-vs-rewrite convention

This migration is a _migration_, not a rewrite. The current Oraclous codebase has production-grade ingredients (see [Section 8](https://oraclous.atlassian.net/wiki/spaces/OP/pages/688329)) that are mostly to be reorganised, not rebuilt. The default bias is therefore **lift, not rewrite** — and that bias has to be written into the planning artifacts, or each implementer silently re-decides it per ticket and drifts toward greenfield because greenfield feels safer in isolation.

**The legacy codebase is always at minimum the behavioural specification — even when its code is not reusable.** New code passes when it does what the legacy did, plus the architectural invariants. "Start from scratch" is the exception that must be justified, not the default.

### 7.1 Project-specific defaults

* **Frontend (**`oraclous-frontend`**):** the previous frontend is a working application. The default is **clone-and-refactor** — the new repo is seeded from the legacy frontend's contents and refactored in place to the target stack, design system, and gateway-only API rule. Greenfield is the exception.
* **Backend (**`oraclous-backend`**):** most existing services are production-grade and correctly factored (`auth-service`, `credential-broker-service`) or sprawling-but-salvageable (`knowledge-graph-builder`). The default per service is **lift-and-reshape** against the four-layer model — populate the new repo from the legacy service, then refactor under TDD to the target layer and conventions. Greenfield applies only to genuinely new surfaces (e.g. the application gateway, which has no clean legacy precursor).

### 7.2 The lift-vs-rewrite rubric

For each deliverable that touches code with a legacy precursor, the verdict is reached by walking this rubric. It produces one of four tags: **Lift**, **Reshape**, **Extract**, or **Greenfield**.

| Question | If yes | If no |
| --- | --- | --- |
| Does the legacy implement this behaviour? | Continue rubric | **Greenfield** is correct; skip the rest |
| Is the legacy behaviour correct per the brief and the architecture? | Continue | The behaviour itself is wrong; **Greenfield** (but legacy is still the spec of what NOT to do) |
| Does the legacy already sit at the target layer boundary? | **Lift** directly (light refactor only) | **Reshape** to fit the boundary, keep the logic |
| Does the legacy already use target conventions (organisation_id, OHM, ReBAC, fail-closed)? | **Lift** directly | **Reshape** conventions, keep the logic |
| Is this behaviour entangled in a larger legacy service that must be split? | **Extract** — lift the behaviour out into its target service | Lift or Reshape as above |
| Does the legacy have tests for this behaviour? | **Lift the tests first**, then the code (see 7.3) | Author new tests; legacy code is still the behavioural spec |

### 7.3 Tests are lifted before code

For any deliverable tagged Lift, Reshape, or Extract where legacy tests exist and remain valid, the [test-author](https://oraclous.atlassian.net/wiki/spaces/OP/pages/294957)'s **first** action is to port the legacy tests for that behaviour into the new test taxonomy (with the correct markers), and confirm they fail against the empty new code. Only then are new tests authored for new behaviour. This is the cheapest, highest-fidelity way to capture "behaviour to preserve" as something executable. The brief names the specific legacy test files.

### 7.4 The Migration source map section

Every release page that touches code with a legacy precursor carries a **Migration source map** section, filled in before the Planned → Briefed transition. One row per deliverable:

| Deliverable | Source in legacy (path) | Target shape | Verdict |
| --- | --- | --- | --- |
| The deliverable from the Deliverables section | The legacy file(s) that implement it, or "none" | The target layer + conventions it must adopt | Lift / Reshape / Extract / Greenfield |

**Ownership of the source map:** [product-planner](https://oraclous.atlassian.net/wiki/spaces/OP/pages/884840) owns the verdicts and the structure; [solution-architect](https://oraclous.atlassian.net/wiki/spaces/OP/pages/164068) signs off the target-shape column (it is an architecture call); [security-architect](https://oraclous.atlassian.net/wiki/spaces/OP/pages/557195) flags any row that carries a threat. All three are coordinator-session personas. The completed source map is part of the Planned → Briefed gate. Each verdict propagates into the stories the planner creates: a Lift/Reshape/Extract story names its legacy source path in the brief, so the implementer starts from the legacy code rather than a blank file.

The original 11 agent skill pages do not yet describe the lift-vs-rewrite rubric or the lift-tests-first rule in their bodies. This is acknowledged drift, reconciled by the same first `docs-writer` ticket that fixes the `needs-human` wording (Section 6.5). Until then, this Section 7 is canonical and the relevant skill pages (test-author, backend-implementer, frontend-implementer, solution-architect) defer to it.

## 8. Status overview

The release pages under this hub are listed below with their current status. This table is the single-glance view of where the migration stands.

> **Roadmap pivot (2026-06-04):** R2 and R3 shipped **hollow** (stub endpoints, dead `oraclous-core-service` logic, dropped auth). The old R4–R8 roadmap and the gateway-from-R5 vertical-slice plan are **superseded by [R3.5 — Make every service real](r3.5-make-every-service-real.md)**, which rebuilds every backend service real, end-to-end, **per service** (each Reza-accepted before the next), per ORAA-4 §21–§23.

| Release | Title | Window | Status |
| --- | --- | --- | --- |
| R0 | Phase 0 — Documentation and stabilisation | Weeks 1-2 | <custom data-type="status" data-id="id-1">Released</custom> (effectively complete with Architecture v1.1 + ADRs + Group B/C artifacts) |
| R0.5 | Phase 0.5 — Organisation tenancy and metering substrate | Weeks 3-4 | <custom data-type="status" data-id="id-2">Planned</custom> |
| R1 | Phase 1 — Auth and credential extensions | Weeks 5-6 | <custom data-type="status" data-id="id-3">Planned</custom> |
| R2 | Phase 2 — Capability registry consolidation | Weeks 7-10 | <custom data-type="status" data-id="id-4">Planned</custom> |
| R3 | Phase 3 — Knowledge graph decomposition | Weeks 11-16 | <custom data-type="status" data-id="id-5">Superseded</custom> (shipped hollow; redone under R3.5) |
| **[R3.5](r3.5-make-every-service-real.md)** | **Make every service real** — graph-first per-service rebuild (ingest → retrieve → identity/org → credential-broker → capability-registry → gateway) | Opens 2026-06-04; sequential until each service is Reza-accepted | <custom data-type="status" data-id="id-35">Active</custom> (**supersedes R4–R8 + the gateway-from-R5 plan**) |
| R4 | Phase 4 — Harness runtime extraction | Weeks 17-20 | <custom data-type="status" data-id="id-6">Superseded</custom> (by R3.5) |
| R5 | Phase 5 — Execution engine and runtime completion | Weeks 21-24 | <custom data-type="status" data-id="id-7">Superseded</custom> (by R3.5) |
| R6 | Phase 6 — Application Gateway extraction | Weeks 25-28 | <custom data-type="status" data-id="id-8">Superseded</custom> (gateway is R3.5 step 6) |
| R7 | Phase 7 — Compiler harness and seed manifests | Weeks 29-32 | <custom data-type="status" data-id="id-9">Superseded</custom> (by R3.5) |
| R8 | Phase 8 — Security hardening pass | Weeks 33-36 | <custom data-type="status" data-id="id-10">Superseded</custom> (now a per-service R3.5 gate) |
| RC | Compliance track — ISO 27001 + SOC 2 Type II | Parallel from R0.5 onward | <custom data-type="status" data-id="id-11">Planned</custom> |
| RF | Frontend track — repo, console, portal, widget SDK | Parallel from R0.5; end-to-end at R6 | <custom data-type="status" data-id="id-12">Proposed</custom> (page pending tech-lead creation) |

Phase 9 (continuous evolution) does not get a release page — it is the post-v1 state, governed by future release planning.

## 9. Related references

* [Section 8 — Consolidation and Migration Plan](https://oraclous.atlassian.net/wiki/spaces/OP/pages/688329) — the narrative this hub executes against; the source of truth for what lifts, reshapes, extracts, and retires
* [10. Engineering Flows](https://oraclous.atlassian.net/wiki/spaces/OP/pages/1212418) — the work-breakdown hierarchy and the cross-cutting agreement protocol
* [Session topology and persona residency](https://oraclous.atlassian.net/wiki/spaces/OP/pages/1736705) and [Jira board and workflow mapping](https://oraclous.atlassian.net/wiki/spaces/OP/pages/1671170) — the session structure and board the operations in Section 6 run against
* [Section 9 — Deferred and Out-of-Scope](https://oraclous.atlassian.net/wiki/spaces/OP/pages/65988) — what is intentionally not in any release
* [Agent Skills Catalogue](https://oraclous.atlassian.net/wiki/spaces/OP/pages/753852) — the agents that own release work
* [Architecture Revision History](https://oraclous.atlassian.net/wiki/spaces/OP/pages/426111) — material changes to architecture documents during releases are recorded there in addition to release pages
* [Agent and Skill Change Log](https://oraclous.atlassian.net/wiki/spaces/OP/pages/426078) — agent-team changes triggered by releases are recorded there
