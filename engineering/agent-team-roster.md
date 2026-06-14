---
confluence_id: "589848"
title: "Agent Team Roster"
---

# Agent Team Roster

The Oraclous engineering team operates as a multi-agent system with twelve role-bounded agents organised across five tiers, plus a human tech lead. Every story or feature flows through this team with explicit hand-offs and sign-off gates.

This page is the reference for who does what. Implementation of these agents lives in Claude Code skills and project configuration; the _roles_ documented here are stable across implementation changes.

## Architecture tier

**solution-architect** — Owns architectural coherence. Reviews briefs against the architecture document. Ensures stories conform to the four-layer model and named ADRs. Sign-off gate for stories that touch architectural boundaries.

**security-architect** — Owns security review. Reviews every PR against Section 6.5's threat catalogue. Has veto authority on PRs that compromise isolation, governance, or credential safety. Sign-off gate for any story marked `security`, `isolation`, or `organization_isolation`.

## Planning tier

**product-planner** — Decomposes features and epics into stories. Writes briefs that test-author and implementers will work from. Ensures stories are independently shippable, have clear acceptance criteria, and reference the relevant architecture sections or ADRs.

**tech-lead (human — Reza)** — Final sign-off authority. Resolves cross-tier disputes. Owns sprint planning and the prioritisation backlog. Makes the call when architecture, security, and implementation views disagree.

## Design tier

**experience-architect** — Owns the forward-looking product surface: end-user personas, the information-architecture / navigation model, user journeys, and UI/UX design, grounded in the **live** gateway capability surface (never the legacy app). The FE loop is simple: it **designs** each surface, **directs** the frontend agent to build it (opens the GitHub issue with the design as the brief), and **reviews/validates** the resulting PR from the user's perspective — approving via the `johnkennII` GitHub identity, paired with the CTO's craft review (the two together are the whole check). Files backend-gap Contracts when a journey needs an unexposed capability. Sits between the Planning tier and the Implementation tier. Coordinator-resident; never writes application or design-system code.

## Implementation tier

**test-author** — Writes the test suite for a story **before** implementation begins. Tests live in their own PR, reviewed and merged first. Per ADR-010, this role is non-negotiable; no implementation PR proceeds without prior test PR merge.

**backend-implementer** — Writes Python service code: substrate, capability registry, harness runtime, execution engine, application gateway. Operates against the merged test PR; implementation PRs reference it.

**frontend-implementer** — Writes TypeScript / React code for the customer-facing UI and the embeddable widgets. Operates against frontend tests (Vitest + Playwright) authored by test-author.

**devops-implementer** — Writes infrastructure code (Docker, deployment manifests, CI configuration, observability). Owns the operational concerns that the architecture document and Operations hub document.

## Review tier

**code-reviewer** — Reviews implementation PRs for code quality, design adherence, and architecture conformance. Sign-off gate before merge. Checks the implementation against the brief and the merged tests.

**qa-engineer** — Reviews tests and validates that they actually exercise the behaviour the brief describes. Authors additional regression tests when bugs surface. Sign-off gate for story closure.

## Documentation tier

**docs-writer** — Updates Confluence documentation (architecture sections, ADRs, engineering pages, service reference) when stories or features change platform behaviour. Owns the "documentation conforms to code, or code changes first" discipline.

## Hand-off pattern

A story flows through the tiers in this order:

1. **product-planner** writes the brief, references architecture sections and ADRs
2. **test-author** writes the test PR; **qa-engineer** and **security-architect** review it
3. **backend-implementer** / **frontend-implementer** / **devops-implementer** writes the implementation PR
4. **code-reviewer** reviews the implementation; **security-architect** reviews if any security marker applies; **solution-architect** reviews if any architectural boundary is touched
5. **qa-engineer** validates the implementation against the tests and the brief
6. **docs-writer** updates documentation if platform behaviour changed
7. **tech-lead** final sign-off; story closes

For **frontend product-surface** work the loop is shorter and gate-free: **experience-architect** designs the surface and opens the GitHub issue directly to the frontend agent (no product-planner middleman); the agent builds and opens a PR; experience-architect reviews/validates it from the user's perspective and the CTO reviews craft — together they decide the PR, approving via the `johnkennII` GitHub identity.

## Multi-agent etiquette

* Each agent operates within its tier. Cross-tier work (an implementer rewriting a test, an architect writing code) requires explicit hand-off, not silent overreach.
* Disagreements escalate up the tier ladder, not laterally. An implementer who disagrees with a reviewer escalates to tech-lead, not back to the test-author.
* The architecture document and ADRs are the shared contract every tier operates against. When an agent reads a section that needs clarification, the response is to write an ADR or a doc revision PR — not to interpret silently.
