# Example 03: Fresh scaffold for a Python library

## Input prompt

"Generate issue templates for this Python library — we publish to PyPI and don't ship a CLI."

## Input files

- `pyproject.toml` — declares `[project]` with `name = "..."`, build backend `hatchling`, no `[project.scripts]`, no `[[bin]]`; classifiers include `Topic :: Software Development :: Libraries`
- `src/<package>/__init__.py` — public API surface
- `README.md` — contains an "Audiences" section covering library consumers (downstream package authors) and triagers (library maintainers); satisfies the audience-artefact precondition without a separate `AUDIENCES.md`
- `.github/` — present but `ISSUE_TEMPLATE/` subdirectory absent; `pull_request_template.md` exists and stays untouched
- No `.github/labels.yml` and no Probot `settings.yml` declaring labels — label taxonomy unknown
- `spec/project/github-issue-templates/en.md` — canonical spec
- `skills/github-issue-templates-apply/templates/{bug_report,feature_request,config}.template.yml` — starting points
- `skills/github-issue-templates-apply/references/project-type-fields.md` — Python-library field bundle

## Expected behaviour

1. Run preconditions, confirm `git rev-parse --is-inside-work-tree`, verify `.github/ISSUE_TEMPLATE/` is absent, locate the spec, and explicitly note that `.github/pull_request_template.md` and `CODEOWNERS` / `SECURITY.md` / `SUPPORT.md` stay out of scope per the spec — only `bug_report.yml`, `feature_request.yml`, `config.yml` are in play.
2. Walk the six detection signals in declared order — signal 1 (Claude plugin) misses (no `.claude-plugin/plugin.json`), signal 2 (Python application) misses (no `[project.scripts]`), signal 3 matches: Python library — record the matching signal explicitly so it can be written into `config.yml`'s derivation comment and stop walking; read the README "Audiences" section, confirm it covers reporter (library consumer / downstream author) and triager (library maintainer), record the artefact path (README anchor) and a short hash without dispatching `audience-identify`.
3. Derive the working set from the Python-library bundle in `references/project-type-fields.md` — `bug_report.yml` baseline + required `library-version`, required `python-version`, required `reproducer` textarea with `render: python`, optional `traceback` textarea with `render: shell`; `feature_request.yml` baseline only (no Python-library extras defined for the feature template — the bundle lists none, and the strictness cap of two required fields holds: search-acknowledgement + one substantive textarea); `config.yml` with `blank_issues_enabled: false` and no `contact_links` unless the user requests one. Do NOT copy fields from the Claude-plugin or Python-application bundles — bundle isolation per the spec.
4. Self-validate the working set (count required fields per template, confirm the substantive required input on `feature_request.yml` is the single textarea, confirm no closed-taxonomy field is required on the feature template), then surface the full plan to the user — matching detection signal, audience source (README "Audiences" section + hash), three filenames, per-template fields beyond baseline, planned `config.yml`, labels pre-filled as empty arrays (not omitted) because no label taxonomy is detectable, `assignees:` left empty (no documented stable triage owner). Block until the user replies "apply all" or per-template approval.
5. On confirmation, write all three files atomically under `.github/ISSUE_TEMPLATE/` with the YAML-comment derivation block at the top of `config.yml` (project type `python-library`, README-anchor audience artefact path + date, list of generated templates, audience hash). On any single-file write failure, roll back partial outputs so the directory never lands half-configured. Report the three written paths back to the user and stop without committing.
