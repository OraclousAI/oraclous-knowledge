# Section 6.5 — Security Threats and Mitigations

**Related structured artifact:** [Structured Threat Catalogue](./structured-threat-catalogue.md)

This section is the _architectural narrative_ — ten threat families with attack mechanisms, coded mitigations, residual risk analysis, and operational guidance.

## Four foundational security principles

- **S1 Defence in depth** — no single control is sufficient
- **S2 Fail closed** — uncertain permission decisions deny; they never grant
- **S3 Untrusted input universally suspect** — all LLM outputs, all API inputs, all external data
- **S4 Provenance as audit guarantee** — every action recorded; the audit trail is load-bearing

## Ten threat families

1. **T1 — Prompt injection** — external content hijacks the model's system prompt
2. **T2 — Tool poisoning** — a tool's description manipulates the model's planning
3. **T3 — Exfiltration via tools** — the model is induced to exfiltrate data through tool calls
4. **T4 — Identity confusion** — model conflates roles, actors, or authorities
5. **T5 — Manifest tampering** — OHM artifacts modified between publication and execution
6. **T6 — Consciousness poisoning** — consciousness records manipulated to alter agent behaviour
7. **T7 — Resource exhaustion** — deliberate or accidental budget consumption
8. **T8 — Side channels** — timing, error-message, or size-based information leakage
9. **T9 — Federation attacks** — cross-workspace traversal exploited for lateral movement
10. **T10 — Cloud-mode threats** — operator-separation breaches, cross-tenant data access

See the [Structured Threat Catalogue](./structured-threat-catalogue.md) for the machine-readable implementation contracts (T1-T7 codified, attack chains, mitigation IDs, required test markers).
