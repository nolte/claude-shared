# Example 03 — Patching a single audience-track mismatch finding

Exercises the `patch` operation: one `drift` finding from a prior audit,
proposed as a single scoped change the user approves before anything is
written, without bundling unrelated edits.

## Input prompt

> Fix the audience-track mismatch the audit flagged on
> `docs/en/guides/deploy.md`.

## Input files

`docs/en/guides/deploy.md` declares `track: user-docs` but carries
`audience: operator`, which the audience artefact maps to
`developer-docs`. The `docs/de/guides/deploy.md` counterpart has the same
mismatch. The audit run that produced this finding is available.

## Expected behaviour

1. **Operation resolves to `patch`.** A single finding to fix, not a
   whole-tree migration.
2. **Conflict surfaced, not silently resolved.** The skill states the
   mismatch precisely: `audience: operator` maps to `developer-docs`, but
   the page declares `track: user-docs`.
3. **Two resolutions offered.** It proposes either changing `track:` on
   the page to `developer-docs` or changing the audience-artefact entry,
   and asks the user to decide — it does not pick for them.
4. **Frontmatter preserved.** When the user chooses to change `track:`,
   the skill edits only that key in its canonical position (between
   `content_mode` and `last_updated`), leaving `title`, `audience`, and
   `last_updated` untouched (Hard rule 7).
5. **Symmetric across languages.** The same patch is applied to
   `docs/de/guides/deploy.md`; patching only the English page is a Hard
   rule 8 violation.
6. **Build verified.** `mkdocs build --strict` runs green before the
   operation ends, and the skill lists the exact files written with
   absolute paths.
