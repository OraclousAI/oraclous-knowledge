---
confluence_id: "753686"
title: "05. Operations"
---

# 05. Operations

How the platform is deployed, operated, monitored, and maintained. This section is the operator's reference.

This section fills in as the platform reaches operational maturity. Most pages start as placeholders in Phase 0 and grow as the docs-writer agent produces content from merged code.

## What's here

* [Deployment Topology](https://oraclous.atlassian.net/wiki/spaces/OP/pages/720961) — the eight-service architecture shared by both deployment modes
* [Deployment — Self-hosted](https://oraclous.atlassian.net/wiki/spaces/OP/pages/164022) — docker-compose and Helm-based deployment for customers running Oraclous on their own infrastructure
* [Deployment — Cloud-hosted](https://oraclous.atlassian.net/wiki/spaces/OP/pages/589868) — the Oraclous-the-company operational stance for cloud-hosted customers
* [Configuration Reference](https://oraclous.atlassian.net/wiki/spaces/OP/pages/131144) — every environment variable, every config flag, every setting
* [Troubleshooting Playbook](https://oraclous.atlassian.net/wiki/spaces/OP/pages/557099) — common problems, diagnostic steps, resolutions
* [Monitoring and Observability](https://oraclous.atlassian.net/wiki/spaces/OP/pages/852031) — what to monitor, dashboards, alerting, log shapes
* [Incident Response](https://oraclous.atlassian.net/wiki/spaces/OP/pages/983041) — escalation paths, communication templates, post-mortem process
* [Fleet-keeper](./fleet-keeper.md) — intake & anti-stall automation for the agent fleet (ORAA-250): auto-unblock + auto-assign + stall digest. Local script `operations/fleet_keeper.py`.

## Status

Operational documentation is deferred until Phase 6 for substantive content. Placeholders are created earlier so the docs-writer agent has somewhere to write as each service ships. The Deployment Topology page is already substantive because the topology is locked from Architecture v1.1.

## Two deployment modes

Per Architecture v1.1 Section 1, Oraclous supports two deployment modes:

1. **Self-hosted** — the customer operates the platform. Deployment, upgrades, monitoring, incident response are the customer's responsibility. The platform ships as docker-compose for evaluation, Helm charts for production Kubernetes.
2. **Cloud-hosted** — Oraclous-the-company operates the platform on the customer's behalf, with equivalent data-sovereignty guarantees backed by ISO 27001 and SOC 2 Type II compliance.

The operational documentation covers both modes. Where they diverge, separate pages exist for each.

## How this section grows

Each page declares its target structure as a placeholder. Substantive content lands as:

* The corresponding service ships (configuration reference)
* The platform reaches operational use (troubleshooting entries grow from observed patterns)
* Phase 6 work begins (monitoring conventions, incident response procedures formalised)
* Cloud-hosted launch approaches (cloud-hosted deployment operational artifacts, compliance evidence)
