# Lektorat-apply operation detail

Full step sequences for the `patch` and `revise` operations plus the audit-trail folder layout, referenced from `SKILL.md` §Operations and §Output handling. The `audit` operation stays in `SKILL.md` because it is the default / common path. The load-bearing invariants for every operation live in `SKILL.md` §Hard rules; this file carries the procedural steps.

## `patch` (one finding, one diff, one approval)

Runs the spec's `patch` operation per §Operations §Operation B — `patch`. Each approval cycle resolves at most one finding.

1. **Run `audit` first** (see `SKILL.md` operation 1) — the patch list is the audit's `findings` array (editorial findings only); `inventory_findings` are **not** patchable. If the caller invoked `patch` standalone, run `audit` implicitly and cache the inventory.
2. **Block on infrastructure conditions** — when `inventory_findings` is non-empty, surface the list to the operator before any patch loop starts. The operator decides: resolve the underlying condition and re-run, or proceed with the partial `findings` set acknowledging the skipped dimensions. Never silently iterate over a partial inventory.
3. **Sort findings in severity order** (`critical` → `warning` → `suggestion`) and present them to the operator one at a time. Within a severity, ties broken by file path then dimension.
4. **For each finding, render the proposed edit as a unified diff** against the on-disk artefact with at least three context lines, labelled with the operation name (`patch`), the finding ID, and the file's repo-relative path. Show the finding's evidence and resolution hint alongside the diff.
5. **Wait for explicit operator decision**: `approve` writes the diff to disk; `skip` defers the finding to the next run; `skip-and-record` records a permanent dismissal (by finding `id`) under `.audits/lektorat/<run>/dismissals.json` so future `audit` runs do not re-surface it.
6. **Pre-write safety checks** (refactor-safety per §Refactor safety): heading-text changes that move the MkDocs-derived slug **must** announce the slug churn to the operator before the write is approved; block-quoted citations and HTML comments **must** stay byte-identical; link `[text](target)` pairs are preserved unless the finding explicitly targets the link; frontmatter key set and key order are preserved; embedded include directives are byte-identical; list items, table rows, and checklist entries are neither reordered, merged, nor split.
7. **After every approved write, re-render the JSON and Markdown reports** under the same `.audits/lektorat/<run>/` folder so the audit-trail reflects the post-patch state. Do not start a fresh run folder per patch; the patch belongs to the audit run that surfaced the finding.

The `patch` operation never silently combines multiple findings into a single edit; a multi-finding fix is a sequence of `patch` operations, not a single one.

## `revise` (full-artefact rewrite with diff review)

Runs the spec's `revise` operation per §Operations §Operation C — `revise`. The rewrite addresses every `critical` and `warning` finding from the prior `audit` in a single pass.

1. **Run `audit` first** on the target artefact (single file, not a set — `revise` is per-artefact). Cache the pre-`revise` findings list and the pre-`revise` total count.
2. **Compose the rewrite** addressing every `critical` and `warning` finding; `suggestion` findings are optional and only adopted when adopting them does not extend the rewrite scope.
3. **Enforce semantic preservation** per §Operation C: every fact, claim, command, identifier, link target, frontmatter key, and code block from the original must still be present in the rewrite, with at most lexical changes (active voice, shorter sentences, lifted prerequisites). Never delete a section, drop a list item or checklist entry, drop a table row, or change a code block — those are structural decisions outside the spec's `revise` scope and belong to the operator.
4. **Forbid new factual content**: if the prose required an addition (new command, new file path, new product name, new URL) that was not present in the original, the operation **must** surface a `suggestion` to the operator and stop. Never invent facts to round out the rewrite.
5. **Render the unified diff** of the proposed full-artefact rewrite (operation `revise`, finding IDs addressed, repo-relative path), with at least three context lines.
6. **Wait for explicit operator decision** on the full diff: `approve` writes the rewrite; `reject` discards it; `revise` invites operator edit instructions and re-composes the rewrite before showing the diff again. Until approval lands, the on-disk artefact is untouched.
7. **Re-run `audit` on the rewrite** before declaring success. Surface any **new** findings the rewrite introduced; if the post-`revise` total finding count exceeds the pre-`revise` count, label the run a **regression** in the operator-facing confirmation and let the operator decide whether to keep, reject, or `revise`-again.
8. **Update the audit-trail folder**: write `pre-revise.json`, `post-revise.json`, `rewrite.diff`, and update `summary.md` to record the regression status. Do not overwrite the original `audit` reports; the `revise` artefacts are siblings.

The `revise` operation never starts without a fresh `audit` pass and never writes the rewrite to disk until the operator explicitly approves the diff.

## Output handling: audit-trail folder layout

All persistent outputs live under `.audits/lektorat/<YYYY-MM-DD-HHMM>/` in the active repository (timestamp in UTC, minute-precision). The folder layout:

```
.audits/lektorat/<YYYY-MM-DD-HHMM>/
├── findings.json        # Machine-readable; top-level keys per spec §Outputs:
│                        #   operation, operation_version, repository, ran_at,
│                        #   language_summary, pipeline_metadata,
│                        #   inventory_findings, findings
├── summary.md           # Human-readable; Infrastructure conditions first,
│                        #   then editorial findings severity-sorted
├── run.json             # Caller-side config: severity floor, resolved target set,
│                        #   user-supplied options (NOT pipeline metadata —
│                        #   that lives in findings.json's pipeline_metadata)
├── dismissals.json      # Recorded skip-and-record entries (patch only)
├── pre-revise.json      # revise only: pre-rewrite audit
├── post-revise.json     # revise only: post-rewrite audit
└── rewrite.diff         # revise only: unified diff of the rewrite
```

Mirrors the audit-trail convention used by `.audits/portfolio/`, `.audits/skill-review/`, and similar layered audits. The folder is per-run; never reuse an existing timestamped folder for a fresh run.
