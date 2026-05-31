# 10. Engineering Flows

**Document status:** Active · **Maintained by:** solution-architect with tech-lead sign-off

This hub holds the **flows** — how the agent team turns big units of work into small, doable, assignable pieces, and how team members reach agreement on shared things.

## What's here

- [Cross-cutting agreement protocol](./cross-cutting-agreement-protocol.md)
- [Interface Contracts](./interface-contracts.md)
- [Jira board and workflow mapping](./jira-board-and-workflow-mapping.md)
- [Session topology and persona residency](./session-topology-and-persona-residency.md)

## The work breakdown hierarchy

| Level | Artifact home | Owning agent(s) |
| --- | --- | --- |
| **Architecture** | Confluence Section 8 | human tech-lead + solution-architect |
| **Release** | Confluence 09. Releases | human tech-lead + solution-architect |
| **Migration source map** | Release page (Section 7) | product-planner + solution-architect + security-architect |
| **Epic** | Jira | product-planner |
| **Contract** | Jira + canonical home | solution-architect |
| **Story** | Jira | product-planner |
| **Tests** | GitHub `[tests]` PR | test-author |
| **Tests sign-off** | GitHub | be-test-reviewer |
| **Implementation** | GitHub `[impl]` PR | implementer |
| **Final review** | GitHub + Jira | code-reviewer + qa-engineer + architects + tech-lead |
