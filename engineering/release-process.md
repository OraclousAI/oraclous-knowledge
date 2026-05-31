# Release Process

The platform's release model is **release-based, milestone-aligned with architecture phases**. Each migration phase from Section 8 corresponds to a release.

## Versioning

`MAJOR.MINOR.PATCH`

- **MAJOR** — incompatible changes to OHM format, substrate schema, or public API contracts
- **MINOR** — new functionality in a backwards-compatible way (each completed phase)
- **PATCH** — backwards-compatible bug fixes

Pre-1.0 releases are explicitly unstable. The platform reaches `v1.0.0` when Phase 8 completes.

## Release procedure (minor releases)

1. Confirm Phase Definition of Done — all stories closed, all sign-off gates cleared
2. Tag the release commit: `git tag -a v0.N.0 -m "Phase N: <name>"`
3. Write the release notes (Confluence)
4. Update the architecture's Migration Phasing page
5. Push the tag — CI builds and publishes container images
6. Deploy to staging — run security test pass
7. Deploy to production — after at least 24 hours staging soak with no regressions

## Compatibility commitments

Between **minor** releases: OHM v1 documents remain valid. Public REST API contracts are not broken. Substrate schemas evolve additively.
