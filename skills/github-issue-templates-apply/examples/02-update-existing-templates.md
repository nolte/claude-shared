# Example 02: Drift detection on an existing template set

## Input prompt

"Re-run the issue-templates skill on this repo — I think the forms have drifted since we last touched them."

## Input files

- `.github/ISSUE_TEMPLATE/bug_report.yml` — present, missing the required `claude-code-version` field that the current Claude-plugin bundle now mandates
- `.github/ISSUE_TEMPLATE/feature_request.yml` — present, but accumulated four `required: true` fields including a `severity` dropdown (closed-taxonomy violation on the feature template)
- `.github/ISSUE_TEMPLATE/config.yml` — present, derivation comment block names audience hash `aud-2025q4-a7f3` and project type `claude-plugin`
- `.github/ISSUE_TEMPLATE/old-question.md` — legacy Markdown question template still on disk
- `AUDIENCES.md` — current audience artefact, hash `aud-2026q2-b81c` (audience set has shifted; "compliance reviewer" gone, "spec author" added)
- `.claude-plugin/plugin.json` and top-level `skills/` / `agents/` — project type still Claude-plugin (no project-type drift)
- `spec/project/github-issue-templates/en.md` — canonical spec
- `skills/github-issue-templates-apply/references/project-type-fields.md` — current Claude-plugin field bundle

## Expected behaviour

1. Run preconditions, then check for uncommitted changes under `.github/ISSUE_TEMPLATE/` — if dirty, ask whether to stash, commit, or abort before reading further; never overwrite uncommitted edits.
2. Re-detect project type (still Claude plugin — no project-type drift), re-read `AUDIENCES.md` and compare its current hash `aud-2026q2-b81c` against the recorded `aud-2025q4-a7f3` in `config.yml`'s derivation comment — record audience drift (compliance-reviewer audience removed, spec-author audience added) and identify which fields each motivated.
3. Diff the current templates against the freshly derived working set and surface four drift classes per spec §"Re-audit and drift detection" — (a) field drift on `bug_report.yml`: missing required `claude-code-version`; (b) strictness drift on `feature_request.yml`: four required fields (cap is two), substantive required input is no longer a single textarea, `severity` dropdown raised to `required: true` on a feature template (closed-taxonomy violation); (c) audience drift: stale fields motivated by the gone compliance-reviewer audience, new fields motivated by the new spec-author audience; (d) format drift: `old-question.md` is Markdown and should migrate to Issue Forms `.yml` or be removed.
4. Present the diff per item with options "apply / skip / skip and remember" — never auto-rewrite, never silently overwrite. For the `.md` legacy template, propose migration but do not auto-rewrite per the spec.
5. On per-item confirmations, apply approved changes atomically in a single batch (downgrade the three over-required feature fields to optional, drop the `severity` field entirely from the feature template, append `claude-code-version` to `bug_report.yml`, add/remove audience-driven fields per the new audience set), update `config.yml`'s derivation comment with the new audience hash and date, re-read `.github/ISSUE_TEMPLATE/` end-to-end to confirm a subsequent clean re-run produces no diff, and report the resulting changes back to the user without committing.
