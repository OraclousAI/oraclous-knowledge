# credential-broker-service

**Layer:** 1 (Substrate) · **Port:** 8002 · **Status:** Production-grade (extension pending Phase 1)

## Purpose

`credential-broker-service` is the platform's secret keeper. It stores credentials under per-organisation encryption and resolves them on demand for authorised invocations. Credentials never leave the broker in plaintext.

## Responsibilities

- Encrypted credential storage (per-organisation encryption keys)
- OAuth token storage with refresh-flow management
- BYOM provider credentials (ADR-007)
- Per-invocation token resolution; tokens never cached outside the broker
- Delegated scope verification (Phase 1 extension)

## Security commitments

- Credentials stored encrypted at rest with per-organisation keys
- In cloud mode: KMS separation ensures Oraclous-the-company cannot unilaterally decrypt (ADR-008)

## Related

- ADR-007 — BYOM with Three Protocol Shapes
- ADR-008 — Cloud-Hosted Mode with Equivalent Data Sovereignty
