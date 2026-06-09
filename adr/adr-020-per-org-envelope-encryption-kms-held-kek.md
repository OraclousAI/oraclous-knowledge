---
confluence_id: TBD
title: "ADR-020 — Per-Org Envelope Encryption with a KMS-Held KEK"
---

# ADR-020 — Per-Org Envelope Encryption with a KMS-Held KEK

## Status

| Field | Value |
|---|---|
| Status | **Accepted** |
| Date | 2026-06-10 |
| Proposed by | solution-architect |
| Approved by | tech-lead (Reza Jahankohan) |
| Supersedes | None |
| Superseded by | None |
| Amends | [ADR-008](adr-008-cloud-hosted-mode-with-equivalent-data-sovereignty.md) (delivers its operator-separation-by-cryptography commitment for the cloud-hosted case); the [credential-broker service-reference](../services-reference/credential-broker-service.md) ("AES-256-GCM with a single `ENCRYPTION_KEY`") |
| Driving artifact | [R7-SEC security-hardening brief](../releases/r7-security-hardening-brief.md) — workstream 2 (KMS / envelope encryption); the as-built single-key posture ([as-built security posture](../engineering/as-built-security-posture.md)) |

## Context

The credential-broker is the platform's recoverable-secret home (ADR-008): OAuth tokens, API keys, connection strings (`credentials.encrypted_cred`) and webhook signing secrets (`webhook_secrets.encrypted_secret`) are encrypted at rest with AES-256-GCM in `core/security.py`. As built, **every** ciphertext across **every** organisation is encrypted under **one** process-wide `ENCRYPTION_KEY` (a base64 env value). That key sits in the broker's environment, so anyone who can read the broker's environment + its database can decrypt every tenant's secrets.

ADR-008 commits cloud-hosted Oraclous to **equivalent data sovereignty** — operator-separation enforced by cryptography, not policy. A single app-held key does not deliver that: the operator (whoever runs the broker) holds the key, so the boundary is policy, not cryptography. Two gaps follow:

1. **No KMS.** The key is in the app environment, not a Key Management Service. There is no hardware/service boundary between "can run the broker" and "can decrypt secrets," no audit trail of key use, no central rotation.
2. **No per-tenant boundary.** One key for all orgs means no per-org rotation, no per-org revocation, and no *crypto-shredding* (destroying one org's key to render only that org's data unreadable). A single key compromise is a total compromise.

R7-SEC closes these as its second headline workstream. Reza's launch decisions (2026-06-10): **per-org DEK**; **AWS KMS** as the real provider (behind a local-first seam); **staged post-launch** — built now, but the invite-only launch ships on the existing single key and cuts over to the envelope when cloud-hosting goes live, so the cutover must be **online and zero-downtime**.

## Decision

Adopt **per-org envelope encryption** in the credential-broker, behind a pluggable **KMS provider** seam, migrated online via a **versioned ciphertext**.

### 1. The envelope (KEK → per-org DEK → secret)

- A **KEK** (key-encryption key) is held by a **KMS** and never leaves it in usable form for AWS KMS (for the local provider it is an env key — see §2).
- Each organisation gets its own **DEK** (data-encryption key, 32 bytes, AES-256). The DEK is generated once, **wrapped** (encrypted) by the KEK, and the wrapped form is stored in a new `org_data_keys` row (`organisation_id` UNIQUE, `wrapped_dek`, `kek_provider`, `kek_key_id`, `created_at`). The plaintext DEK is **never** persisted.
- A secret is encrypted with AES-256-GCM under its org's **plaintext DEK** (obtained by asking the KMS to unwrap the stored wrapped DEK). The plaintext DEK is cached in-process briefly (TTL) so an AWS-KMS unwrap is not paid per operation; the cache holds only DEKs, never the KEK.

This gives a per-tenant cryptographic boundary: rotating/destroying one org's DEK (or its KMS grant) affects only that org. Reading the broker DB alone is useless without the KMS; the KMS sees only DEK wraps/unwraps, never the secrets.

### 2. The `KmsProvider` seam (local-first, AWS-real)

A narrow `Protocol`:

```
class KmsProvider(Protocol):
    async def generate_data_key(self) -> tuple[bytes, bytes]:   # (plaintext_dek, wrapped_dek)
    async def decrypt_data_key(self, wrapped_dek: bytes) -> bytes:  # plaintext_dek
    @property
    def key_id(self) -> str: ...
```

- **`LocalKmsProvider`** (default — dev, self-host, and pre-cutover cloud): the KEK is a 32-byte env key (`KMS_LOCAL_KEK`, base64). `generate_data_key` = `os.urandom(32)` wrapped with AES-256-GCM under the KEK; `decrypt_data_key` unwraps it. No external dependency; the operator still holds the KEK (so self-host keeps full sovereignty), but the per-org DEK structure + the migration are identical to the cloud path.
- **`AwsKmsProvider`** (cloud): `generate_data_key` / `decrypt` via `boto3` against a configured CMK (`KMS_AWS_KEY_ID`). The CMK never leaves AWS KMS; the broker only ever sees wrapped + transiently-unwrapped DEKs. Selected by `KMS_PROVIDER=aws`.

The provider is chosen by config; the rest of the broker depends only on the `Protocol`. Self-hosted deployments keep `local`; cloud-hosted sets `aws`.

### 3. Versioned ciphertext + the online migration

The stored value gains a **version tag** so the two formats coexist during cutover:

- **v1** (legacy): the existing `hex(nonce‖ct)` under the single `ENCRYPTION_KEY`. Untagged (back-compat — an untagged value is v1).
- **v2** (envelope): `v2:` + base64(`nonce‖ct`) encrypted under the org's DEK.

`decrypt` is **format-polymorphic**: a `v2:`-tagged value goes through the envelope (org DEK); anything else is decrypted with the legacy single key. This lets the new code read **both** the moment it deploys. The cutover is the standard zero-downtime sequence:

1. **Deploy polymorphic decrypt** (reads v1 + v2; still writes v1) — safe, reversible.
2. **Flip writes to v2** (every new/updated secret is enveloped; reads still handle v1).
3. **Batched backfill** — a re-encrypt sweep walks each org's v1 rows, decrypts (single key) and re-encrypts (org DEK → v2), idempotent + resumable, org by org.
4. **Retire the single key** — once the backfill is verified (no v1 ciphertext remains), the legacy `ENCRYPTION_KEY` fallback is removed. *This is a separate, later, Reza-signed-off op* (a destructive-change-protocol step, ORAA-4 §15) — **not** part of the S5 build.

R7-SEC S5 delivers steps 1–3 (the envelope live, writing v2, reading both, with a backfill command). Step 4 follows after the backfill is run + verified in each environment.

### 4. Scope

The credential-broker **only** — it is the sole home of recoverable secret material (ADR-008). Other services hold opaque references (a `secret_id` / `broker_secret_ref`), never ciphertext, so they are unaffected. The envelope replaces `core/security.py`'s module-level `encrypt_secret`/`decrypt_secret` with an org-aware `EnvelopeService` (the org is already in scope at every call site — the credential rows and webhook-secret rows are org-stamped).

## Consequences

**Positive**
- Delivers ADR-008's cryptographic operator-separation for cloud-hosting: DB access alone cannot read tenant secrets without the KMS; per-org DEKs give a real per-tenant boundary (rotation, revocation, crypto-shred).
- The seam keeps self-host sovereign (local KEK) and cloud-host KMS-backed from one codebase.
- Versioned + polymorphic = a reversible, zero-downtime cutover; no flag-day re-encryption.

**Negative / costs**
- An AWS-KMS unwrap per (uncached) org adds latency + an external dependency on the hot path; mitigated by the per-org DEK cache (one unwrap per org per TTL, not per secret).
- DEK-cache invalidation on rotation, and KMS availability, become operational concerns (a KMS outage blocks decrypts — fail-closed, by design, for secret material).
- The migration carries two keys (legacy + KEK) until step 4; the broker must hold both during cutover.

**Neutral / deferred**
- **Per-org DEK rotation** (re-wrap on KEK rotation; re-encrypt on DEK rotation) reuses the backfill machinery — deferred until rotation is operationally needed.
- **The single-key retirement** (step 4) is a later Reza-signed-off destructive op.
- Staging: ships **non-gating** for the invite-only launch (the launch runs on v1 + `LocalKmsProvider`); the AWS cutover happens when cloud-hosting goes live.

## Alternatives considered

- **Keep the single key, rotate it periodically.** Rejected — rotation alone gives neither a KMS boundary nor a per-tenant boundary; it does not satisfy ADR-008 for cloud-hosting.
- **Per-org key, but app-held (no KMS).** Rejected — improves blast-radius but still leaves the operator holding all keys; no hardware/service separation.
- **Encrypt the whole DB (TDE) / disk encryption.** Rejected — protects against stolen disks, not against the operator (who has live DB + app access); orthogonal, not a substitute.
- **A dedicated secrets manager (Vault/Secrets Manager) per secret.** Rejected for now — heavier operational surface than needed; the envelope + KMS gives the same cryptographic property with the broker staying the single secret home. Revisit if secret volume/rotation demands it.
