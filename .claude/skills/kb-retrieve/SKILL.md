---
name: kb-retrieve
description: Token-efficient retrieval from the Oraclous knowledge base — read the root index first, open the ONE relevant section index, then open only the specific file you need; never read the whole tree.
---

# kb-retrieve

Use this skill whenever you need to answer a question from the Oraclous
knowledge base (`oraclous-knowledge`). It enforces the token-efficiency
contract: retrieve **one page via the index**, never the whole tree.

`oraclous-knowledge` is the **canonical** knowledge base. Confluence is a
**read-only mirror**; the `_mirror/` directory in this repo is a non-canonical
dump — ignore it for retrieval.

## Why

The KB is large (~100+ markdown files across 11 sections). Reading the whole
tree, or opening many files speculatively, burns the context budget for no
benefit. The root `llms.txt` / `index.md` exist precisely so you can route to
the single relevant file in two hops.

## Retrieval protocol

1. **Read the root entry point first.** Open `llms.txt` (preferred — it is the
   most compact) or `index.md` at the repo root. Each lists the 11 sections
   with a one-line summary and a relative link to that section's `index.md`,
   plus a "Key entry points" shortlist of the most important canonical docs.
2. **Pick the ONE most relevant section.** Match the question to a single
   section summary. If two seem plausible, pick the more specific one; you can
   always widen later.
3. **Open that section's `index.md`.** It lists the section's pages with links.
   Use it to locate the exact page that answers the question.
4. **Open only the specific file(s) you need.** Read the single page (or at most
   the two or three) that directly bear on the question. Do not pre-load
   siblings "just in case".
5. **Stop when answered.** If the page points to another canonical page, follow
   that one link rather than scanning the directory.

Never run a broad recursive read of the repo, and never open `_mirror/`.

## Example

Question: "What is the commit message convention?"

1. Read root `llms.txt`.
2. The `03. Engineering` summary mentions workflows, conventions, and gates →
   pick `engineering`.
3. Open `engineering/index.md`; find the Git Workflow / PR Conventions page.
4. Open only that one file and read the convention.

Total: 3 files opened, not 100.

## Graph queries — relationships & cross-cutting questions

The index protocol above is the free, fast path for "where is X documented?".
For **relationship** questions — "how does X connect to Y?", "what depends on
Z?", "what is the rationale behind decision D?", or "what am I missing?" — use
the graphify knowledge graph instead of reading files:

- A graph + an agent-crawlable wiki live at `graphify-out/` (built by graphify).
  Start at `graphify-out/wiki/index.md` (communities → god nodes), or
- Query it directly, token-budgeted:
  - `graphify query "<question>"` — broad context (BFS)
  - `graphify query "<question>" --dfs` — trace a specific chain
  - `graphify path "A" "B"` — shortest path between two concepts
  - `graphify explain "X"` — a node and its neighbours

A graph query costs ~3k tokens versus ~230k to read the corpus naively (~80×
reduction). Keep the graph current after KB edits with `graphify <repo>
--update` (incremental — re-extracts only changed files). The graph is the
relationship map; the section indexes remain the fastest path to the one page
that states a fact.

## Anti-patterns

- Reading every file in a section to "be thorough".
- Globbing `**/*.md` and dumping it into context.
- Treating `_mirror/` content as authoritative.
- Skipping the index and guessing file paths.
