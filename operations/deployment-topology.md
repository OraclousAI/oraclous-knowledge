---
confluence_id: "720961"
title: "Deployment Topology"
---

# Deployment Topology

This page describes how the eight services in the target architecture are deployed in both self-hosted and cloud-hosted modes. The topology is the same in both modes; only the operator and the compliance posture differ (ADR-008).

## Service stack

The platform deploys as eight independent services backed by three infrastructure components:

**Services**

* `auth-service` (8000)
* `capability-registry-service` (8001)
* `credential-broker-service` (8002)
* `knowledge-graph-service` (8003)
* `harness-runtime-service` (8004)
* `execution-engine-service` (8005)
* `knowledge-retriever-service` (8006)
* `application-gateway-service` (8007)

**Infrastructure**

* **Neo4j** — knowledge graph storage, ReBAC graph, provenance
* **Postgres** — relational data (users, credentials, chat history, capability descriptors, durable execution state, metering)
* **Redis** — caches, job queues, schedule fire times, session state

**External (cloud mode only)**

* KMS (key management service) — per-organisation encryption keys with operator separation
* Object storage — large file ingestion sources, exportable artifacts

## Deployment unit

Each service ships as a container image. Image tags follow the platform's semver (e.g., `oraclous/harness-runtime:v0.5.0`). The full stack is a versioned set: deploying `v0.5.0` deploys all eight services at `v0.5.0`. Mismatched service versions are not supported.

## Local development

Local development uses Docker Compose with all eight services plus Neo4j, Postgres, and Redis. The compose file lives in `OraclousAI/oraclous-backend` and bootstraps a fully working stack with seeded default manifests.

A single `make dev` brings the stack up; `make test` runs the full test suite against it. Frontend development runs separately with Vite proxying to the gateway.

## Staging environment

Staging mirrors production in topology but at smaller scale. Every release passes through staging for at least 24 hours of soak before production deployment (per the Release Process). Adversarial security tests run against staging on every release.

## Production environments

**Self-hosted production** is the customer's responsibility. The platform provides Kubernetes manifests, Helm charts, and Docker Compose configurations for common deployment shapes. Customers operate their own Neo4j, Postgres, and Redis (or use managed alternatives).

**Cloud-hosted production** is operated by Oraclous-the-company. Each organisation is logically isolated through the `organization_id` scoping (ADR-006) on a shared Neo4j cluster, Postgres database, and Redis instance. Per-organisation encryption keys live in KMS with operator separation.

## Scaling

Each service scales horizontally and independently:

* `application-gateway-service` and `harness-runtime-service` scale with synchronous request load
* `execution-engine-service` scales with durable job volume and schedule density
* `knowledge-retriever-service` scales with retrieval volume (separate from the builder)
* `knowledge-graph-service` scales with ingestion volume
* `auth-service`, `credential-broker-service`, `capability-registry-service` typically need less aggressive scaling — they are foundational but not high-throughput

The split between build and retrieve (Phase 3) is what makes the retrieval service scale independently of ingestion load. Section 8's "graph retriever decision" justifies this.

## Database connections

Services connect to Neo4j and Postgres with role-based credentials:

* Build-side services (`knowledge-graph-service`) get write-capable Neo4j roles
* Read-side services (`knowledge-retriever-service`) get read-only Neo4j roles
* Other services get their own per-service Postgres roles with least-privilege grants

This is enforced at the database server level, not just at the application level. A bug in a read-side service cannot accidentally write to the graph because the database refuses the write.

## Networking

* Inter-service traffic is encrypted (mTLS in cloud mode, configurable in self-hosted)
* The gateway is the only service exposed publicly; all others are internal
* The gateway enforces authentication on every external request
* Internal services trust each other within the deployment boundary but still validate request signatures for sensitive operations

## Observability

Every service emits structured logs, traces, and metrics. The Observability page documents the specific tools and conventions.

## Disaster recovery

* Neo4j: continuous backups with point-in-time recovery for the past 30 days
* Postgres: continuous backups with point-in-time recovery for the past 30 days
* Redis: ephemeral by design; data in Redis is recoverable from Neo4j or Postgres
* KMS: independent backup of per-organisation keys with multi-region replication (cloud mode)

Recovery target: RPO 1 hour, RTO 4 hours for the substrate; gateway and runtime services are stateless and recover in minutes.
