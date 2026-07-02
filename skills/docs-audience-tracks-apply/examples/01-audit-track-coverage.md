# Example 01 — Read-only audit of track coverage across a bilingual docs tree

Exercises the `audit` operation: a read-only conformance pass that
classifies every Acceptance-Criteria item as `pass`, `missing`, or
`drift`, grouped by spec area, and writes nothing.

## Input prompt

> Audit this repo's docs against the audience-tracks spec.

## Input files

`docs/en/` and `docs/de/` trees, an `AUDIENCES.md` at the repo root
mapping `user`, `contributor`, and `operator`, and an `mkdocs.yml`
declaring the `en`/`de` language list. Roughly 80 % of pages carry a
`track:` key; a handful under `docs/en/guides/` do not, and one page
declares `track: user-docs` while its `audience: operator` maps to
`developer-docs`.

## Expected behaviour

1. **Preconditions pass.** cwd is a git repo, the spec resolves (repo
   copy or plugin fallback), the audience artefact and `mkdocs.yml` are
   found, and the operation resolves to `audit` because the user asked
   for a read-only check.
2. **Findings grouped per spec area.** The skill walks the AC one item at
   a time and reports rows under: track frontmatter, audience-to-track
   mapping, user-docs content contract, developer-docs content contract,
   content-mode mapping, and the home-page contract.
3. **Missing and drift classified.** The `docs/en/guides/` pages without
   `track:` are `missing`; the `user-docs`-vs-`operator` page is a
   content-mode/audience-track mismatch reported as `drift` with a
   one-line evidence snippet.
4. **SHOULD blocks are suggestions.** Absent quickstart/troubleshooting
   blocks are reported as suggestions, not failures; only the MUST
   content blocks fail the audit.
5. **Read-only.** No frontmatter is written and no placeholder page is
   scaffolded — the audit never autofixes. The output ends with the
   coverage summary and routes the user to `migrate`/`patch` for the fix.
