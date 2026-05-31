# ADR-008 — Cloud-Hosted Mode with Equivalent Data Sovereignty

| Field | Value |
| --- | --- |
| Status | Accepted |
| Date | 27 May 2026 |
| Approved by | tech-lead (Reza Jahankohan) |

## Decision

Cloud-hosted Oraclous delivers **equivalent data sovereignty** to self-hosted Oraclous:

- Customer state at rest is encrypted under key material the customer controls
- Oraclous staff cannot decrypt customer state by virtue of operating the platform
- Support and debugging happen with the customer's participation, not in lieu of it
- Customers who want operator-accessible debugging can opt into a lower-isolation tier on a per-organisation basis (explicit, audited opt-in)
