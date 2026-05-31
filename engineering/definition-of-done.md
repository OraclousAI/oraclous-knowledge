# Definition of Done

A story is Done when **all** of these are true:

## Brief and tests

- [ ] The product-planner's brief is linked and references the relevant architecture section(s) and ADR(s)
- [ ] The test-author PR has merged, and its tests describe the brief's acceptance criteria
- [ ] All tests in the test PR were previously failing (red) and now pass (green) after implementation

## Implementation

- [ ] Implementation PR references the merged test PR
- [ ] Implementation PR squash-merged to `main` with a Conventional Commit message
- [ ] All CI checks passed: unit, integration, security, isolation, organization_isolation, type checking, lint
- [ ] No new TODOs without a linked Jira ticket

## Review sign-offs

- [ ] code-reviewer approved
- [ ] qa-engineer validated and approved
- [ ] security-architect approved (if security/isolation/organization_isolation story)
- [ ] solution-architect approved (if architectural boundary touched)
- [ ] tech-lead final sign-off recorded

## Documentation

- [ ] Confluence documentation updated where platform behaviour changed
- [ ] In-repo documentation updated where developer-facing behaviour changed
- [ ] If a new ADR was needed, the ADR is merged before story closure

## Security posture

- [ ] No new query path missing `organization_id` or `graph_id` filter
- [ ] No new credential handling that bypasses the credential broker
- [ ] No new logging that could leak secrets (detect-secrets clean)
- [ ] No new threat surface unaccounted for in Section 6.5
