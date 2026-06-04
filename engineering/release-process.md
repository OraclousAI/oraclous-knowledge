---
confluence_id: "426058"
title: "Release Process"
---

# Release Process

The platform's release model is **release-based, milestone-aligned with architecture phases**. Each migration phase from Section 8 corresponds to a release; patch releases handle bug fixes between phase boundaries.

> **Superseded roadmap (R3.5).** The old **R4–R8** roadmap and its **gateway-from-R5 vertical slices** plan are **discarded**. R2/R3 shipped **hollow** (stub endpoints, `raise NotImplementedError`, a `GraphNodeService` stub class defined inside a route file, ~6,300 LOC of real logic left dead and undeleted in `oraclous-backend/oraclous-core-service/`, and auth that dropped human/email/OAuth/org management). **R3.5** replaces R4–R8: it rebuilds every service **real, end-to-end, per service**, in a hard-sequenced cadence with a per-service human sign-off gate (see [R3.5 release cadence](#r35-release-cadence-per-service-sequential-delivery) below). The canonical authority for R3.5 is **ORAA-4 operating-contract** (§21–§23); when this page and ORAA-4 diverge, ORAA-4 wins.

## Versioning

Releases follow semantic versioning: `MAJOR.MINOR.PATCH`.

* **MAJOR** — incompatible changes to the OHM format, the substrate schema, or the public API contracts. Major version bumps require an ADR superseding the affected commitments.
* **MINOR** — new functionality added in a backwards-compatible way. Each completed migration phase bumps the minor version (Phase 0.5 ships as `v0.1.0`, Phase 1 as `v0.2.0`, etc.).
* **PATCH** — backwards-compatible bug fixes. Multiple patches may ship between minor versions.

Pre-1.0 releases are explicitly unstable; the platform is `v0.x.y` through Phase 8 and reaches `v1.0.0` when the architecture as described in Sections 1-7 is fully implemented and security-hardened (end of Phase 8).

## Release cadence

* **Phase releases (minor bumps)** — every 4–8 weeks per Section 8's timeline. Each shipping when its phase Definition of Done clears.
* **Patch releases** — as needed. A patch release is triggered by either (a) a production bug that warrants a fix between phases, or (b) a security issue requiring immediate response.
* **No fixed time-based cadence.** Releases happen when the work is done, not when the calendar says.

## Release procedure

For minor releases:

1. **Confirm Phase Definition of Done.** All stories in the phase's epic closed; all sign-off gates cleared; security test pass complete.
2. **Tag the release commit.** Annotated tag: `git tag -a v0.N.0 -m "Phase N: <name>"`. The tag points at the final phase-completion commit on `main`.
3. **Write the release notes.** Confluence page under the Release Notes section of the Meta hub, naming what shipped, what migrated, what's known-broken, and what's deferred to subsequent phases.
4. **Update the architecture's Migration Phasing page** to mark the phase as Shipped with the release tag.
5. **Push the tag** to GitHub. CI builds and publishes container images tagged with the version.
6. **Deploy to staging.** The full service stack at the new version. Run the security test pass against staging.
7. **Deploy to production.** After at least 24 hours of staging soak with no regressions.

For patch releases:

1. **Branch from the most recent minor tag.** Cherry-pick the fix commits onto the patch branch.
2. **Tag the patch.** `git tag -a v0.N.M -m "Patch: <summary>"`.
3. **Write a brief release notes entry** in the Meta hub.
4. **Push, build, deploy** through the same staging → production pipeline.

## Hotfixes

Hotfixes are patches that bypass the normal staging soak because the issue is severe (active production breakage, active security issue). Hotfix procedure:

1. tech-lead authorises the hotfix explicitly (Slack thread, Jira hotfix ticket)
2. Fix branch is `hotfix/ORA-NNN/short-description`, branched from the latest production tag
3. Tests in the test PR cover the regression specifically
4. Staging soak is reduced to 1 hour (or skipped entirely with tech-lead authorisation)
5. Post-deployment: a retrospective documents what failed and adjusts process to prevent recurrence

Hotfixes are a last resort. Frequent hotfixes signal a problem with the staging environment, the test coverage, or the release gating.

## Release-seam retrospective

The hotfix step above mandates a post-deployment retrospective whenever a hotfix ships. That same discipline applies, generalised, at **every release seam** — not only after a hotfix.

At each release gate the CTO runs a retrospective on the release just completed. The retrospective must produce **concrete deltas**, not just discussion:

* edits to the operating contract (ORAA-4), the agent bundles, or the knowledge base, **or**
* a logged "won't fix" for each candidate change that was considered and deliberately declined.

The release-gate issue **cannot close** until every surfaced delta has either been applied or explicitly waived. A retrospective that ends with "we noticed some friction" and no recorded action is not complete.

This generalises the hotfix-retrospective hook: where the hotfix retro asks "what failed, and how do we stop it recurring?" after an emergency, the release-seam retrospective asks the same question routinely, at the planned boundary between releases, so process drift is corrected at the seam rather than accumulating until it forces a hotfix.

## Goal status hygiene and sequencing at the release seam

Releases are **strictly sequenced**: only the **highest unfinished release is workable** at any time. The team does not open the next goal while the current one is still in flight, and a delivered goal must never be left lingering in `active`.

Before the next goal may open, the CTO performs status hygiene on the goal just delivered — at the release seam, alongside the retrospective above:

1. **Mark the completed goal `achieved`.** A goal that has shipped is not `active`; leaving it `active` makes the board lie about what is in progress and blurs which release is the workable one.
2. **Mark ALL of that goal's projects `completed`.** A goal cannot be cleanly `achieved` while its child projects still read as open work; close them out in the same pass.

A delivered goal that stays `active`, or that carries projects still marked open, is a hygiene defect to fix before the next goal opens. This status pass is **tied to the release-seam retrospective**: the retrospective closes the engineering loop on the release, and the goal/project status pass closes the planning loop — both happen at the same seam, before the next release becomes workable.

## R3.5 release cadence: per-service sequential delivery

R3.5 supersedes the discarded R4–R8 roadmap (see the note at the top of this page). It is **not** a single milestone release; it is a **per-service cadence**. Each service is rebuilt **real and end-to-end**, one at a time, and a service's Project does not open until the prior dependent service has cleared its human sign-off gate. The spec is pinned to legacy `develop` at commit `84152635de05c105765cfe6b631bb5ba81f2f4aa` (TASK-237; [ADR-022](../adr/) recipe/primitive/unified-graph ingestion model). Never write to `legacy-reference/`; read the spec via `git show develop:<path>`.

### Graph-first service order

Services ship in a hard sequence, graph-first, because each depends on the substrate the prior one establishes:

1. **knowledge-graph-service** (ingest)
2. **knowledge-retriever-service** (read)
3. **identity/org service** (NEW: users + email + OAuth Google/GitHub/Notion + orgs/members/roles/invites; orgs **leave** the graph service)
4. **credential-broker-service**
5. **capability-registry + tools + connectors** (port from `oraclous-core-service`, then salvage-then-delete it — human-gated)
6. **application-gateway**

### Hard per-service human sign-off gate

The cadence is **strictly sequential**: only one service is in flight at a time, and the next dependent service's **Project does not open** until the current service is fully done. "Done" here is the hardened per-service Definition of Done (ORAA-4 §22) — all eight gates, of which "merged PR + green stub-tests" satisfies **none** of gates 2–6. The terminal gate is **human**:

* The service's issue carries the **`needs-human`** flag until Reza personally tests it and signs off. **No service is done while `needs-human` is set.**
* Reza runs the service's end-to-end smoke (`services/<svc>/tests/smoke/smoke.sh`, which also runs in CI as the docker-required `r3_5_gate` job, modelled on the r2-gate) against real substrate, and signs off before the **next dependent service's Project opens**.
* This is a per-service application of [§8 sequencing](#goal-status-hygiene-and-sequencing-at-the-release-seam): the prior service's work must be `achieved`/`completed` and human-accepted before the next becomes workable.

### Reaching services before the gateway exists

The **application-gateway is the last service** (step 6). Until it exists, services are reached **directly by host `IP:port`** — this is legacy parity (the legacy app had no gateway). API-authz and gateway-routed access concerns belong to the gateway service, not to the earlier services; earlier services expose their endpoints directly.

### Per-service scope (anti-micro-ticket)

Per ORAA-4 §23, **one service = one deliverable**, decomposed into **at most six coarse vertical slices**. Each slice cuts all layers (route → service → repository), ends in a passing smoke, and is a single `[tests]` + `[impl]` pair. No ticket per file, import, or endpoint-shell; no giant interlocked task graphs. The canonical service architecture each service conforms to (ORAA-4 §21) and its enforcement are described in [service-architecture-standard.md](service-architecture-standard.md).

### Hollowness audit and salvage-then-delete

`tools/audit/hollowness_audit.py` produces a true-completion map and **re-opens** the hollow R2/R3 "done" stories under R3.5. `oraclous-core-service` is marked `port_source: true`, `deletable: false`: it **stays** until its logic is ported and tested into capability-registry (step 5). Its deletion is **destructive** and requires human sign-off ([§15](../engineering/index.md)).

## Compatibility commitments

Between **minor** releases:

* OHM v1 documents remain valid and executable. Schema changes that affect existing documents trigger a minor format bump (`ohm: 2`), with v1 documents still accepted via the registry's version pinning.
* Public REST API contracts are not broken. New endpoints are added; existing endpoints are not removed without a deprecation cycle.
* Substrate schemas evolve additively. Columns are added; existing columns are not removed without a migration window during which both old and new are supported.

Between **major** releases:

* Breaking changes are documented in the major release notes with migration guides
* A major version supports the previous major's customers for at least 12 months as a deprecation window
* ADRs that supersede prior decisions are mandatory for any breaking change

## Rollback

Every release is rollback-able. The procedure:

1. tech-lead authorises the rollback
2. devops-implementer redeploys the previous version's container images to production
3. Database migrations that the rolled-forward version applied need explicit reverse migration scripts
4. The rollback is documented in the Meta hub's Incident Log with a follow-up plan

Migrations that are not reversible (data deletions, irreversible schema changes) require explicit pre-release tech-lead approval and a documented forward-only plan. These are exceptional.

## Deprecation cycle

When functionality must be removed:

1. **Mark as deprecated** in code, docs, and release notes. The functionality continues to work.
2. **Communicate** the deprecation to customers via release notes and (for cloud customers) in-product notifications.
3. **Wait** at least 90 days (for minor-version deprecations) or 12 months (for major-version deprecations).
4. **Remove** in a subsequent release. The removal release notes call out what's gone.

No silent removals. No "we removed this in v0.5 with no warning."
