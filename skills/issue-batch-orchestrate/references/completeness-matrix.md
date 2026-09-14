# Completeness matrix

The matrix is what turns "every relevant adaptation happened" from a claim into
something a reviewer can check. It is the group-level form of the plan contract in
`spec/claude/research-plan-implement/` §"The plan is the review surface": name the
files, name the change, name the check.

## Shape

Rows are the member issues. Columns are the artifact classes **the repository under
change actually ships**.

| Member | Source | Spec | Tests | Docs | Config / workflows | Generated index |
|---|---|---|---|---|---|---|
| #623 | `settings.py:41` — coerce topics to string; check: `task test` | not applicable — no spec governs the field | `test_settings.py::test_topics_string` | not applicable — internal | `.github/settings.yml` topics block; check: settings app sync | not applicable |
| #624 | not applicable — config only | `spec/project/project-structure/` §Probot; check: `pre-commit run check-section-refs` | not applicable | `docs/en/setup.md` §Apps; check: `task docs` | `.github/settings.yml` `_extends`; check: app loads the file | `spec/README.md` row; check: `task test` |

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

A repository with no tests carries no Tests column. A repository with a generated
catalog must carry that column, because a missing index regeneration is exactly the
silent omission the matrix exists to catch.

## The cell contract

Every cell holds one of two things:

1. **A named change plus the check that proves it.** The change names the file or path;
   the check returns a signal the run can read — a test id, a task target, a linter, a
   command with an exit code.
2. **`not applicable` plus a reason.** The reason is one clause, and it says why this
   member cannot touch this class.

An empty cell is an incomplete plan. It reads identically to "we looked and there was
nothing", which is the judgement the matrix exists to replace with evidence.

## Failure modes

- **The comfortable blank.** Filling source and tests, leaving spec and docs empty
  because they "probably don't apply". If they do not apply, say so and why — that
  sentence is cheap and it is the whole point.
- **A check that is not a check.** "verified manually" and "looks right" return no
  signal. Name something executable.
- **The estimated count.** When a cell's check produces a number, run it. A number
  nobody measured reads as evidence and is worse than no number.
- **Matrix drift.** When operation 5 surfaces a change the plan missed, that is a local
  adaptation at minimum: update the cell. If it invalidates an admission predicate, the
  mode, or the ordering, it is a structural regression and the plan returns for
  re-approval.
