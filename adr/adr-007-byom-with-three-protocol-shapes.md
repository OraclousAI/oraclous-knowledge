# ADR-007 — BYOM with Three Protocol Shapes for v1

| Field | Value |
| --- | --- |
| Status | Accepted |
| Date | 27 May 2026 |
| Approved by | tech-lead (Reza Jahankohan) |

## Decision

For v1, Oraclous supports **three** BYOM protocol shapes:

1. **Anthropic native** — the Anthropic Messages API shape
2. **OpenAI-compatible** — the OpenAI Chat Completions API shape
3. **Gemini-compatible** — the Google Generative Language API shape

Credentials are envelope-encrypted: the BYOM credential is stored encrypted under the organisation's KMS-controlled wrapping key. In cloud-hosted mode, the wrapping key lives in customer-controlled key material.
