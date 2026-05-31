# ADR-004 — Federation via ReBAC Traversal

| Field | Value |
| --- | --- |
| Status | Accepted |
| Date | 27 May 2026 |
| Approved by | tech-lead (Reza Jahankohan) |

## Decision

Cross-organisation access is mediated entirely by the substrate's ReBAC layer. There is no parallel "federation" subsystem; federation is a pattern of ReBAC relations.

- The capability registry exposes a third registry prefix, `federated:<federation-id>`, in addition to `core` and `org:<org-id>`.
- Resolving a `federated:*` reference requires a `has_federation_agreement` relation between the calling and target organisations.
- The audit log records the federation traversal with both organisation identities.
- The policy set must permit the `federated:*` registry (`policy-set:production-federated@1.0.0`).
