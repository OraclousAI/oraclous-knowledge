# ADR-038 — Tool & Data Adoption Primitives (E5)

| | |
| --- | --- |
| **Status** | **Accepted** (Reza sign-off, 2026-06-21) |
| **Driving epic** | E5 — Tool & data adoption + batteries-included registry (issue `oraclous-backend#386`). This ADR is the chain-starter (`#484`) gating `#485`–`#490`. |
| **Builds on** | ADR-001 (four layers; registry is Layer 2), ADR-002 (tools are OHM descriptors), ADR-008 (operator separation), ADR-018 (downstream identity / `X-Internal-Key`), ADR-020 (credential broker envelope), ADR-032 (deny-by-default capability ceiling), ADR-034 (adoption-first import) |
| **Verdict** | **Reshape, not greenfield** — wire three adoption primitives onto the existing capability-registry dispatch spine. |

## Context

A team-of-agents must dispatch three classes of *user-supplied* capability: (1) an unmodified CLI/python **loader run on a schedule** whose output lands in the org store, (2) a local python package's **exported functions as a typed tool group**, (3) external **connectors / MCP servers**. The machinery already exists; this ADR wires the last mile.

- The **capability-registry** is the Layer-2 dispatch spine (ADR-001). A tool is a `kind=tool` OHM `CapabilityDescriptor` (ADR-002); an executor is a `BaseToolExecutor → InternalTool → DatabaseTool` subclass chosen by `domain/executors/factory.py` (`_EXECUTORS` plugin-id map + an `_is_mcp` `spec.type` discriminator).
- `services/tool_execution_service.py:execute_sync` is the **canonical spine**: resolve every declared credential via the broker → write a QUEUED provenance/execution row → dispatch → `context.scrub()` in `finally`. Provenance on every dispatch (Governance §3.7).
- `services/mcp_import_service.py` **already proves the "adopt an external source" pattern end-to-end**: discover → per-org `pending_approval` descriptor → admin **approve/reject HITL gate**; `tool_execution_service` fail-closes on a non-`active` tool.
- **The gap** (`packages/ohm/.../import_/mapping.py:87`): a member's `tools:` line renders to a `core/<slug>@1` ref **with no executor behind it**. E5 wires that ref to a real executor for all three primitive classes.
- The **deny-by-default ceiling is already enforced at two fail-closed seams** — static pre-run (`team_run_service._enforce_member_ceilings → assert_subharness_within_ceiling`, 422 before INSERT) and the single live dispatch seam (`tool_use.py:163`, `binding ∉ tool_ceiling → capability_denied`, before HITL, before `registry.execute`). **This ADR adds NO third gate.**

## Decision

### D1 — Three primitives as first-class registry citizens

| Primitive | Descriptor | Executor (new, thin) | Lift |
| --- | --- | --- | --- |
| **script-as-scheduled-ingestion** | `spec.type=script_ingestion`; immutable invocation contract (argv/entrypoint, `credential_requirements`, output-sink = org store). Loader invoked **AS-IS**, never re-hosted (ADR-034 §5). | `ScriptIngestionExecutor(InternalTool)` — runs the declared argv under the InternalTool timeout; creds injected via the resolved `ExecutionContext`, never baked into the descriptor. New factory `is_script_ingestion` branch. | Reshape (lift legacy `ConnectorFetcher` cursor/rate-limit/auth + ingestion-tool defs onto `InternalTool` + `execute_sync`). |
| **library-as-tool-group** | ONE `spec.type=library_group`; `spec.capabilities[]` = one op per exported function (typed I/O) — the multi-operation shape `_ConnectorToolPlugin.descriptor()` already emits. **Zero harness change** (harness emits one ToolSpec per op as `binding__op`). | `LibraryGroupExecutor(InternalTool)` — dispatches `input_data['operation']` to the named function with validated args. New factory `is_library_group` branch. | Reshape (ADR-034 §5 pre-committed "verifiable function" — EURail merge-spine / bitcoin loaders). |
| **connector / MCP adoption** | MCP ships today (`spec.type=mcp`). **Add** a generic `spec.type=connector` (REST/SQL) from the legacy `ConnectorFetcher` shape. | Reuse `McpToolExecutor` for MCP; new `ConnectorExecutor(InternalTool)` / `DatabaseTool`. New factory `is_connector` branch. | Reshape (MCP shipped R6; connector lifts the legacy base). |

### D2 — Ceiling binding: a pinned two-part identity (adds NO new check)

At adoption, mint and **pin forever**: (1) **Resolution key** — a descriptor whose `metadata.name` **slug-matches** the manifest ref (`RegistryClient.resolve_capability` fail-closes unless `_slug(tool.name) == _ref_slug(ref)`; an `explicit_id` must still slug-match — an id can't smuggle a different capability). (2) **Ceiling key** — `OHMCapability(ref=core/<name>@<version>, binding=<token>)` where `<token>` is **byte-identical** to the member's `OHMMember.tools` entry (the ceiling compare is exact-string, no normalization). Built-in/curated → `core/<slug>@<version>`; per-org adopted → `org:<org-id>/<slug>@<version>`. Replicates `mapping.py:87`. Omit either key → denied 422 / `capability_denied` / fail-closed resolve. **Canonical binding-token format mandated** (lowercase slug; per-org namespaced by org-id).

### D3 — Secret resolution (O1): reuse the broker path verbatim

At dispatch, `execute_sync` walks `spec.credential_requirements` and calls `CredentialBrokerPort.resolve(org, user, requirement, credential_id=instance.credential_mappings[type])` — fail-closed. `RealCredentialBroker` resolves OAuth via `/internal/runtime-token` and api_key/connection_string/etc. via `/internal/resolve-credential`, both org-scoped + `X-Internal-Key`-gated (ADR-018; constant-time, 403/404-masked). Decrypted payload lands in the `ExecutionContext`, consumed transiently, `scrub()`'d. **The IDENTICAL path the harness uses for a BYOM model/judge key.** O1 = one onboarding write (per-org envelope, ADR-020, owned by `#485`) + reuse of this seam. **No service but the broker holds a recoverable secret; no descriptor bakes a key** (ADR-008).

### D4 — Dispatch + provenance + adoption gate (invariants)

- **Everything dispatches through `execute_sync`** (incl. a cron-fired loader run → the SAME provenance row, §3.7). The scheduler routes *through* the spine, never around it.
- **Per-org adoption HITL**: a user-supplied loader/library/connector is `pending_approval`; an **org admin** (not the platform operator — ADR-008) approves→`active` before any run (reuse `mcp_import` `set_status`; rejected-not-deleted retention). Curated/built-in primitives are seeded `active` via `plugin_sync`.

### D5 — Isolation model for user-supplied code (accepted default)

Executing a user's python / shelling their loader is arbitrary code (ADR-007/008 cover credentials, not sandboxing):

- **Out-of-process**: user code runs in a **subprocess**, never in the registry process, under a **hard time + memory/CPU cap**.
- **Deny-by-default egress**: no network unless the descriptor declares an **egress allowlist** (mirrors ADR-025 SQL-connector egress).
- The **approve/reject HITL gate** is the supply-chain barrier.
- Stronger isolation (container/gVisor/seccomp) is a follow-on if the subprocess posture proves insufficient.

## Reuse vs new

**Reused (Reshape):** the `execute_sync` four-layer spine, the factory + executor hierarchy, descriptor authoring + UUIDv5 + `plugin_sync`, the multi-operation descriptor shape + `binding__op` emission, the **entire mcp_import adoption template**, both ceiling seams + the `capability_ceiling=list(member.tools)` channel, the importer ref/binding minting, the registry resolver, the **full broker seam**, the execution-engine cron scheduler + KGS-ingest/ADR-022 recipe sink. **New (thin):** 3 executor subclasses + 3 factory `spec.type` branches + 3 descriptor shapes + the scheduler→adopted-tool extension + the per-function dispatch body + the D5 subprocess wrapper. Nothing forks the framework.

## Consequences / risks

1. **Arbitrary-code isolation (D5)** — the load-bearing risk; the subprocess + caps + egress-allowlist posture bounds it; container-grade isolation is a follow-on.
2. **Binding/ref drift** — exact-string ceiling vs slugified resolution; a sloppy adoption produces a silently-dead capability. Mitigated by D2's mandated format + pinned identity.
3. **Provenance completeness on scheduled runs** — the scheduler MUST route through `execute_sync` (§3.7).
4. **Async gap** — `execute_sync` is sync-only; long runs are owned by the execution-engine, not the registry timeout (the engine→registry dispatch contract is decided in `#489`/the scheduler issue).
5. **Per-org descriptor proliferation** — needs `_MAX_TOOLS`-style bounding + an admin curation story.
6. **Supply-chain trust** — the HITL approval is the barrier; compounds D5.

## Accepted decisions (the open items resolved at sign-off)

- **D5 isolation** — subprocess + time/memory/CPU caps + deny-by-default egress allowlist, **accepted** as the shipping posture for user-code primitives (revisit to container-grade if insufficient).
- **Scheduler/async seam** — long-running adopted-tool runs are owned by the **execution-engine** (extend the cron path that schedules a harness run → an adopted-tool run); the registry stays sync. Detailed in `#489`.
- **#484/#485 split** — `#485` owns the O1 onboarding *write* (paste-once per-org via ADR-020 EnvelopeService); this ADR states only the through-the-registry dispatch+resolve + the ceiling binding.
- **Built-in vs per-org** — curated platform batteries (web-research, common connectors) seed `active` via `plugin_sync` with a global `core/<slug>` token; user-supplied loaders/libraries/connectors are per-org `pending_approval` with an `org:<org-id>/<slug>` token.
- **HITL approver** — an **org admin** (not the platform operator, ADR-008), with rejected-not-deleted audit retention applied uniformly.

## References

- Epic E5 `oraclous-backend#386`; children `#484`–`#490`. ADR-034 §5 (adoption-first import); ADR-020 (credential broker); ADR-032 (capability ceiling); ADR-008 (operator separation); ADR-025 (SQL-connector egress precedent).
