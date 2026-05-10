# Example 01 — Clean dispatch, every pre-publish gate green

A scheduled-release operator runs the skill against `nolte/example-plugin`,
which has exactly one open release-drafter draft on `develop`. Every one
of the five pre-publish gates declared by
`spec/project/release-skill-layer/<canonical_language>.md` §"Skill B —
Release publish trigger" passes, the operator confirms the disclosed
state, and the skill issues a single `gh workflow run release-publish.yml`
invocation with the mandatory `tag` input. Default single-shot mode —
no wait-mode opt-in — so the skill reports the run URL and stops.

## Input prompt

> Publish the release.

## Input files

The active checkout is `nolte/example-plugin` on branch `develop`.
`gh auth status` confirms an authenticated session, and
`git rev-parse --is-inside-work-tree` returns `true`.
`gh repo view --json defaultBranchRef --jq .defaultBranchRef.name`
returns `develop`. Both `spec/project/release-skill-layer/` and
`spec/project/release-automation/` resolve via the `nolte-shared` plugin
install path.

`gh release list --json isDraft,tagName,targetCommitish,createdAt,name`
returns one element:

```json
[
  {
    "isDraft": true,
    "tagName": "v0.4.0",
    "targetCommitish": "develop",
    "createdAt": "2026-05-09T08:14:22Z",
    "name": "v0.4.0"
  }
]
```

The `targetCommitish` resolves to SHA `9f1c2ab0…` and is reachable from
`origin/develop` (`git merge-base --is-ancestor 9f1c2ab0… origin/develop`
exits `0`).

`.github/release-automation.yml` is absent, so the version-bearing-file
list comes from the default Claude-plugin row of `release-automation`
§Version-bearing files: `.claude-plugin/plugin.json` (selector
`.version`). At the target SHA the file reads `"version": "0.4.0"`,
which under the "strip leading `v`" transform equals the target tag.

`git log -1 --pretty=%s --follow -- .claude-plugin/plugin.json` returns
`chore(release): v0.4.0 (#187)`, satisfying the prefix-match for the
alignment-commit gate.

`.github/settings.yml` declares two required contexts on `develop`:
`ci / lint` and `ci / test`. Both report `conclusion=success` for the
develop tip SHA via
`gh api repos/nolte/example-plugin/commits/<sha>/check-runs`.

`.github/workflows/release-publish.yml` exists in the working tree.

The draft body contains the marker
`<!-- release-skill-layer:project-context-start -->` (Skill A has
already curated the body).

## Expected behaviour

1. **Preconditions confirmed.** Repo is git, `gh` is authenticated,
   default branch is `develop`, and both specs are reachable. The skill
   responds in the operator's language (German).
2. **Single open draft resolved.** `gh release list` returns exactly
   one matching draft (`v0.4.0`, `targetCommitish=develop`); the skill
   does not fall back to a "newest wins" heuristic and does not require
   the operator to pass `--tag`.
3. **Gate 2a passes.** `git fetch origin develop`, target SHA resolved,
   `git merge-base --is-ancestor` exits `0`. Reported as `PASS`.
4. **Gate 2b passes.** `.claude-plugin/plugin.json#.version` reads
   `0.4.0` at the target SHA; under "strip leading `v`" this equals the
   target tag `v0.4.0`. Reported as `PASS` with the diff line
   `.claude-plugin/plugin.json: 0.4.0 == 0.4.0 (target v0.4.0)`.
5. **Gate 2c passes.** Most recent commit touching
   `.claude-plugin/plugin.json` carries the subject
   `chore(release): v0.4.0 (#187)` — prefix match on
   `chore(release): v0.4.0` succeeds (the `(#187)` suffix is accepted
   per `release-automation` §Pre-publish verification).
6. **Gate 2d passes.** Both required contexts (`ci / lint`, `ci / test`)
   report `conclusion=success` on the develop tip. No context is
   `failure`, `cancelled`, `timed_out`, or `in_progress`.
7. **Gate 2e passes.** `.github/workflows/release-publish.yml` exists.
8. **Validated state disclosed.** A single block lists target tag
   (`v0.4.0`), target SHA (`9f1c2ab0…`), every gate result with
   `PASS`/`FAIL`, the version-bearing-file diff summary, an
   audience-coverage note that the draft body already carries the
   `release-skill-layer:project-context-start` marker (Skill A has run;
   no offer to dispatch `release-notes-curate`), and the literal
   command that will be executed:
   `gh workflow run release-publish.yml --ref develop -f tag=v0.4.0`.
9. **Operator confirms.** The skill blocks until the operator confirms;
   on confirmation it issues exactly that invocation. The `tag` input
   is passed explicitly even though only one draft is open.
10. **Dispatch verified.**
    `gh run list --workflow=release-publish.yml --limit 1 --json databaseId,status,conclusion,url,headSha`
    returns a fresh run whose `headSha` equals the draft target SHA and
    whose `status` is `queued` or `in_progress`. The skill reports the
    run URL plus the current status to the operator.
11. **Single-shot default honoured.** No polling loop; the operator did
    not opt in to wait mode (no `--wait`, no phrasing like
    "warte bis der Publish durch ist"). The skill stops after surfacing
    the run URL.
12. **Hard rules honoured.** No `gh release edit --draft=false` call,
    no `gh api -X PATCH …/releases/<id>` flipping `draft=false`, no
    `--ref` other than `develop`, no retry logic — only the one
    `gh workflow run` invocation.
