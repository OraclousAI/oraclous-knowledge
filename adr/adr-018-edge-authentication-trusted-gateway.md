---
confluence_id: TBD
title: "ADR-018 — Edge Authentication: the gateway is the single auth boundary; services trust forwarded identity"
---

# ADR-018 — Edge Authentication (Trusted Gateway)

## Status

| Field | Value |
|---|---|
| Status | **Accepted** |
| Date | 2026-06-05 |
| Proposed by | solution-architect |
| Approved by | tech-lead (Reza Jahankohan) |
| Supersedes | None |
| Superseded by | None |
| Driving artifact | FE-first integration finding (2026-06-05): every R3.5 service re-validates the JWT, so a real session required `*_AUTH_MODE=jwt` set on all five services and the JWT secret distributed everywhere |

## Context

The R3.5 build gave **every** service its own identity seam that **re-validates the bearer JWT** (`*_AUTH_MODE=dev|jwt`). The application-gateway already terminates auth at the edge: in `jwt` mode it verifies the HS256 token, then forwards the verified identity downstream as `X-Principal-Id` / `X-Principal-Type` / `X-Organisation-Id`, **stripping any client-supplied copies first** (anti-spoof). But the upstream services ignore those headers and decode the token again themselves.

This surfaced concretely during FE-first work: a real login token only reached a protected endpoint once `GATEWAY_AUTH_MODE=jwt` **and** `KGS_AUTH_MODE=jwt`/`KRS_AUTH_MODE=jwt`/`CAPABILITY_REGISTRY_AUTH_MODE=jwt`/`CRED_BROKER_AUTH_MODE=jwt` were all set, with the shared `AUTH_JWT_SECRET` present in every container. Re-validating at every hop is wrong on several axes:

- **Duplicated work** — the token is verified once at the edge and then again at each upstream, for no added trust.
- **Coupling to the auth mechanism** — every service must hold the JWT secret and know the token shape. Changing how auth works (rotation, a different algorithm, opaque tokens, a session service) means touching every service.
- **Lock-step configuration** — the whole fleet must be flipped to the same mode together; a single service left in `dev` silently rejects real tokens.
- **No clean ingress story** — services that each accept any valid JWT cannot be safely exposed, and the edge's verified identity is wasted.

The desired model is the standard one: **authenticate once at the edge; downstream services trust the edge's verified identity and use it only for internal operations** (org-scoping, ownership, ReBAC). The open question is how an upstream service *trusts* that a request — and its `X-Principal-*` headers — actually came from the gateway and not from a direct caller forging headers.

## Decision

Adopt **edge authentication**. The application-gateway is the **single authentication boundary**; upstream services **trust the gateway's forwarded identity and do not re-validate tokens**.

1. **The gateway terminates auth** (verifies the JWT/session), resolves the `Principal`, and forwards `X-Principal-Id` / `X-Principal-Type` / `X-Organisation-Id` / `X-Principal-Org-Role` (the member's org role — added R7-SEC S2; present only when the principal carries a role), stripping any client-supplied copies (anti-spoof — the role is trust-asserted exactly like the other `X-Principal-*`).

2. **The gateway attests every forwarded request with `X-Internal-Key`** — a shared secret (`INTERNAL_SERVICE_KEY`) injected on all upstream requests (a client-supplied copy is stripped first, exactly like `X-Principal-*`). This is the proof-of-origin that a request came through the gateway.

3. **Services gain a `gateway` auth mode** that becomes the production default. In `gateway` mode a service:
   - requires a valid `X-Internal-Key` (constant-time compare, **fail-closed 403** if missing/wrong/unset);
   - builds its `Principal` from the trusted `X-Principal-*` / `X-Organisation-Id` headers;
   - **validates no token** and holds no JWT secret;
   - scopes all work to the real `X-Organisation-Id` through the existing governance/tenancy context.

4. **`dev` mode is retained** for each service's standalone smoke (fixed `dev-token` → fixed dev principal/org). A direct-`jwt` mode may be retained per service for reaching it without the gateway in testing, but it is **not** the production path.

5. **Sole ingress.** In production only the gateway is network-exposed; upstreams are internal. The `X-Internal-Key` gate is **defense-in-depth** so that even if an upstream port is reachable (as in local compose, where services keep host ports for their smokes), a request without the shared key is rejected — trust does not rest on network isolation alone.

### Trust mechanism: why `X-Internal-Key`

`X-Internal-Key` (a shared secret, constant-time compared, fail-closed) was chosen over **network-isolation-only** (rejected: no protection if a port is ever exposed, and local compose exposes them by design) and **mTLS** (deferred: heavier to operate; revisit at infrastructure hardening if a stronger guarantee is needed). The primitive already existed in the capability-registry (`verify_internal_key`, `INTERNAL_SERVICE_KEY`) for service-to-service calls; this ADR generalises it to the gateway→service edge.

## Consequences

- A real session works through the gateway with **no JWT secret in the data services** and no per-service `jwt` toggling. The full stack runs `GATEWAY_AUTH_MODE=jwt` + each data service in `gateway` mode, sharing one `INTERNAL_SERVICE_KEY`.
- Auth mechanism changes are localised to the gateway. Services depend on the *shape* of the forwarded identity, not on how it was authenticated.
- The auth boundary and the org-scoping source unify: identity and the org come from the same trusted headers.
- **Migration is per service.** The gateway-side attestation lands once; each service adopts `gateway` mode incrementally (knowledge-graph-service first, then knowledge-retriever, capability-registry, credential-broker). Until a service is migrated it keeps working in `dev`/`jwt` mode.
- The `X-Internal-Key` is a shared secret and must be rotated/managed like one; it is dev-default `dev-internal-key` locally and a real secret in production. It is proof-of-origin, **not** a substitute for the gateway's token verification.
- **As-built (2026-06-05):** the gateway-side `X-Internal-Key` injection and the **knowledge-graph-service** `gateway` mode are implemented and live-verified (edge-auth round-trip succeeds; a direct-to-service call with a forged identity and missing/wrong key is rejected 403). The remaining services adopt `gateway` mode in follow-up increments.

## Alternatives considered

### A. Keep per-service JWT validation (status quo)
Every service re-validates the token. Rejected: duplicated verification, every service coupled to the JWT secret and token shape, lock-step configuration, and no clean ingress model. This is the very state that motivated the ADR.

### B. Trust forwarded headers with network isolation only (no shared key)
Services trust `X-Principal-*` purely because upstreams are unreachable except via the gateway. Rejected as the *sole* control: it has no defense if a port is ever exposed, and the local compose exposes service ports by design for their smokes, so header-spoofing would be trivially possible there. Network isolation remains valuable in production but is layered *under* the `X-Internal-Key` gate, not relied on alone.

### C. mTLS between gateway and services
Mutual TLS gives a strong cryptographic proof of origin. Deferred rather than rejected: heavier to provision and operate (cert lifecycle) than a shared header secret, and the `X-Internal-Key` gate already closes the spoofing gap for the current threat model. mTLS can be added at infrastructure hardening if a stronger guarantee is warranted.
