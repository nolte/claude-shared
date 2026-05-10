# Example 02 — Version-bearing files misaligned with target tag

The operator asks for a publish on `nolte/example-py-lib`. Exactly one
release-drafter draft is open on `develop` for tag `v1.7.0`, but
`pyproject.toml`'s `[project].version` still reads `1.6.3` — the
`chore(release): v1.7.0` alignment commit has not landed yet. Gate 2b
("Version-bearing files aligned") fails. Per the spec the skill MUST
NOT proceed past a failed gate; it surfaces the gate name, the failure
detail, and the remediation path, and refuses to issue
`gh workflow run release-publish.yml`.

## Input prompt

> Trigger release publish.

## Input files

The active checkout is `nolte/example-py-lib` on branch `develop`.
Preconditions all pass: git repo, `gh auth status` OK, default branch
`develop`, both specs reachable.

`gh release list --json isDraft,tagName,targetCommitish,createdAt,name`
returns one element:

```json
[
  {
    "isDraft": true,
    "tagName": "v1.7.0",
    "targetCommitish": "develop",
    "createdAt": "2026-05-09T11:02:55Z",
    "name": "v1.7.0"
  }
]
```

The `targetCommitish` resolves to SHA `4d7e3c91…` and is reachable from
`origin/develop` — Gate 2a passes.

`.github/release-automation.yml` is absent, so the version-bearing-file
list comes from the default Python-library row of `release-automation`
§Version-bearing files: `pyproject.toml` (selector `[project].version`).
At the target SHA `git show 4d7e3c91…:pyproject.toml` returns:

```toml
[project]
name = "example-py-lib"
version = "1.6.3"
```

Under the "strip leading `v`" transform the file value `1.6.3` does
**not** equal the target tag `v1.7.0`.

`git log -1 --pretty=%s --follow -- pyproject.toml` returns
`fix: tighten the retry backoff (#214)` — there is no
`chore(release): v1.7.0` commit on the path either.

`.github/settings.yml` declares `ci / pytest` and `ci / ruff` as
required contexts; both report `conclusion=success` on the develop tip.

`.github/workflows/release-publish.yml` exists in the working tree.

## Expected behaviour

1. **Preconditions confirmed and single open draft resolved.**
   Operations 1 and the precondition block run as in example 01.
2. **Gate 2a passes.** `git merge-base --is-ancestor 4d7e3c91… origin/develop`
   exits `0`. Reported as `PASS`.
3. **Gate 2b fails.** The skill reads
   `pyproject.toml#[project].version` at the target SHA, gets `1.6.3`,
   compares against the target tag `v1.7.0` under the "strip leading
   `v`" transform, and detects a mismatch. The failure detail names
   the file (`pyproject.toml`), the selector (`[project].version`),
   the current value (`1.6.3`), and the expected value (`1.7.0`).
4. **Skill stops at the first failed gate.** Per the spec the skill
   MUST NOT proceed past a failed gate; Gates 2c, 2d, and 2e are not
   evaluated (the alignment-commit gate would also fail, but the
   version-mismatch detail is the actionable signal — the report does
   not pretend to have walked the remaining gates).
5. **Remediation surfaced verbatim from the spec.** The failure block
   reports:
   `Gate 2b — Version-bearing files aligned: FAIL. pyproject.toml#[project].version = 1.6.3, expected 1.7.0 (target v1.7.0 under "strip leading v" transform). Remediation: open a chore(release): v1.7.0 PR (fallback path), or wait for the workflow-driven primary path to land its alignment commit.`
6. **No dispatch issued.** The skill does **not** run
   `gh workflow run release-publish.yml`. No `--dry-run` fallback is
   offered — `--dry-run` validates without flipping `draft: false`, but
   the spec's hard rule still forbids dispatch on any failed gate.
7. **No flip-to-published fallback.** The skill does not call
   `gh release edit --draft=false`, does not call `gh api -X PATCH`
   on the release, and does not propose either as a workaround.
8. **No `workflow-health` handoff.** Gate 2b is a content drift, not a
   red required check; routing to `workflow-health` triage is reserved
   for Gate 2d failures. The skill ends with the operator-facing
   remediation hint and stops.
9. **Hard rules honoured.** Single-shot, no retry, no `--ref` other
   than `develop`, no proceeding past the failed gate, no operator
   confirmation prompt (the dispatch is refused outright; there is
   nothing to confirm).
