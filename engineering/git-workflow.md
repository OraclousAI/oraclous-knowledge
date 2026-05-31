# Git Workflow

## Repositories

- `OraclousAI/oraclous-backend` — Python services
- `OraclousAI/oraclous-frontend` — React + TypeScript application

## Branching model

The trunk is `main`. Direct pushes forbidden. Branch naming:

- `ORA-NNN/short-description` — story work
- `tests/ORA-NNN/short-description` — test-author PR (merges first)
- `chore/short-description` — chores not tied to a Jira ticket
- `hotfix/ORA-NNN/short-description` — urgent production fixes

## Commit messages

Conventional Commits: `<type>(<scope>): <description>`

Types: `feat`, `fix`, `chore`, `docs`, `test`, `refactor`, `perf`, `build`, `ci`

Footer: `Refs: ORA-NNN` or `Closes: ORA-NNN`

## Merge strategy

PRs merge via **squash-merge** by default. Branches rebase onto `main` rather than merging `main` into them.

## Tags and releases

Annotated tags: `git tag -a v0.N.0 -m "Phase N: <name>"`
