# Example 01 — Read-only audit ranking duplicated paragraphs

Exercises the `audit` operation: a read-only scan that hashes paragraph
blocks across the `docs/<lang>/` trees, groups exact duplicates over the
spec's DRY threshold, ranks them, and proposes a canonical source per
finding — writing nothing.

## Input prompt

> Find duplicated content across the docs.

## Input files

`docs/en/` where an identical four-line "installing the CLI" paragraph
appears verbatim on three guide pages, and a two-line note that appears on
two pages. `mkdocs.yml` declares `mkdocs-include-markdown-plugin` and it
is pinned in the Python dep manifest. A `CONTRIBUTING.md` at the repo root
contains the same install paragraph.

## Expected behaviour

1. **Preconditions pass.** cwd is a git repo, the `mkdocs-structure` spec
   resolves, the language list comes from `spec/.spec-config.yml`, and the
   include plugin is present and pinned (missing it would route to
   `mkdocs-structure-apply patch`, not add it here).
2. **Non-page and generated content excluded.** `_`-prefixed snippet
   folders, catalog-generator pages, and pages already carrying an
   `{% include-markdown … %}` directive are skipped; the latter surface
   separately as "partial DRY (existing include)" hints.
3. **Frontmatter stripped, blocks hashed.** Each page's YAML frontmatter
   is removed before splitting; blocks are whitespace-normalised and
   hashed, with fenced code blocks treated as one indivisible unit.
4. **Findings over threshold only.** The four-line × three-page install
   paragraph is a finding; the two-line note is *not* (below the ≥3-line
   floor). Thresholds are read from the spec, never baked in.
5. **Ranked by impact.** Findings are ordered by `line_count ×
   occurrence_count` descending.
6. **Canonical source proposed.** Because the install paragraph also
   lives verbatim in `CONTRIBUTING.md`, the skill proposes that live
   source file over a new dedicated snippet (Hard rule 8).
7. **Read-only.** The audit emits the findings table plus the
   `approve <id>` / `skip <id>` choice list and writes nothing.
