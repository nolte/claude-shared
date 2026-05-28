# Example 02: `patch` on a published top-level README with critical + warning findings

## Input prompt

"Run lektorat-apply patch on README.md, focus on the critical findings."

## Input files (optional)

- `README.md` — top-level repository artefact, English, no MkDocs frontmatter; resolves to the whole audience set per audience-binding priority rule 2 for top-level Markdown
- `AUDIENCES.md` — audience artefact at the repo root, declares `end-users`, `contributors`, `operators`, `maintainers`
- A prior `audit` run already produced `.audits/lektorat/2026-05-21-1430/findings.json` containing two `critical` D5 (register-mismatch, operator-jargon on an end-user-facing artefact) and one `critical` D3 (spelling error in a published artefact) finding, plus several `warning` D4 inconsistency findings
- `.vale.ini` pins `nolte/vale-style@v0.1.10` for EN-text D3 mechanics

## Expected behaviour

1. Run `audit` first on `README.md` to refresh the findings list (the caller invoked `patch` standalone, so the audit pass runs implicitly). Cache the inventory in the existing `.audits/lektorat/2026-05-21-1430/` folder since the patch belongs to that audit run; do not start a fresh timestamped folder per patch.
2. Apply the caller's severity floor — "focus on the critical findings" narrows the patch list to `critical` only. Sort the three `critical` findings in severity-then-file-then-dimension order: D3 spelling (file: `README.md`, line 47), D5 register-mismatch (file: `README.md`, line 89), D5 register-mismatch (file: `README.md`, line 134).
3. **For finding 1 (D3 spelling, line 47)** — render the proposed edit as a unified diff against the on-disk `README.md` with at least three context lines, labelled `[patch] [finding fbd2a91…] README.md`. Show the evidence (`"deploment"` — likely misspelling of `"deployment"`) and the resolution hint (`Replace "deploment" with "deployment"`). Verify the term is not in the `nolte/vale-style@v0.1.10` accept-vocabulary nor in the audience-artefact protected-terms list before proposing the correction. Wait for explicit operator decision: `approve` writes; `skip` defers; `skip-and-record` writes the finding `id` to `.audits/lektorat/2026-05-21-1430/dismissals.json`.
4. **For finding 2 (D5 register-mismatch, line 89)** — the finding flags an operator-internal phrase ("set `LOG_LEVEL=trace` in the operator harness") on an end-user-facing README. The proposed resolution is **not** a silent re-frame — per `spec/project/lektorat/` §D5, wrong-audience content is **flagged for the operator to move**, not rewritten to match a different audience. Render the diff as an inline `<!-- TODO: move to operator docs -->` comment marking the section rather than as a content rewrite. Wait for operator approval.
5. **For finding 3 (D5 register-mismatch, line 134)** — same treatment as finding 2.
6. **Pre-write safety checks** on every approved diff per `spec/project/lektorat/` §Refactor safety: confirm no heading text changed (no slug churn); confirm every block-quoted citation (`> …`) and HTML comment stays byte-identical; confirm Markdown links `[text](target)` are preserved unless the finding explicitly targets a link; confirm the YAML frontmatter (if any) keeps key set and key order; confirm no list-item / table-row / checklist-entry reorder, merge, or split.
7. **After every approved write, re-render `findings.json` and `summary.md`** under the same `.audits/lektorat/2026-05-21-1430/` folder so the audit-trail reflects the post-patch state. The dismissals from `skip-and-record` are honoured by stable finding `id` on the next `audit` run.
8. Confirm in English with the per-finding outcome (approved / skipped / skipped-and-recorded), the remaining `warning` findings the operator deferred to a later run, and a follow-up reminder: the operator still needs to stage the README change (`git add README.md`), commit it, and open a PR via `nolte-shared:pull-request-create` — this skill **never** stages, commits, bumps `.claude-plugin/plugin.json` version, or opens PRs.
