---
confluence_id: "393465"
title: "PR Conventions"
---

# PR Conventions

This page defines the structure, sizing, and review expectations for pull requests in both repositories. It complements the Git Workflow page (which covers branching and commits) by focusing on the _review experience_.

## PR sizing

PRs should be small enough to review carefully in one sitting. Concretely:

* **Target:** under 300 lines of net change (additions + deletions, excluding generated files and lock files)
* **Acceptable:** 300–600 lines, if the change is cohesive (one concern, one architectural area)
* **Requires justification:** 600+ lines, with the PR description explaining why splitting is not possible
* **Almost always too big:** 1,000+ lines, except for mechanical refactors (renames, type-only changes, generated code)

The goal is not the line count itself; the goal is reviewability. A 1,500-line PR that adds one new file with clear structure may be easier to review than a 200-line PR that touches twelve files across three services.

## PR description template

Every PR has a description following this structure:

**Summary** — one or two sentences naming what changes and why. The reader should understand the _intent_ without scrolling.

**Architectural context** — references to the architecture section or ADR that motivates the change. If the PR introduces new architectural decisions, those are written as ADRs (in this Confluence space) before the PR opens, not in the PR description.

**Test PR reference** — for implementation PRs, link to the test-author PR that this implements against. Show that the previously-failing tests now pass.

**Scope of change** — bulleted list of what changed at the architectural or service-boundary level. Not a line-by-line diff explanation; the diff is the diff.

**Out of scope** — explicit list of things the PR deliberately does _not_ do. Prevents reviewer scope creep ("could you also fix X while you're in here?") and documents the limited intent.

**Testing notes** — any non-obvious aspects of how the change is tested (specific markers run, manual steps for integration tests, etc.).

**Deployment notes** — anything special the devops-implementer needs to know (migration scripts, feature flags, ordering constraints).

## Review expectations

The code-reviewer (always) reviews for:

* Architecture conformance (does this respect the four-layer model and named ADRs?)
* Test alignment (does the implementation actually satisfy the merged test PR?)
* Code quality (readability, naming, error handling, edge cases)
* Performance and security implications visible in the diff

The security-architect (when security markers apply) reviews for:

* Isolation guarantees preserved (no query path missing `organization_id` or `graph_id`)
* Credential handling (no plaintext leakage, no logging of secrets)
* Threat catalogue alignment (does the change introduce any of the threats in Section 6.5?)

The solution-architect (when architectural boundaries are touched) reviews for:

* Layer respect (no Layer 4 code reaching into Layer 1 internals)
* Service boundary contracts (cross-service calls go through documented APIs, not internals)
* OHM-shaped artifacts (capabilities, harnesses, etc. conform to the manifest spec)

The qa-engineer (before story closure) reviews for:

* Tests actually exercise the behaviour the brief describes
* Edge cases covered (empty inputs, boundary values, concurrent access, failure modes)
* Regression risk (does this PR potentially affect features outside its declared scope?)

## Review etiquette

* **Comments are observations or questions, not demands.** A reviewer saying "I'd find this clearer as X" is a suggestion; the author can accept or push back with reasoning.
* **Blocking changes are explicit.** A reviewer who believes a change must not merge as-is uses GitHub's "Request changes" status, not just a comment.
* **Author has the final say within their PR's scope.** Reviewers who think the architecture should be different escalate to an ADR or doc revision, not to a PR comment thread.
* **Reviews happen within 24 working hours** of the PR being marked ready. PRs that age without review are escalated to tech-lead.

## When PRs sit too long

A PR open for more than three working days without merge is reviewed for:

* Is it blocked on a review? — ping the reviewer; escalate if unresponsive
* Is it blocked on a question the author hasn't answered? — close or update
* Has `main` moved significantly under it? — rebase
* Is it the wrong size or scope? — split or close in favour of a fresh PR

Long-lived PRs are an anti-pattern in trunk-based development. They accumulate merge conflicts, lose context, and discourage future small PRs.

## Draft PRs

Draft PRs are encouraged for early feedback or for parking work-in-progress that needs to survive an environment change. Draft PRs do not require reviews and do not appear in review queues. When ready for review, the author marks the PR as ready and requests reviewers.

## Stacked PRs

For changes that genuinely cannot be split into independent PRs (rare), stacked PRs are acceptable: PR B branches off PR A, PR C branches off PR B, etc. Each PR in the stack is reviewed independently. The stack merges bottom-up; each merge triggers a rebase of the PR above.

Stacked PRs are an advanced pattern and should be rare. Prefer splitting work to be genuinely independent where possible.
