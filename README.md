---
source_page_id: 688237
title: Oraclous Platform
---

# Oraclous Platform

**An open-source platform for organisational second minds — where human members and AI agents work side by side over sovereign data, orchestrated by goals written in natural language.**

**Architecture status:** <custom data-type="status" data-id="id-0">v1.1 LOCKED</custom>   **Implementation:** <custom data-type="status" data-id="id-1">Phase 0 — Setup</custom>

## What this space contains

This is the single source of truth for the Oraclous platform. Architecture, decisions, engineering practices, operational documentation, and compliance evidence all live here. Code lives in GitHub under the [OraclousAI organisation](https://github.com/OraclousAI); work tracking lives in the **Oraclous V1** Jira project; this space is where the _thinking_ lives.

## Navigation

| Section | What's there | Read first if you are... |
| --- | --- | --- |
| **01. Architecture** | The Platform Architecture v1.1 document, the OHM specification, structured governance and threat catalogues | ...new to the project, designing a feature, or reviewing a PR for architectural compliance |
| **02. ADRs** | Architecture Decision Records — the reasoning behind every major decision | ...wondering why a particular choice was made |
| **03. Engineering** | Test strategy, agent team roster, git workflow, code conventions, PR process | ...implementing a task or reviewing a PR |
| **04. Services Reference** | One page per service — purpose, API surface, configuration | ...working on a specific service |
| **05. Operations** | Deployment guides, runbooks, monitoring, troubleshooting | ...deploying, operating, or debugging the platform |
| **06. Compliance** | ISO 27001, SOC 2 Type II, data sovereignty documentation | ...evaluating security or doing a compliance review |
| **07. Frontend** | Frontend architecture, design system, component catalog | ...working on the frontend |
| **08. Meta** | Working agreement, onboarding, index | ...joining the project |

## How this space is maintained

Most content here is authored by humans and AI agents working together. The architecture document is the contract — implementation conforms to it, or the document changes first. ADRs capture decisions as they happen. Service and operations pages are filled in as services are built.

When content needs to change, it changes deliberately, with reasoning. Silent drift is the failure mode this discipline prevents.

## Founding principles

1. **Open Source** — every layer of the platform is open source; no black boxes
2. **No Vendor Lock-in** — all artifacts portable through OHM (the Oraclous Harness Manifest format)
3. **Data Sovereignty** — customer data never leaves customer-isolated infrastructure, in both self-hosted and cloud-hosted deployment modes
4. **Honest Documentation** — the architecture documents what the platform _does_, including its limitations and trade-offs; no marketing-style claims

## Quick links

* [Jira board — Oraclous V1](https://oraclous.atlassian.net/jira/software/projects/ORA/boards/1)
* [GitHub — OraclousAI organisation](https://github.com/OraclousAI)

_Last updated: 27 May 2026 — Architecture v1.1 locked, implementation setup underway._
