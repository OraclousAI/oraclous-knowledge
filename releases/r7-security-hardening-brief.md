# R7-SEC — External-launch security hardening (brief)

| | |
| --- | --- |
| Release | **R7-SEC — External-launch security hardening** |
| Status | **Active** (scoped + decisions locked 2026-06-10; built sequentially after R6) |
| Predecessor | [R6 — gateway hardening](r6-gateway-hardening-brief.md) (Released, §22-signed-off) |
| Theme | Turn the **as-built** authz posture (org-scoping only, **no roles**) and crypto posture (**a single `ENCRYPTION_KEY` decrypts every org**) into a minimal, honest, externally-launchable floor — without building anything the launch doesn't need. |

## Why

R6 made the gateway the sole external surface. Before that surface faces external tenants, two as-built gaps must close (the [as-built security posture](../engineering/) — authz is **org-scoping only**; ReBAC is enforced at the substrate/graph seam (ADR-004/ADR-013) but **not** at the application layer; secrets-at-rest use a **single** AES-256-GCM key). R7-SEC closes the launch-blocking subset and **explicitly defers** the rest.

## Launch decisions (Reza, 2026-06-10)

- **Launch model = invite-only / design-partner** → the account-takeover slice (S6) is **deferred** (not blocking when we control who onboards).
- **Sovereignty positioning = not at launch** → KMS/envelope (S5) **stages post-launch** (still built, last, non-gating; an honest interim single-key disclosure stands until it lands). Do **not** sell sovereignty to sovereignty-sensitive buyers until S5 ships.
- **KMS provider = AWS KMS** is the headline cloud integration (behind a `LocalKmsProvider` dev/CI backend); Vault Transit is the self-managed/HSM half of the ADR-008 pair (follow-on).
- **DEK granularity = per-org** (org isolation + amortized KMS calls); per-secret stays a future high-sensitivity tier behind the same seam.
- **Authz = an org-roles floor (admin vs member)**, NOT cross-org ReBAC.

## Slices (sequential; each a §21 vertical cut ending in a live smoke + §22 sign-off)

| # | Slice | Pre-launch blocking? | Touches |
| --- | --- | --- | --- |
| **S1** | **Tenancy-leak verification + anti-spoof audit** — an adversarial cross-org battery against every R6 ingress that mints identity **without** `verify_token()` (integration-key, webhook, chat, MCP); prove `org_id` is real-never-empty and strip-then-assert holds; close any stray `org_id=''`; add the success-path response-header denylist (Server/X-Powered-By, ORAA-279). The #1 launch risk (T1 cross-org leak), largely already mitigated in R6 — **ship first, it gates everything.** | **Yes** (every model) | gateway (verification; assertions reach every downstream) |
| **S2** | **Org-admin roles floor** *(headline #1)* — mint the existing auth-service `OrgRole` (owner>admin>member) as an `org_role` **JWT claim** (PIP); propagate as `X-Principal-Org-Role` through the ADR-018 trusted gateway with **strip-then-assert**; add `require_admin` (PDP/PEP) in the gateway; define `role_rank>=ADMIN` **once** in `packages/governance`. Gate the **destructive** management ops (key mint/revoke, agent publish/unpublish, webhook-sub create/delete) on `require_admin`; reads stay member. **Do NOT** build cross-org ReBAC or wire `ReBACEngine`. | **Yes** (every model) | auth-service (claim), gateway (header + `require_admin`), `packages/governance` (rank helper) |
| S3 | **Webhook per-subscription / per-key rate-limit** (the T5 gate) — above the per-IP edge floor; a single abused subscription is throttled independently. | Pre-launch | gateway |
| S4 | **Cheap follow-ups bundle** — webhook **orphan-secret GC** (an admin-gated broker `DELETE` + idempotent sweep), the chat **history-fold injection fence** (fence/escape the folded transcript), **`/v1/` path normalisation**. | Pre-launch | credential-broker (DELETE), gateway |
| **S5** | **KMS / per-org envelope encryption** *(headline #2; largest; LAST)* — a `KmsProvider` Protocol (`generate_data_key`/`decrypt_data_key`); `LocalKmsProvider` (env KEK; dev/CI/self-hosted) **first**, then `AwsKmsProvider` (boto3, `EncryptionContext={organisation_id,store}`); **per-org DEK** in a new `org_data_keys` table; a **versioned v2 self-describing envelope** in the existing String columns; `core/security` re-routed to the seam (the 3 write + 3 read callers unchanged); **online format-polymorphic decrypt → flip writes to v2 → idempotent org-by-org batched backfill → retire the single-key fallback**. Scope = the two reversible broker stores (`user_credentials`, `webhook_secrets`). **Land an ADR extending ADR-008 first.** | Only if selling sovereignty | credential-broker **only** |
| S6 *(deferred)* | Account-takeover hardening (email-verify, password-reset, login lockout, OAuth refresh) — **deferred** (invite-only launch). | — | auth-service |

## Explicitly deferred (post-launch follow-ons — NOT launch-blocking)

Full cross-org / federation ReBAC (ADR-004) · wiring `ReBACEngine` as the gateway authorizer · per-member-per-resource fine-grained ACLs · the **MCP client / external-tool import** (+ its nonexistent SSRF-safe egress guard + supply-chain HITL + broker-held external creds — its own feature, not a hardening item) · audit-payload-at-rest encryption (extends the S5 seam later) · all superseded-R8 advanced detection (consciousness-drift, federation-laundering, schedule-storm). None are reachable at launch; OpenAPI/KB must declare **only** the auth modes the substrate actually enforces (edge-JWT + org-scoping + integration-key allow-list + the new org-role floor) — no security theatre.

## Top risks

- **Launch-model ambiguity** flips S5/S6 blocking — resolved (invite-only + KMS-stages); S1–S2 are blocking under every model and start immediately.
- **KMS migration data-loss/lockout** — keep the v1 single-key fallback until a verification pass confirms zero v1 rows; per-batch idempotent backfill; cross-org `encryption_context` mismatch is a release gate.
- **ReBAC overreach** — hard-scope S2 to the org-role rank predicate; the brief forbids touching `ReBACEngine`.
- **Anti-spoof regression on `X-Principal-Org-Role`** — same strip-then-assert as `X-Principal-*`; S1's spoof-injection battery is extended to the new header in S2.
- **Honest-disclosure gap** if KMS stages — ship an explicit interim single-key disclosure; don't sell sovereignty until S5 lands.
