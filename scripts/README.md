# scripts/

Tooling for the Oraclous Knowledge Base retrieval layer (WS-D Phase 1).

## `build_kb_index.py` — KB index generator

Deterministic, idempotent generator (Python 3, standard library only) that
keeps the root `index.md` and `llms.txt` in sync with the content sections.

It walks the 11 canonical content sections — `adr/ architecture/ compliance/
contracts/ engineering/ flows/ frontend/ meta/ operations/ releases/
services-reference/` (skipping `_mirror/`, `.git/`, `scripts/`, `.githooks/`,
`.claude/`). For each section it reads `<section>/index.md`, extracts the
frontmatter `title` (regex, no PyYAML) and the first prose paragraph as a
one-line summary, and counts the `.md` files in the section. It then
regenerates two files at the repo root:

- **`index.md`** — a navigable root index: title, the "How agents should use
  this" token-efficiency contract, and a table of the 11 sections with summary
  and file count.
- **`llms.txt`** — the llms.txt-convention entry point (relative links): a
  blockquote summary, the 11 section links, a curated "Key entry points" list,
  and an "Optional" note that `_mirror/` is a non-canonical Confluence mirror.

Both files carry a `GENERATED ... do not edit by hand` header. Output is stable
(sections are processed alphabetically by path) so regeneration is reproducible.

### Usage

```sh
# Regenerate index.md and llms.txt
python3 scripts/build_kb_index.py

# CI / pre-commit check: verify the on-disk files are current.
# Exits 0 if up to date; exits 1 with a unified diff hint if stale or missing.
python3 scripts/build_kb_index.py --check
```

Run the script from anywhere — it resolves the repo root from its own location.

The generator also prints, to stderr, any section whose `index.md` lacked a
parseable frontmatter `title` or prose summary (so the content can be fixed).

## `setup-hooks.sh` — activate git hooks

`core.hooksPath` is local config and cannot be committed, so each clone runs
this once to point git at the tracked `.githooks/` directory:

```sh
sh scripts/setup-hooks.sh
```

## `.githooks/pre-commit`

A POSIX `sh` hook. When a commit stages a tracked `.md` file under any content
section, it runs `python3 scripts/build_kb_index.py` and `git add index.md
llms.txt`, so every commit carries a current index. It is fast and offline; if
`python3` is missing it prints a warning and exits 0 rather than blocking the
commit.

### CI usage

In CI, run the check mode to fail the build if someone edited content without
regenerating the index:

```sh
python3 scripts/build_kb_index.py --check
```
