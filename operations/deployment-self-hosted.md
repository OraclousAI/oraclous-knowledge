<!-- source page id: 164022 | title: Deployment — Self-hosted -->
# Deployment — Self-hosted

Operational guide for customers running Oraclous on their own infrastructure. This page tells a self-hosting operator what they need to install, configure, and run the platform.

## Status

Placeholder — substantive content lands in Phase 6

Self-hosted deployment is a first-class delivery mode per ADR-008. The platform ships everything a customer needs to operate Oraclous on their own infrastructure with the same data-sovereignty guarantees as cloud-hosted, minus the compliance posture (which the customer maintains themselves if required).

## What this page will cover

* **Prerequisites** — operating system, container runtime, Kubernetes version, network requirements
* **Supported topologies** — single-node evaluation, multi-node production, high-availability shapes
* **Docker Compose deployment** — for evaluation, development, and small production deployments

    * Quickstart steps
    * Required infrastructure (Neo4j, Postgres, Redis)
    * Initial seeding of default OHM artifacts
    * Verifying the install
    
* **Helm chart deployment** — for production Kubernetes deployments

    * Chart repository location
    * Values reference (links to Configuration Reference)
    * Persistent volume considerations
    * Ingress and TLS termination
    * Resource sizing guidance per service
    
* **External infrastructure** — guidance for customers using managed Neo4j, managed Postgres, managed Redis
* **Upgrade procedure** — how to apply a new platform version, including the all-services-at-the-same-version constraint
* **Backup and restore** — what to back up, restore procedures, recovery testing
* **Security hardening** — recommended TLS, mTLS, secret management, network policies
* **Sizing guidance** — CPU, memory, storage estimates by deployment size

## Related references

* **Deployment Topology** — the service architecture both deployment modes share
* **Configuration Reference** — every environment variable and config flag
* **Release Process** — version cadence and upgrade compatibility rules
* **ADR-008** — equivalent data-sovereignty guarantees in both modes
