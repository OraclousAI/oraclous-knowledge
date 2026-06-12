# ADR-021 — Fail-Closed Operational Defaults and a Shared Degradation-Alert Seam

## Status

| | |
| --- | --- |
| Status | Accepted |
| Date | 2026-06-12 |
| Deciders | security-architect (drafted), Reza (signed off) |
| Driving epic | [#292](https://github.com/OraclousAI/oraclous-backend/issues/292) — Safety & hollowness hardening |
| Extends | [ADR-013](adr-013-fail-closed-authority-placement-at-the-substrate-rebac-seam.md) (fail-closed authority placement) · §3.5 (fail-closed defaults) · [ADR-008](adr-008-cloud-hosted-equivalent-data-sovereignty.md) (operator separation) |

## Context

§3.5 mandates fail-closed, and ADR-012/ADR-013 enforce it at the substrate/ReBAC **authorization** seam. But three **operational** surfaces — surfaced by the backend deep-audit (#292) — fail *open* or degrade *silently*:

* **Fake credential-broker + fake LLM are the literal defaults** (`capability-registry-service core/config.py:47`, `harness-runtime-service core/config.py:54`, `deploy/docker-compose.yml` `:-fake`). A deploy that forgets the env override silently runs the fake broker / scripted LLM — voiding §3.5 and the ADR-008 operator-separation guarantee.
* **The rate-limiter fails open silently** on a Redis outage: `application-gateway-service repositories/rate_limit_store.py::enforce_bucket` swallows with *no* log; `auth-service core/rate_limiter.py` logs only. The bypass is invisible.
* **Startup degradation is invisible**: each `lifespan.py` sets `app.state.<repo>=None` on a store-bind failure and logs a WARNING, but every `/health` route returns a static `status="ok"` — false-healthy while data operations 503.
* **`packages/telemetry` is an empty placeholder** — there is no shared structured-alert seam, so all degradation is buried in unstructured logs.

None of these are production incidents (the live `deploy/.env` overrides the modes and the stores are healthy), so this is **defense-in-depth hardening before external exposure**, not incident response. But they are exactly the fail-open class §3.5 forbids, and the question — *what is the safe default for each surface, and how is the unsafe mode made explicit and visible* — must be decided once so the surfaces do not drift.

## Decision

### 1. Fail-mode policy, per surface

Each surface takes the fail-mode that is **actually safe for that surface**; the unsafe mode requires an explicit opt-in **and** always emits a structured alert. The policy is not "fail-closed everywhere" — it is "fail to the safe state for *this* surface, never silently."

| Surface | Safe default | Opt-in escape hatch | Always |
| --- | --- | --- | --- |
| **Fake broker / LLM** | **fail-CLOSED** — `real` / `live` is the default | `CREDENTIAL_BROKER_MODE=fake` / `HARNESS_LLM_MODE=fake`, set **only** in the dev/CI/smoke compose profile + CI workflow | a loud one-time **startup ALERT** at the selection sites (`core/lifespan.py`, `core/dependencies.py`) whenever fake/scripted is active — never a buried WARNING |
| **Rate-limiter** | **fail-OPEN** — a transient Redis outage must not self-DoS the sole ingress | `allow-during-outage=false` → 503-on-outage, for a hardened deploy with a Redis-HA story | a structured alert on **every** fail-open (kill the silent `enforce_bucket` swallow); route the auth limiter's existing logs through the seam |
| **Startup degradation** | **degraded-health body** — `/health` (or `/readyz`) reads `app.state.<repo>` and returns `status="degraded"` (200 for liveness, 503 for readiness) when a critical store did not bind | a flag-gated `exit(1)`-on-degrade variant, for orchestrator-managed restart | a structured alert at the lifespan catch sites, replacing the bare `logger.warning` |

The `Fake*` classes are retained — they remain valid for CI/smoke; they are simply never reached by accident. The real broker / live LLM factory already fail-close on missing creds / unwired shapes; the only new behaviour is that *selecting fake is explicit and loud*.

### 2. Shared degradation-alert seam

Fill the empty `packages/telemetry` with a **minimal** structured-alert primitive — `alert(severity, code, service, detail, **context)` (and/or `emit_degradation(...)`) — that emits a structured event carrying a stable machine `code` and a severity, **initially backed by structured logging** (WARN/ERROR) so ops can scrape and route it, with a clean extension point for a real alerting backend later. All three surfaces emit through it. This is a function plus an event shape — **not** an alerting framework; the backend itself is out of scope (ops/infra).

## Alternatives considered

* **A. Leave the fail-open defaults as-is.** Rejected — it *is* the §3.5 violation; a forgotten env var silently runs a fake broker/LLM in a "real" deploy.
* **B. Rate-limiter fail-CLOSED by default.** Rejected — failing closed on a transient Redis blip self-DoSes the sole external ingress; availability of the edge outweighs strict limiting during a blip. The opt-in `allow-during-outage=false` flag covers the hardened, HA-backed case.
* **C. `exit(1)`-on-degrade as the startup default.** Rejected as the default — it crash-loops dev/CI where a store is intentionally absent. Offered as a flag-gated variant for orchestrator-managed environments.
* **D. Build a full alerting/observability backend now.** Rejected — out of scope (ops/infra). The minimal seam + structured logging + an extension point is sufficient and avoids over-building.

## Consequences

### Positive

* §3.5 fail-closed extends from authorization (ADR-012/013) to the operational runtime: a misconfigured deploy fails **loudly** (real-mode startup pressure surfaces via degraded-health) instead of silently faking.
* Rate-limit bypass and store-degradation become **visible** to ops via a reusable, structured alert seam.
* The empty `packages/telemetry` placeholder becomes a real (if minimal) substrate other services can adopt.

### Negative / risks

* Flipping the fake defaults **breaks key-free dev/CI/smoke runs unless gated** by the dev/CI profile flag — mandatory mitigation, wired into the smoke compose + CI workflow.
* The `exit(1)`-on-degrade and `allow-during-outage=false` variants must **default to the safe mode** and be documented as advanced (a wrong setting + no HA story 503s all traffic).
* The readiness change touches all 7 substrate/runtime services' lifespan + health — broad, but each edit is mechanical and identical, so it stays one coarse PR (ORAA-4 §19), not a sprawl.

## Enforcement

* **Slice A** (one or two coarse vertical PRs) implements the seam + the three surfaces, with **failure-mode tests as a hard DoD** — e.g. a Redis-outage test proving the limiter's chosen behaviour, and a no-creds startup test proving degraded-health. The dev/CI profile flag is wired into the smoke compose + CI.
* **Slice B** is the trivial `[chore]` for #298 (stale "placeholder shell" `__init__` docstrings).
* Security-architect signs off the safety PRs (the failure-mode tests are the verification surface).
