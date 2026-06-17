# ADR-030 — Realize the Postgres RLS Backstop (per-service policies + an async GUC-binding seam + a non-bypassing runtime role)

## Status

| | |
| --- | --- |
| Status | Accepted — **Realized 2026-06-17** (epic [#353](https://github.com/OraclousAI/oraclous-backend/issues/353) closed) |
| Date | 2026-06-17 |
| Deciders | solution-architect (drafted), Reza (greenlit the realize epic, 2026-06-17) |
| Driving epic | Realise RLS backstop ([`oraclous-backend#353`](https://github.com/OraclousAI/oraclous-backend/issues/353)) · grade-A remediation WP-5 Option A |
| Builds on | [ADR-006](adr-006-organisation-as-outermost-tenancy-unit.md) (org as tenancy), [ADR-012](adr-012-substrate-tenancy-enforcement-seam-and-rls-backstop-preconditions.md) (the seam + RLS preconditions — this ADR *realizes* its §2), [ADR-013](adr-013-fail-closed-authority-placement-at-the-substrate-rebac-seam.md) |

> **✅ Realized 2026-06-17 (epic #353 closed).** All 7 backend services now connect at runtime as the NOSUPERUSER/NOBYPASSRLS `oraclous_app` role with `ENABLE`+`FORCE ROW LEVEL SECURITY` + an org-isolation policy on every org-scoped table — **27 forced-RLS tables**, proven by data-layer isolation tests + live smoke. PRs #367 (credential-broker + foundation), #368 (auth), #369 (shared `oraclous_substrate` GUC/role seam: `build_rls_engine`/`org_scope`/`install_org_guc_guard`/`provision_app_role`), #370 (knowledge-graph), #371+#372 (execution-engine + request-path fix), #373 (capability-registry + harness-runtime), #374+#375 (application-gateway + dep fix). Cross-org *producers* (auth credential-store, engine reaper/Beat, gateway `get_by_prefix`/`get_by_id`) run on a separate owner engine (the §3 carve); every other request-path op binds the org via `org_scope`. Two CI-blind bug classes surfaced (request-path empty-GUC fail-close; missing per-service pyproject dep masked by the workspace venv) — now covered by real-path isolation tests + the `check_service_dep_imports` / `check_rls_request_binding` guardrails. **Prod must override the dev `oraclous_app` password** with a managed credential.

## Context

ADR-012 §2 committed to Postgres RLS as the defense-in-depth backstop behind app-layer org-scoping, and specified the preconditions (`NOSUPERUSER`/`NOBYPASSRLS` role; transaction-local GUC). The grade-A audit (WP-5) found, and ADR-012's as-built note now records, that **RLS is not realized**: no migration enables it, the runtime connects as a superuser, and app-layer `WHERE organisation_id = …` is the only live control. This ADR is the realization design. It is deliberately adversarial about *why the obvious plan does not work as written*, because three facts in the current code break the naive "just call `apply()` and route through `scoped_pg_connection`" approach:

1. **`scoped_pg_connection` is sync `psycopg`; every service is async SQLAlchemy (`asyncpg`).** `packages/substrate/access.py` `scoped_pg_connection` / `bind_organisation_guc` open a **synchronous** `psycopg` connection and `SELECT set_config(..., true)`. All 8 services create their own `create_async_engine` (asyncpg) sessions in `repositories/` and **none** call the substrate seam in the request path. You cannot drop a sync psycopg context manager into an async SQLAlchemy repository. **Realizing RLS therefore requires an async GUC-binding mechanism, not the existing sync seam.**
2. **The runtime role is the `oraclous` superuser** (`deploy/docker-compose.yml`: `postgresql+asyncpg://oraclous:oraclous@postgres`). A superuser **bypasses RLS unconditionally** (ADR-012's own precondition). Policies would be inert until the runtime connects as a dedicated `NOSUPERUSER NOBYPASSRLS` role. (The test suite already provisions exactly such a role — `oraclous_app` in `tests/organization_isolation/conftest.py` — which is how `test_query_path_org_enforcement.py` proves RLS works; the gap is purely that the *deployed* services don't use it.)
3. **`substrate.schema.postgres.apply()` is KGS-specific and table-creating, not a generic RLS applier.** It hardcodes `TENANT_TABLES = (knowledge_graphs, ingestion_jobs, connectors, blob_cas)` and `CREATE TABLE IF NOT EXISTS` with its own column DDL. The ~28 org-scoped tables across the other six Postgres services (auth, credential-broker, capability-registry, harness-runtime, execution-engine, application-gateway) are not covered, and they already exist via each service's own migrations — they need RLS *added to existing tables*, not re-created.

## Decision

Realize the RLS backstop in **four mechanisms**, rolled out **service-by-service** (phased), each phase proven by a data-layer isolation test.

### 1. A generic, idempotent per-table RLS applier (substrate)

Add `oraclous_substrate.schema.postgres.enable_rls_on(conn, table, *, org_column="organisation_id")` that, on an **existing** table, issues (idempotently):

```sql
ALTER TABLE public."{table}" ENABLE ROW LEVEL SECURITY;
ALTER TABLE public."{table}" FORCE ROW LEVEL SECURITY;   -- bites the table owner too
DROP POLICY IF EXISTS "{table}_org_isolation" ON public."{table}";
CREATE POLICY "{table}_org_isolation" ON public."{table}"
  USING      ({org_column} = NULLIF(current_setting('app.current_organisation_id', true), '')::uuid)
  WITH CHECK ({org_column} = NULLIF(current_setting('app.current_organisation_id', true), '')::uuid);
```

The **`WITH CHECK`** clause is mandatory (not just `USING`) so a cross-org **write** is denied, not merely a read filtered. The `NULLIF(...,'')` guard fails closed to zero rows when the GUC is unbound/empty. Refactor the existing `apply()` to compose `enable_rls_on` over its 4 tables (no behaviour change for KGS).

### 2. An **async** GUC-binding seam (the load-bearing new piece)

Add an async equivalent of `bind_organisation_guc` usable by the services' SQLAlchemy async engines: a session/transaction hook that, at the start of each request-path transaction, executes `SELECT set_config('app.current_organisation_id', :org, true)` (transaction-local) with `org = enforced_organisation_id()` (fail-closed; never from the request body). Implement once in `packages/substrate` (e.g. `bind_org_guc_async(session)` + a SQLAlchemy `begin`/checkout event helper) and wire it into each service's session factory so **every** request-path transaction is org-bound. Worker/Celery DB paths (NullPool) bind the same way from their task org-context. Pooled connections are safe because the binding is `SET LOCAL` (dies with the transaction).

### 3. A dedicated `NOSUPERUSER NOBYPASSRLS` runtime role

Provision an app role (e.g. `oraclous_app`) with `NOSUPERUSER NOBYPASSRLS` and the needed `GRANT`s on the org-scoped tables/sequences (via an init script and/or a privileged bootstrap migration). **Migrations keep running as the privileged owner** (`oraclous`) — DDL + `FORCE RLS` require ownership — while **runtime services switch their `DATABASE_URL` to the `oraclous_app` role.** This is a deploy change (compose/helm env + role provisioning), not just code. The substrate's existing role-precondition check (`scoped_pg_connection` refuses `rolsuper`/`rolbypassrls`) should be mirrored as an async startup assertion so a service mis-deployed under a bypassing role fails closed loudly.

### 4. A recurrence guardrail — `check_rls_coverage`

`tools/lint/check_rls_coverage.py` + an integration assertion: every org-scoped table (a manifest, or derived from the models that carry `organisation_id`) must, after migrations, have `relrowsecurity` **and** `relforcerowsecurity` true and an org-parameterised policy. A new org-scoped table shipping without RLS fails CI. (Mirrors `test_postgres_org_schema.py`, generalized across all services.)

### Phasing (service-by-service; each phase is independently shippable + tested)

Order by blast-radius-vs-sensitivity: **credential-broker + auth first** (most sensitive: credentials, tokens, org keys), then capability-registry, harness-runtime, execution-engine, application-gateway, and fold knowledge-graph (already has `apply()` targets) in. Each phase ships: (a) the per-table RLS migration, (b) the async GUC binding wired into that service's sessions, (c) the runtime-role switch for that service, (d) a data-layer isolation test that **removes the app-layer `WHERE` predicate and proves RLS alone returns only the bound org's rows** (the real backstop proof, mirroring `test_org_guc_isolates_postgres_reads_and_writes`), and a cross-org write denied (`WITH CHECK` → 42501). The app-layer `WHERE` filtering stays — RLS is the *backstop*, defense-in-depth, not a replacement.

## Consequences

- **The control becomes real, not documented.** A bug that drops an app-layer `WHERE` clause no longer silently leaks cross-org rows — RLS catches it (the point of a backstop). Closes the ADR-012 §2 gap and grade-A A4.
- **It is a genuine multi-service epic, not a single PR** — ~28 tables across 7 services, an async-seam addition, a role/deploy change. Sized at one phase per service (≈7 vertical slices), each CI-green + isolation-tested before the next. This is why it was deferred from the autonomous remediation run.
- **Runtime role switch is the riskiest step.** Moving services off the superuser to `oraclous_app` requires complete `GRANT` coverage; a missing grant fails a service closed at first query. Mitigation: provision grants in the same migration that enables RLS for that service; assert the role at startup; phase per-service so a mistake is contained to one service.
- **Perf:** one extra `SET LOCAL` round-trip per request transaction (negligible; it is a local GUC set, no I/O beyond the statement). Connection pooling unaffected (transaction-local).
- **`FORCE ROW LEVEL SECURITY` matters:** without it the table owner (often the migration role) bypasses the policy; with services on `oraclous_app` (non-owner, non-super) the policy binds regardless, and `FORCE` covers any owner-role path.
- **Does not touch ReBAC or per-org KMS** — RLS is org-row isolation, orthogonal to relationship authz (still 0 enforcement) and to crypto separation (still a single enc key). Those remain separate surfaces.
- **Open for the decider:** (a) confirm the appetite/timing (this is real engineering across every service); (b) the role name + whether one shared `oraclous_app` or per-service roles; (c) whether to also bind the GUC in worker/Celery paths in the same phase or a follow-on.
