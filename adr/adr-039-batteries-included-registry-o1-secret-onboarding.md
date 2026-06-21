# ADR-039 — Batteries-Included Registry + O1 Secret Onboarding (E5)

| | |
| --- | --- |
| **Status** | **Accepted** (Reza sign-off, 2026-06-21) |
| **Driving epic** | E5 — Tool & data adoption + batteries-included registry (issue `oraclous-backend#386`). This is the second E5 ADR (`#485`); with ADR-038 it gates the impl pairs `#486`–`#490`. |
| **Builds on** | ADR-038 (adoption primitives + the broker-resolve dispatch rule), ADR-020 (per-org credential envelope), ADR-018, ADR-008 (operator separation), ADR-032 (capability ceiling) |
| **Verdict** | **Reshape** — seed curated tools via the existing `plugin_sync`; reuse the existing credential-store + `EnvelopeService` for O1. No new credential plane. |

## Context

ADR-038 decided *how* a tool/loader/connector is adopted, bound to the deny-by-default ceiling, and credential-resolved at dispatch. This ADR decides (a) **which batteries ship pre-registered and credential-ready** (so a user's first run works with no setup) and (b) the **O1 secret-onboarding contract** — paste a key **once**, scoped per-org, reused by every tool, **no per-tool auth-prompt wall**. The machinery exists: curated tools register via `services/plugin_sync.py:sync_plugins` from `domain/plugins/builtin.py` at lifespan; secrets are stored via the credential-broker `POST /credentials/` (the public gateway path the BYOM model/judge already use) and encrypted per-org by `EnvelopeService.encrypt(organisation_id, plaintext)` (ADR-020 per-org DEK). This ADR fixes the curated *set* + the onboarding *contract*; it adds no new credential plane.

## Decision

### D1 — The curated batteries-included set (seeded `active` via `plugin_sync`, global `core/<slug>` tokens)
Pre-registered + credential-ready, so an imported member that declares the token runs immediately (no per-org adoption HITL for the platform-curated set; ADR-038 D4 reserves `pending_approval` for *user-supplied* primitives):
- **Web-research battery** (item 5, the EURail blocker) — `web.search` / `web.fetch` / `web.read` as a built-in tool group, credential-ready via the broker. *Impl: `#486`.*
- **Common connectors (starter set)** — on the ADR-038 connector framework; the E5 starter is the bitcoin set (Binance / Coin Metrics / FRED / mempool.space / alternative.me / Bitnodes), each a curated `spec.type=connector` descriptor with declared `credential_requirements`. *Impl: `#489`.*
- **Scheduler** — the existing execution-engine cron path (ADR-038 D4: adopted-tool runs route through `execute_sync`; the long-running seam is engine-side). *Impl: `#489` / the scheduler issue.*
- **Notification / delivery sink** — a curated connector that writes to a drafts queue / sends a notification; a **declared, ceiling-gated** capability (never ambient — the "generators have no send/publish/spend tools unless granted" structural boundary). *Impl: `#489`.*

A curated battery's identity is the **global `core/<slug>@<version>`** form (ADR-038 D2), seeded idempotently by `plugin_sync` (deterministic UUIDv5), so a member's `tools:` token is stable platform-wide.

### D2 — O1 secret-onboarding write: paste once, per-org, reused (no new store)
- **Write** — paste a key **once** via the credential-broker `POST /credentials/` through the gateway (the same path the BYOM model/judge use); `EnvelopeService.encrypt(org, plaintext)` stores it under the org's DEK (ADR-020). Operator separation holds (ADR-008): only the broker decrypts.
- **Resolve** — every tool/loader/connector declares `credential_requirements`; at dispatch `execute_sync` resolves the per-org credential via the broker (`/internal/resolve-credential`, `X-Internal-Key`) — **the ADR-038 D3 path verbatim**. One stored key is reused by every capability declaring the same requirement.
- **No descriptor holds a key** (ADR-008); the secret lives only in the per-org envelope.

### D3 — The "no auth-prompt wall" operational rule
- A tool whose `credential_requirements` are **already satisfied** by a stored per-org credential dispatches with **no prompt**.
- A tool with a **missing** requirement fails closed with a **typed** `needs_credential` signal — the requirement id + provider only, a leak-safe machine token (the §3 rule-8 / #483 envelope discipline; **never a value**) — surfaced once so the UI prompts **once**; the pasted key is stored per-org (D2) and **reused**, never re-prompted per tool/run.
- O1 acceptance: *the first scheduled run consumes secrets with no auth-prompt wall.*

### D4 — Curated vs user-supplied boundary (per ADR-038 D4)
- **Curated** (this ADR's set) — seeded `active` via `plugin_sync`, global token, no per-org HITL; platform-vetted, so the ADR-038 D5 user-code isolation concern does not apply.
- **User-supplied** (ADR-038) — per-org `pending_approval` + org-admin HITL + D5 subprocess isolation.

## Accepted decisions (the open items resolved at sign-off)
- **External-call credential policy** — **BYOM-only, per-org** is the default: every external connector/web call resolves a per-org credential (operator-separation-cleanest, ADR-008). A platform-shared key is a deliberate, named exception per connector, never the default.
- **E5 starter connector set** — ship the **web-research battery** (EURail blocker) + the **bitcoin starter connectors** above; the broader catalogue is incremental (later issues), not an E5 gate.
- **`needs_credential` edge contract** — a typed machine token (`requirement_id` + `provider`, no value), surfaced via the gateway under the same leak-safe envelope discipline as VALIDATION_FAILED (cf. `#483`).

## Reuse vs new
**Reused:** `plugin_sync` + `builtin.py` curated seeding; the credential-broker `POST /credentials/` + `EnvelopeService` (ADR-020); the ADR-038 D3 resolve path; the connector framework + `execute_sync` spine; the engine cron scheduler. **New (thin):** the curated descriptors for the web-research battery + starter connectors + delivery sink (impl `#486`/`#489`); the typed `needs_credential` edge signal (D3). No new credential plane, no new registry path.

## Consequences / risks
1. **`needs_credential` leak-safety** — the typed signal must surface only the requirement id + provider, never a value (§3 rule 8; cf. `#483`).
2. **Sink as a capability** — the delivery/notification sink is ceiling-gated like any tool; "no send/publish/spend without a declared, approved sink" must hold (a declared capability, never ambient).
3. **Curated-credential drift** — a curated connector's declared `credential_requirements` must match what the broker resolves, or the first run fails closed.

## References
- Epic E5 `oraclous-backend#386`; children `#484` (ADR-038) / `#485` (this) / `#486`–`#490`. ADR-038 (adoption primitives), ADR-020 (credential broker envelope), ADR-008 (operator separation), ADR-032 (capability ceiling). Related: `#483` (leak-safe error-envelope discipline).
