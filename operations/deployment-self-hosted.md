# Deployment — Self-hosted

Operational guide for customers running Oraclous on their own infrastructure.

**Status:** Placeholder — substantive content lands in Phase 6

Self-hosted deployment is a first-class delivery mode per ADR-008. The platform ships everything a customer needs to operate Oraclous on their own infrastructure with the same data-sovereignty guarantees as cloud-hosted.

## What this page will cover

- Prerequisites — operating system, container runtime, Kubernetes version, network requirements
- Docker Compose deployment — quickstart, required infrastructure, initial seeding, verifying the install
- Helm chart deployment — chart repository location, values reference, persistent volume considerations
- Upgrade procedure — how to apply a new platform version
- Backup and restore
- Security hardening
