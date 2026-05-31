# Deployment Topology

The platform deploys as eight independent services backed by three infrastructure components. The topology is the same in both self-hosted and cloud-hosted modes.

## Service stack

**Services:**
- `auth-service` (8000)
- `capability-registry-service` (8001)
- `credential-broker-service` (8002)
- `knowledge-graph-service` (8003)
- `harness-runtime-service` (8004)
- `execution-engine-service` (8005)
- `knowledge-retriever-service` (8006)
- `application-gateway-service` (8007)

**Infrastructure:**
- **Neo4j** — knowledge graph storage, ReBAC graph, provenance
- **Postgres** — relational data (users, credentials, chat history, capability descriptors, durable execution state, metering)
- **Redis** — caches, job queues, schedule fire times, session state

## Local development

Docker Compose with all eight services plus Neo4j, Postgres, and Redis. `make dev` brings the stack up; `make test` runs the full test suite.

## Disaster recovery

- Neo4j + Postgres: continuous backups with point-in-time recovery for 30 days
- Redis: ephemeral by design; data recoverable from Neo4j or Postgres
- RPO 1 hour, RTO 4 hours for the substrate
