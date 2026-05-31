---
confluence_id: "131144"
title: "Configuration Reference"
---

# Configuration Reference

The canonical reference for every environment variable, config flag, and tunable setting the platform exposes. Operators consult this page to understand what they can configure and what each setting does.

## Status

Placeholder — content lands as each service ships in Phases 1–6

This page is maintained by the docs-writer agent: whenever a service introduces or modifies a configuration surface, the corresponding section here is updated as part of the same PR. The Definition of Done requires that any config addition be reflected in this reference.

## Structure

The reference is organised by service. Each service section will list:

* **Variable name** — exact env var or config key
* **Type** — string, integer, duration, URL, boolean, secret
* **Default** — built-in default (and whether it is safe for production)
* **Required** — yes / no / yes-in-production
* **Description** — what it does, in operational terms
* **Constraints** — valid values, ranges, format
* **Security note** — if relevant (e.g. "must be a secret in production")
* **Change requires restart** — yes / no
* **Introduced in** — version it first appeared

## Service-by-service sections (to be populated)

* **auth-service** — issuer, JWT signing key sources, session settings, identity provider configuration, organisation-tenancy settings
* **capability-registry-service** — registry storage, capability validation policies
* **credential-broker-service** — KMS configuration, per-organisation key handling, secret rotation cadence, BYOM provider endpoints
* **knowledge-graph-service** — Neo4j connection, ingestion concurrency, embedding model configuration
* **harness-runtime-service** — orchestration agent model, default budgets, manifest cache settings
* **execution-engine-service** — schedule store, durable job concurrency, retry policy defaults
* **knowledge-retriever-service** — Neo4j read connection, embedding model, cache sizes
* **application-gateway-service** — listen address, rate limits, MCP exposure, CORS policy

## Cross-cutting configuration

* **Logging** — log level, log format, log destination per service
* **Tracing** — OTLP endpoint, sampling rate, exporter selection
* **Metrics** — exporter selection, scrape interval, label cardinality limits
* **Security** — mTLS configuration, TLS certificate sources, header policy
* **Tenancy** — `organization_id` handling, fallback policies in self-hosted single-org deployments

## Configuration philosophy

The platform prefers:

1. **Safe defaults** — out-of-the-box settings work in evaluation; production-grade settings are documented and recommended explicitly
2. **One way to configure** — each setting has one canonical source (environment variable); config files exist only where structured data justifies them
3. **Explicit secrets** — secret values are never read from environment variables in production deployments; the credential-broker handles secret retrieval
4. **Version compatibility** — config that worked in version N continues to work in version N+1 with deprecation warnings; breaking changes go through a major version

## Related references

* **Definition of Done** — config additions are part of the DoD
* **Deployment — Self-hosted** — links to specific operator-relevant settings
* **Deployment — Cloud-hosted** — cloud-mode-specific configuration
* **Service Reference pages** — each service's own page summarises its key configuration
