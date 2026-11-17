# Completeness matrix

The matrix is what turns "every relevant adaptation happened" from a claim into
something a reviewer can check. It is the group-level form of the plan contract in
`spec/claude/research-plan-implement/` §"The plan is the review surface": name the
files, name the change, name the check.

## Shape

Rows are the member issues. Columns are the artifact classes **the repository under
change actually ships**.

| Member | Source | Spec | Tests | Docs | Config / workflows | Generated index | Existing installations / upgrade / rollback |
|---|---|---|---|---|---|---|---|
| #701 | `settings.py:41` — coerce topics to string; check: `task test` | not applicable — no spec governs the field | `test_settings.py::test_topics_string` | not applicable — internal | `.github/settings.yml` topics block; check: settings app sync | not applicable | consumer config key `topics` now parses as list or string; health gate: none (Python library); rollback restores string-only parsing, so a list written after the update fails on the previous release; check: `test_settings.py::test_previous_release_config_parses` |
| #702 | not applicable — config only | `spec/project/project-structure/` §Probot; check: `pre-commit run check-section-refs` | not applicable | `docs/en/setup.md` §Apps; check: `task docs` | `.github/settings.yml` `_extends`; check: app loads the file | `spec/README.md` row; check: `task test` | not applicable — touches no persisted state, consumer configuration key, invocation name or artifact path |

## Deriving the column set

Derive columns from the repository, never from a fixed list. Probe for what the
repository ships and drop what it does not:

- source: a language manifest (`pyproject.toml`, `package.json`, `go.mod`)
- spec: a `spec/` tree
- tests: a test directory or a `task test` target
- docs: `mkdocs.yml` or a `docs/` tree
- config / workflows: `.github/workflows/`, `.github/settings.yml`, `Taskfile.yml`
- generated index: a catalog or index the build regenerates (`spec/README.md`,
  `docs/*/skills/**`)
- existing installations / upgrade / rollback: the repository ships a deployable
  artefact. Resolve this against `spec/project/release-artifact/` §"Artefact taxonomy"
  for the detected project type rather than keeping a list here. Every row except
  documentation-only names an artefact that an existing installation updates to. A
  deployable artefact the taxonomy does not name yet, such as an OS or appliance image
  or a Helm chart, carries the column too; record the missing taxonomy row as a
  finding rather than dropping the column

A repository with no tests carries no Tests column. A repository with a generated
catalog must carry that column, because a missing index regeneration is exactly the
silent omission the matrix exists to catch.

A repository that ships a deployable artefact must carry the Existing installations /
upgrade / rollback column, for the same reason: what a change does to an installation
that already runs is where the expensive defects sit. A plan gate approved "a short
provisioned secret keeps the services stopped"; only the pre-merge review found that
every automatic update of an existing device then failed its health check and rolled
back, on every update. A repository that ships no deployable artefact drops the column
and says so in one line under the matrix:
`not applicable — the repository ships no deployable artefact (documentation-only)`.

## The cell contract

Every cell holds one of two things:

1. **A named change plus the check that proves it.** The change names the file or path;
   the check returns a signal the run can read — a test id, a task target, a linter, a
   command with an exit code.
2. **`not applicable` plus a reason.** The reason is one clause, and it says why this
   member cannot touch this class.

An empty cell is an incomplete plan. It reads identically to "we looked and there was
nothing", which is the judgement the matrix exists to replace with evidence.

### Existing installations / upgrade / rollback

A change cell in this column names four things, each as a short clause:

1. **Upgraded state:** the state an installation running the previous release is in
   after it updates to this change — migrated data, kept configuration, services running
   or stopped.
2. **Health gate:** whether the update tool's health gate still passes on that upgraded
   installation, naming the gate (the appliance's post-update health check, the Helm
   `--wait` readiness, the package manager's post-install script). Where the artefact's
   update path has no health gate (a Claude plugin, a library or package consumed by
   version), state `health gate: none (<artefact kind>)` and name instead the state
   surfaces the installed version reads: persisted state (such as checkpoint schemas
   under `.resume/<skill>/`), consumer configuration keys or files, invocation names
   (skill and agent names, CLI flags), and artifact paths.
3. **Rollback:** what a rollback restores, and what it can't — a schema migration that
   ran forward, a secret that was rotated.
4. **Proving check:** the executable check that shows all three, such as an update boot
   test from the previous image or a migration test against a snapshot of the previous
   schema. Without a health gate, the check proves compatibility of the named surfaces:
   resuming a checkpoint the previous release wrote, `python3 scripts/validate_skills.py`
   for invocation names, a parse test of the previous release's configuration.

Example cell for an appliance image: "previous image boots, migrates the settings file,
services start; health gate passes; rollback restores the previous image and the
unmigrated file; check: `task test:update-boot`".

Example cell for a Claude plugin whose skill renames a checkpoint field: "a checkpoint
the previous release wrote under `.resume/<skill>/` resumes, the old field read as an
alias; health gate: none (Claude plugin); rollback restores the previous skill, which
ignores the new field, so a checkpoint written after the update resumes without it;
check: resume test from a previous-release checkpoint fixture".

`not applicable` needs a reason, as in any other column. Where the update path has no
health gate, a change still reaches every installation on update, so "cannot reach an
installation" is not a reason. Such a member is `not applicable` only when it touches
none of the four surfaces, and the cell says exactly that:
`not applicable — touches no persisted state, consumer configuration key, invocation name or artifact path`.
The fixed wording is a checklist the reviewer can verify against the diff, not a
boilerplate pass.

## Failure modes

- **The comfortable blank.** Filling source and tests, leaving spec and docs empty
  because they "probably don't apply". If they do not apply, say so and why — that
  sentence is cheap and it is the whole point.
- **A check that is not a check.** "verified manually" and "looks right" return no
  signal. Name something executable.
- **The fresh-install check.** Proving the upgrade column with a test that boots or
  installs from scratch. A fresh install never carries the previous release's state, so
  it passes exactly where the upgraded installation fails its health gate.
- **The estimated count.** When a cell's check produces a number, run it. A number
  nobody measured reads as evidence and is worse than no number.
- **Matrix drift.** When operation 5 surfaces a change the plan missed, that is a local
  adaptation at minimum: update the cell. If it invalidates an admission predicate, the
  mode, or the ordering, it is a structural regression and the plan returns for
  re-approval.
