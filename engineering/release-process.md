---
confluence_id: "426058"
title: "Release Process"
---

# Release Process

The platform's release model is **release-based, milestone-aligned with architecture phases**. Each migration phase from Section 8 corresponds to a release; patch releases handle bug fixes between phase boundaries.

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
