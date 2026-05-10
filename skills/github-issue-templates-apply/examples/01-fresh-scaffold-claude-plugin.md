# Example 01: Fresh scaffold for a Claude Code plugin repo

## Input prompt

"Scaffold GitHub issue forms for this repo — there's nothing under `.github/ISSUE_TEMPLATE/` yet."

## Input files

- `.claude-plugin/plugin.json` — manifest at repo root, asserts the plugin classification
- `skills/` and `agents/` — top-level folders confirming the plugin shape
- `AUDIENCES.md` — existing audience artefact covering reporters (plugin operators, skill authors) and triagers (plugin maintainers)
- `.github/labels.yml` — label taxonomy with `bug`, `enhancement`, `needs-triage`
- `spec/project/github-issue-templates/en.md` — canonical spec resolved from the target repo
- `skills/github-issue-templates-apply/templates/{bug_report,feature_request,config}.template.yml` — starting points
- `skills/github-issue-templates-apply/references/project-type-fields.md` — Claude-plugin field bundle

## Expected behaviour

1. Run preconditions — confirm `git rev-parse --is-inside-work-tree`, locate `spec/project/github-issue-templates/en.md`, verify `.github/ISSUE_TEMPLATE/` is absent (no uncommitted-content concern), confirm `pull-request-workflow` and `CODEOWNERS` / `SECURITY.md` stay out of scope.
2. Detect project type via signal 1 (Claude Code plugin) — record the matching signal (`.claude-plugin/plugin.json` plus `skills/` + `agents/`) and skip the remaining five signals; read `AUDIENCES.md`, confirm it covers reporters and triagers, record its path and a short hash for the `config.yml` comment block instead of dispatching `audience-identify`.
3. Derive the working set from `references/project-type-fields.md` Claude-plugin bundle — `bug_report.yml` (baseline + required `artefact-kind` dropdown, `artefact-name`, `plugin-version`, `claude-code-version`, optional `transcript` textarea with `render: shell`), `feature_request.yml` (baseline + optional `target-artefact` dropdown only — explicitly NOT required per the strictness cap), and `config.yml` with `blank_issues_enabled: false`; self-validate that `feature_request.yml` ends up with exactly two required fields (search-acknowledgement checkbox + one substantive textarea) and that no closed-taxonomy field is required on the feature template.
4. Surface the full plan to the user as one block — detected project type with matching signal, audience artefact path + reporter/triager audiences, three filenames (`bug_report.yml`, `feature_request.yml`, `config.yml`), per-template field deltas beyond the baseline, planned `config.yml` (`blank_issues_enabled: false`, no `contact_links` proposed), labels pre-filled from `.github/labels.yml` (`bug` / `needs-triage` for bug, `enhancement` / `needs-triage` for feature), and `assignees:` left empty (no documented stable triage owner) — then block until the user replies "apply all" or per-template approval.
5. On confirmation, write all three files in a single batch under `.github/ISSUE_TEMPLATE/`, prepending the YAML-comment derivation block to `config.yml` (project type, audience artefact path + date, list of generated templates, audience hash); on any single-file write failure, delete partial outputs so the directory never lands half-configured. Report the three written paths back to the user and stop without committing.
