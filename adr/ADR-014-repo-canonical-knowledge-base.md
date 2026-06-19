---
confluence_id: "4685826"
title: "ADR-014 — Repo-canonical knowledge base; Confluence as mirror; GitHub Issues as master board"
---

# ADR-014 — Repo-canonical knowledge base; Confluence as mirror; GitHub Issues as master board

This page is a **mirror** of `adr/ADR-014-repo-canonical-knowledge-base.md` in [oraclous-knowledge](https://github.com/OraclousAI/oraclous-knowledge). The repo is canonical; edits made here may be overwritten by the next mirror sync.

## Status

| Field | Value |
| --- | --- |
| Status | <custom data-type="status" data-id="id-0">Accepted</custom> |
| Date | 31 May 2026 |
| Proposed by | solution-architect |
| Approved by | tech-lead (Reza Jahankohan) — PR #1 merged commit `76dd833b`, 2026-05-31 |
| Supersedes | [ADR-011 — External Jira and Confluence (Not Local Wiki)](https://oraclous.atlassian.net/wiki/spaces/OP/pages/393443) — in full |
| Superseded by | None |
| Driving artifact | ORAA-7 — Migrate Confluence OP → oraclous-knowledge (canonical); ADR-014 authored under ORAA-9, migration PR under ORAA-8 |

## Context

[ADR-011](https://oraclous.atlassian.net/wiki/spaces/OP/pages/393443) made two founding tooling decisions for the agent team: external **Atlassian Confluence** as the canonical documentation system, and external **Atlassian Jira** (project `ORA`) as the canonical ticketing system. Both were chosen to give the founding team functioning infrastructure on day one without absorbing setup cost into the platform's own bootstrap. Building a local wiki was explicitly rejected (ADR-011 alternative A) on the grounds that it would force every agent to learn a custom Markdown convention, push ticketing onto a structure-poor backend, and tie documentation evolution to repo changes.

Three things have changed since that decision, and together they invert its conclusion for the documentation axis:

1. **The agents are now git-native operators, not Confluence-native ones.** The team works through repository sessions whose primary medium is files, branches, diffs, and PRs. Confluence's rich stored format — the very thing ADR-011 valued — is now an _impedance_: it is not diffable, not reviewable as a unit of change, not blame-able, and not reachable by CI. Documentation drift is invisible until someone reads the page; there is no mechanical gate that can fail a build when a doc contradicts code.
2. **The off-the-shelf-tooling argument has flipped.** ADR-011 rejected a local knowledge base because standing one up would cost founding budget. A GitHub repository (`oraclous-knowledge`) costs effectively nothing to stand up, inherits the review, history, access-control, and automation the team _already runs_ for code, and requires no new convention beyond Markdown — which every agent already authors fluently. The "custom rendering / custom convention" cost ADR-011 feared does not materialise with a plain Markdown repo plus GitHub's native rendering.
3. **Ticketing has already moved.** This decision is being recorded as a GitHub issue (ORAA-7 / ORAA-9), not in Jira. The agent team's master board, assignment model, and run audit trail are GitHub-native today: work is tracked as GitHub Issues + PRs, agents pick up issues by assignee/label, and the `gh` CLI drives the board. Jira `ORA` is no longer the system of record for task tracking; continuing to name it canonical in an accepted ADR is a documented-reality drift.

ADR-011 anticipated exactly this moment. Its implementation notes state: _"If the team eventually migrates away from Atlassian, the migration is an explicit ADR-level decision with an explicit plan, not a silent transition. The structured artifacts … are deliberately authored to survive a migration: their content is portable Markdown / YAML / HTML."_ This ADR is that explicit decision. The portability ADR-011 designed for is what makes the migration cheap: the Confluence corpus is being lifted page-for-page into the repo, not rewritten.

The decision to make is therefore not _whether_ the artifacts are portable — ADR-011 already secured that — but _where the single source of truth now lives_, and _what Confluence and Jira become once it moves_.

## Decision

The Oraclous knowledge base is **repo-canonical**. Specifically:

### 1. `oraclous-knowledge` (GitHub) is the canonical knowledge base

The GitHub repository `git@github.com:OraclousAI/oraclous-knowledge.git` is the single source of truth for all internal engineering documentation: architecture, ADRs, service references, operations, compliance, frontend docs, releases, engineering flows, interface contracts, and persona/skill pages. Content is plain Markdown (plus YAML/HTML where a structured artifact requires it), in a folder tree that mirrors the former Confluence numbered hierarchy 1:1 (see ORAA-8 folder mapping). Where this repo and any other artifact disagree, **the repo wins**.

### 2. Confluence OP is a one-way downstream mirror

The Confluence space `OP` is demoted from canonical to **read-only mirror**. It is a _derivative_ of the repo, regenerated from repo content; it is never edited directly, and edits made in Confluence are not authoritative and may be overwritten by the next sync. The sync is **strictly one-way**: repo → Confluence, never Confluence → repo. A `_mirror/confluence-map.yaml` (`pageId ↔ repo path`) is the durable mapping that drives the sync. Confluence remains valuable as a browse/read surface for humans and externally-granted collaborators who should not be given repo access.

### 3. GitHub Issues is the master board for task tracking

GitHub Issues + PRs are the canonical system of record for issues, assignments, dependencies, approvals, and the run audit trail. Agents pick up issues by assignee/label and the `gh` CLI drives the board. It replaces Jira `ORA` as the master board. Cross-references in documentation use GitHub issue links (`OraclousAI/<repo>#<number>`).

### 4. docs-writer is the sole writer; everyone else is read-only + delegate

`oraclous-knowledge` is **sole-writer**: the **docs-writer** agent is the only agent that commits to it. All other agents treat the repo as **read-only**. When any agent needs a knowledge-base change (a new ADR, an architecture revision, a service-reference correction), it does not edit the repo; it **delegates via a child issue** to docs-writer, supplying the exact content and target path. The author of record for the _decision_ remains the originating role (e.g. solution-architect authors ADR text); docs-writer is the author of record for the _commit_.

This ADR is itself the first instance of the pattern: solution-architect authored the ADR-014 text; docs-writer lands the file in the repo.

### 5. The Confluence mirror process

After a PR merges to the canonical repo, the mirror is updated repo → Confluence using `confluence-map.yaml` to resolve each changed file to its target page. The mirror update is a docs-writer / CI responsibility, not a manual cross-edit. Until the mirror automation exists, Confluence is simply stale-but-labelled (the repo README and each mirrored page state that the repo is canonical and Confluence is the mirror); a labelled stale mirror is acceptable, a silently-authoritative-looking stale mirror is not.

## Alternatives considered

### A. Keep ADR-011 as-is (Confluence canonical, Jira canonical)

Status quo. **Rejected.** It is already counter-factual: ticketing runs as GitHub Issues + PRs today, and the agent team operates git-native. Leaving an accepted ADR naming Jira/Confluence canonical institutionalises drift between the recorded decision and the lived workflow — precisely the silent-disagreement failure the architecture-coherence discipline exists to prevent.

### B. Repo-canonical, but drop Confluence entirely

Delete the Confluence space once the repo exists. **Rejected for now.** Confluence still carries value as a zero-friction read surface for externally-granted collaborators (investors, partners, prospective hires) who should not receive repo access — a benefit ADR-011 named and this ADR preserves. Keeping it as a clearly-labelled mirror retains that benefit at low cost; deleting it is a separable future decision if the read-surface value disappears.

### C. Two-way sync between repo and Confluence

Let edits flow in both directions. **Rejected.** Bidirectional sync re-creates the two-sources-of-truth problem this ADR exists to eliminate: merge conflicts between a diffable system and a non-diffable one have no clean resolution, and "which side wins" becomes a per-edit judgement call. One-way (repo → Confluence) keeps the canonical/derivative relationship unambiguous.

### D. Allow every agent to write to the repo (no sole-writer)

Drop the docs-writer bottleneck; let each role commit its own docs. **Rejected.** A multi-writer knowledge base re-introduces uncoordinated drift, inconsistent structure, and the loss of a single reviewable choke point — and it muddies CODEOWNERS/branch-protection enforcement (ORAA-10). A single writer with a delegate-by-child-issue intake keeps structure coherent and makes the enforcement mechanism (one owner, one protected branch) simple. The cost — docs-writer is a serialization point — is accepted and bounded by the fact that authoring (the slow part) is parallel across roles; only the commit is serialized.

## Consequences

### Positive

* **Documentation gains everything code already has:** PRs, review, diffs, blame, branch protection, and CI hooks that can mechanically gate doc/code coherence. A doc change is now a reviewable unit.
* **One source of truth, unambiguously.** The repo wins; Confluence is explicitly derivative. No more "which copy is right" ambiguity.
* **No new tooling debt.** Markdown + GitHub reuses the team's existing competencies and infrastructure; the "custom convention / custom rendering" cost ADR-011 feared does not arise.
* **Governance is enforceable in-band.** Sole-writer + CODEOWNERS + branch protection (ORAA-10) makes "who may change the knowledge base" a mechanically enforced property, not a convention.
* **The read surface is preserved.** External collaborators keep a no-repo-access Confluence view via the one-way mirror.
* **Recorded reality matches lived reality.** GitHub-Issues-as-master-board is what the team already does; this ADR stops the accepted-ADR-vs-practice drift.

### Negative

* **Confluence's rich structuring is lost on the canonical side.** Status macros, info panels, and hierarchical page widgets do not survive as first-class Markdown. Mitigated: structured artifacts (OHM spec, Governance Taxonomy, Threat Catalogue) carry their structure as YAML/HTML, exactly as ADR-011 designed for portability.
* **A mirror process must be built and maintained.** Until it exists, Confluence is stale (labelled, per §5). The sync is real ongoing work owned by docs-writer/devops; it is a standing cost, not a one-time migration cost.
* **The Atlassian MCP write tooling becomes read-only in practice.** Agents that authored via `updateConfluencePage` now author via repo PRs (through docs-writer). Confluence MCP writes are reserved for the mirror process.
* **docs-writer is a serialization point** for knowledge-base commits. Accepted (alternative D); authoring stays parallel, only commits serialize.
* **Cross-references churn.** Existing `oraclous.atlassian.net/wiki/...` and Jira `ORA-…` links across the corpus point at the now-derivative systems. They remain resolvable (mirror + Jira read-only) but new references should target the repo and GitHub Issues; a follow-up pass to re-point high-traffic links may be warranted.
* **External read-access now depends on the mirror being current.** A collaborator reading only Confluence sees the repo state as of the last sync, not HEAD. The labelling in §5 makes this explicit rather than misleading.

## Implementation notes

* The migration itself (110 Confluence pages → repo, `confluence-map.yaml`, README) is ORAA-8; this ADR file (`adr/ADR-014-repo-canonical-knowledge-base.md`) landed in the same PR (branch `kb/migrate-confluence-op`), committed by docs-writer per the sole-writer rule this ADR establishes.
* Governance enforcement — CODEOWNERS + branch protection making docs-writer the sole writer mechanically — is ORAA-10.
* The ADR-011 Confluence page (`393443`) has been marked **Superseded** with a banner pointing at the repo-canonical copy. These Confluence edits are the _last_ authoritative Confluence writes for these pages — thereafter they are mirror-only.
* Scope: this ADR governs **internal engineering documentation and task tracking**. Customer-facing/product documentation is out of scope (as it was in ADR-011).

## References

* [ADR-011 — External Jira and Confluence (Not Local Wiki)](https://oraclous.atlassian.net/wiki/spaces/OP/pages/393443) — superseded in full by this ADR; its portability foresight is what makes this migration cheap.
* [ADR-010 — Test-Driven Development with Test-Author Agent](https://oraclous.atlassian.net/wiki/spaces/OP/pages/557078) — the workflow discipline the new CI-gated docs hooks extend to documentation.
* ORAA-7 — parent: migrate Confluence OP → oraclous-knowledge, docs-writer sole writer, ADR-014 supersede ADR-011, governance.
* ORAA-8 — the migration PR this ADR file shipped in.
* ORAA-9 — this ADR's authoring issue.
* ORAA-10 — CODEOWNERS + branch-protection governance enforcement.

## Revision history

| Date | Change |
| --- | --- |
| 31 May 2026 | Initial draft (Proposed) authored by solution-architect under ORAA-9. Supersedes ADR-011 in full. Pending Reza approval of the migration PR (ORAA-8). |
| 31 May 2026 | Status → **Accepted**. PR #1 merged (commit `76dd833b`). Confluence page created as mirror. \[agent:docs-writer\] |
