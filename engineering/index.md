---
confluence_id: "65923"
title: "03. Engineering"
---

# 03. Engineering

This hub anchors the engineering documentation that governs how the Oraclous Platform is built. These pages describe the process — workflows, conventions, gates — not the architecture itself (which lives under the Architecture hub) and not service specifics (which live under Services Reference).

## Process

* [Test Strategy](https://oraclous.atlassian.net/wiki/spaces/OP/pages/720940) — test pyramid, markers, CI gates, test authorship
* [Git Workflow](https://oraclous.atlassian.net/wiki/spaces/OP/pages/131103) — branching model, commit conventions, merge strategy
* [PR Conventions](https://oraclous.atlassian.net/wiki/spaces/OP/pages/393465) — PR sizing, description template, review expectations
* [Code Style Guide](https://oraclous.atlassian.net/wiki/spaces/OP/pages/426037) — Python and TypeScript conventions
* [Definition of Done](https://oraclous.atlassian.net/wiki/spaces/OP/pages/66010) — gates a story must clear before closure
* [Release Process](https://oraclous.atlassian.net/wiki/spaces/OP/pages/426058) — versioning, cadence, rollback, deprecation

## Team

* [Agent Team Roster](https://oraclous.atlassian.net/wiki/spaces/OP/pages/589848) — the eleven role-bounded agents and one human tech lead

## How these pages relate

The engineering documentation operates as a chain. Reading top-to-bottom:

1. **Agent Team Roster** names who does what
2. **Test Strategy** says what gets written first (per ADR-010)
3. **Git Workflow** + **PR Conventions** + **Code Style Guide** govern how the work itself happens
4. **Definition of Done** says when work is finished
5. **Release Process** says how finished work reaches production

A new contributor reading these in order should be able to pick up and execute the team's workflow without further onboarding.

## Authority

These pages are the engineering team's contract. They override ad-hoc decisions; when reality and these pages disagree, the resolution is to either update the page or change reality. Silent drift is the failure mode the documentation exists to prevent.

When a story or PR proposes something these pages don't cover, the response is to either (a) add a section to the relevant page, or (b) write an ADR if the addition is architectural. Inline interpretation across a PR thread does not establish policy.

## Agent-governance gates are enforced in ORAA-4

The mechanical governance gates that agents run on — the pre-push gate, one-commit-per-concern, the mergeability gate, dedup-before-fix-ticket, the fail-closed unblock rule, branch-from-merged-tests, rebase-on-merge, the release-seam retrospective, and the destructive-change protocol — are **enforced** in the operating contract (ORAA-4). The pages in this hub **restate those rules for humans**, in each page's own voice. They are not the enforcement surface; ORAA-4 is.

Because the rule lives in two places by design (enforced in ORAA-4, restated here), the two **must be kept in sync**. These KB pages are not a place to quietly diverge from the contract: when they disagree with ORAA-4, ORAA-4 wins, and the divergence is a docs bug to fix.

### Governance-change checklist

Any change to a mechanical agent-governance rule must update **all three** surfaces together, in the same change set:

1. **ORAA-4** — the operating contract (the enforcement surface).
2. **The agent bundles** — both the live instances **and** the roster templates they are cloned from. (Updating instances without templates means the next clone regresses.)
3. **These KB pages** — the human-facing restatement in this hub.

A governance change that touches only one or two of these is incomplete and leaves the surfaces inconsistent. Record the change in the [Agent and Skill Change Log](https://oraclous.atlassian.net/wiki/spaces/OP/pages/426078).
