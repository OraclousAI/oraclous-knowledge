# ADR-025 — SQL Database Connector: Egress and Credential Posture

## Status

| | |
| --- | --- |
| Status | Accepted |
| Date | 2026-06-12 |
| Deciders | solution-architect + security-architect (drafted), Reza (signed off the egress posture) |
| Driving epic | [#294](https://github.com/OraclousAI/oraclous-backend/issues/294) — Legacy-restorations · issue [#307](https://github.com/OraclousAI/oraclous-backend/issues/307) |
| Builds on | [ADR-013](adr-013-fail-closed-authority-placement-at-the-substrate-rebac-seam.md) / §3.5 (fail-closed) · [ADR-021](adr-021-fail-closed-operational-defaults-and-degradation-alert-seam.md) (operational fail-modes) · [ADR-018](adr-018-edge-authentication-trusted-gateway.md) (multi-tenant scope) |
| Re-architects | legacy `knowledge-graph-builder/app/services/{database_connector_service.py, structured_ingest_service.py, schema_mapper.py}` |

## Context

R3.5 dropped the legacy SQL database connector (PostgreSQL/MySQL schema introspection, FK→relationship mapping, structured ingest). Restoring it (#307) reintroduces a capability with a distinct security shape: **the platform makes an outbound connection to an arbitrary, user-supplied external database** — a raw TCP connection to `host:port`, not an HTTP request.

Two facts force a decision:

* **The existing egress/SSRF guards are HTTP(S)-only.** `harness-runtime-service` and `capability-registry-service` each carry a `domain/egress.py` that validates *outbound URLs* (scheme http(s), block link-local/metadata/private hosts). A SQL connection is a TCP socket to a DB port — it **bypasses these guards entirely**. Reaching a SQL DB with no host validation is a textbook SSRF vector (e.g. pointing the "connector" at `169.254.169.254` or an internal `10.x` service).
* **A credential path already exists.** The credential-broker supports a `connection_string` type, resolved by `credential_id` (the capability-registry `PostgreSQLReader` already uses it). There is no need to invent connector-side secret storage.

The open questions: *what host-egress policy governs the DB connection, how are connection credentials supplied, and where does the connector live.*

## Decision

### 1. Egress posture — a per-connection **structural TCP SSRF check** (fail-closed)

A **new TCP-aware egress guard** validates the DB `host:port` before connecting. It mirrors and extends the existing HTTP guards to a raw-socket target:

* **Block** — link-local `169.254.0.0/16` (incl. cloud-metadata `169.254.169.254`), loopback (`127/8`, `::1`), private RFC-1918 (`10/8`, `172.16/12`, `192.168/16`) + IPv6 ULA (`fc00::/7`), blocked hostnames (`localhost`, `metadata*`, suffixes `.internal`/`.local`/`.localhost`/`.cluster.local`), and single-label/bare-container hostnames.
* **Allow** — public hostnames and public IPs.
* **Single-tenant / dev mode** — a flag mirroring the HRS egress `allow_private`: when set, private targets are allowed so a self-hosted user can ingest from a local/internal DB.
* **Resolve-then-check** — resolve the hostname and validate the resolved IP; **fail-closed** on unresolvable/ambiguous. The DNS-rebinding TOCTOU (resolve public-now / connect private-later) is a known limitation; the mitigation is to **pin the resolved IP into the connection** (follow-on if not done in #307).

This is the option Reza selected over the two alternatives below. It is the floor that closes the real SSRF vectors (internal/metadata/private) while remaining **self-serve** — an org can connect to its own public DB without operator involvement.

### 2. Credential posture — `connection_string` by `credential_id`, at request time

Connection credentials use the broker's existing **`connection_string`** type, resolved by **`credential_id`** supplied at ingest-request time (not stored with a connector definition). This mirrors the capability-registry `PostgreSQLReader`. The egress guard validates the host parsed from the resolved DSN. Org+graph scope is server-injected by the existing writer — the caller cannot override it.

### 3. Placement — KGS relational ingest → recipe engine

The connector lands in the **knowledge-graph-service** as a relational ingest source: introspect schema → map rows to entities (keyed by PK) and FKs to relationships → produce a `StructuralRepresentation` → feed the **recipe engine** (the recipe schema already declares `source_type: "relational"` but had no extractor; this wires it). §21-layered: the driver/Cypher access lives in repositories, the egress guard in `domain/`.

### 4. Shared egress logic

The structural-check logic is now needed in three places (HRS, CRS, and the new KGS-TCP guard). It **should be extracted into a shared module** if that is a clean refactor; if extracting across HRS/CRS is too invasive for this slice, mirror the `domain/egress.py` pattern in KGS and record the 3-way duplication as a consolidation follow-up.

## Alternatives considered

* **A. Operator global allow-list.** Only operator-approved DB hosts (env/config) are reachable; no org self-serve. Rejected — highest operational friction; every new data source needs an ops change; defeats self-service ingest.
* **C. Per-org allow-list + structural check.** Each org declares its permitted DB hosts (stored via the broker/auth); ingest validates against the org list *and* the structural check. **Deferred, not rejected** — it is the stronger posture for hostile multi-tenancy, but adds a broker/auth schema change + per-org config, and is premature while the broader authz hardening (ReBAC enforcement, per-org KMS) is still pending (R7-SEC/R8). Revisit when that lands; the structural guard (Option B) is forward-compatible with adding a per-org list on top.

## Consequences

* A **new TCP egress guard** becomes load-bearing for the SQL connector; a GDS-style typed error (not a swallowed 500) on a blocked/unresolvable host.
* The **`relational` recipe source type** goes live (was declared-but-unwired).
* **DNS-rebinding TOCTOU** is a documented residual; resolved-IP pinning is the mitigation (in #307 if feasible, else a follow-on).
* A **3rd egress-guard instance** exists; a shared-module consolidation is the recommended follow-up.
* The decision is **forward-compatible** with Option C (a per-org allow-list layered on the structural floor) when hostile multi-tenancy is in scope.

## See also

* [ADR-013](adr-013-fail-closed-authority-placement-at-the-substrate-rebac-seam.md) / §3.5 (fail-closed) · [ADR-021](adr-021-fail-closed-operational-defaults-and-degradation-alert-seam.md) (operational egress/degradation) · [ADR-018](adr-018-edge-authentication-trusted-gateway.md) (multi-tenant scope)
* Existing guards: `harness-runtime-service` / `capability-registry-service` `domain/egress.py`
* Legacy source: `legacy-reference/old-backend/knowledge-graph-builder/app/services/{database_connector_service.py, structured_ingest_service.py, schema_mapper.py}`
* Issues [#307](https://github.com/OraclousAI/oraclous-backend/issues/307) · [#294](https://github.com/OraclousAI/oraclous-backend/issues/294)
