# Section 8 — Consolidation and Migration Plan

## Current state of the codebase

Four services exist: `auth-service` (production-grade), `credential-broker-service` (production-grade), `oraclous-core-service` (mixed), `knowledge-graph-builder` (sprawling — production-grade content, wrong service boundaries).

## Target architecture mapped to services

**Layer 1 — Substrate:**
- `auth-service` (port 8000)
- `credential-broker-service` (port 8002)
- `knowledge-graph-service` (port 8003) [renamed]
- `knowledge-retriever-service` (port 8006) [NEW]

**Layer 2 — Capability Registry:**
- `capability-registry-service` (port 8001) [evolved from oraclous-core-service]

**Layer 3 — Harness Runtime + Execution Engine:**
- `harness-runtime-service` (port 8004) [NEW, lifted from knowledge-graph-builder]
- `execution-engine-service` (port 8005) [NEW]

**Layer 4 — Application Gateway:**
- `application-gateway-service` (port 8007) [NEW]

## Migration phasing

- **Phase 0 (R0)** — Documentation and stabilisation (Weeks 1-2)
- **Phase 0.5 (R0.5)** — Organisation tenancy and metering substrate (Weeks 3-4)
- **Phase 1 (R1)** — Auth and credential extensions (Weeks 5-6)
- **Phase 2 (R2)** — Capability registry consolidation (Weeks 7-10)
- **Phase 3 (R3)** — Knowledge graph decomposition (Weeks 11-16)
- **Phase 4 (R4)** — Harness runtime extraction (Weeks 17-20)
- **Phase 5 (R5)** — Execution engine and runtime completion (Weeks 21-24)
- **Phase 6 (R6)** — Application Gateway extraction (Weeks 25-28)
- **Phase 7 (R7)** — Compiler harness and seed manifests (Weeks 29-32)
- **Phase 8 (R8)** — Security hardening pass (Weeks 33-36)
