# Example 03 — Branch lags `origin/develop`, skill refuses and routes back to manual rebase

A `feat/`-prefixed branch that was pushed days ago and is now several
commits behind the current `develop` tip. Exercises the
branch-freshness Hard Rule: the skill **MUST NOT** open a PR whose
feature branch doesn't contain `origin/develop`'s tip, so it presents
the lag, asks the operator for the sync strategy (rebase vs merge),
and — when the operator declines to let the skill drive the sync
itself — refuses to continue and routes them back to a manual rebase
workflow. No `gh pr create` runs.

## Input prompt

> Open the PR for this branch.

## Input files

Current branch: `feat/audience-doc-author-output-shape`. The remote
default integration branch is `develop`. `gh auth status` is healthy,
`git status --porcelain` is empty, and the branch was pushed two
weeks ago to `origin/feat/audience-doc-author-output-shape`. There is
**no** open PR for this branch yet (so pull-request-workflow §Fix-forward
on red checks doesn't apply — the rebase-comment requirement is
limited to open non-draft PRs).

After `git fetch origin develop`:

`git log --oneline origin/develop..HEAD`:

```
4433aa9 feat(audience-doc-author): tighten output-shape contract
```

`git rev-list --count HEAD..origin/develop` reports `7` — the branch
is **behind** `develop` by seven commits.

`git merge-base --is-ancestor origin/develop HEAD` exits **non-zero**.

The repository ships a `Taskfile.yml` with a `lint` target.

## Expected behaviour

1. **Preconditions pass.** `feat/` prefix is allowed, `develop`
   exists on the remote, `gh` is authenticated, working tree is
   clean.
2. **Change context collected in parallel** as in Example 01. The
   skill notes one local commit ahead and a non-trivial number of
   commits behind.
3. **Branch-freshness check fails.** `git merge-base --is-ancestor
   origin/develop HEAD` exits non-zero. The skill **MUST NOT** skip
   this and **MUST NOT** proceed to draft a title or body before the
   lag is resolved.
4. **Lag reported to the operator.** The skill states the precise
   number of commits behind (`7`, derived from
   `git rev-list --count HEAD..origin/develop`) and names the
   spec rule it's enforcing (pull-request-workflow §Branch freshness).
5. **Sync strategy offered.** Per the spec, both rebase and merge are
   permitted. The skill recommends **rebase** because, although the
   branch has been pushed, no open PR exists yet, so review anchors
   aren't at stake. It explains the trade-off and asks the operator
   which they want.
6. **Operator declines automated sync.** The operator says they want
   to handle the rebase themselves so they can carefully resolve a
   conflict they're expecting in `project/audiences.md`. The skill
   **refuses to continue**:
   - It does **not** silently fall back to merge.
   - It does **not** proceed to draft the PR body anyway "for later".
   - It does **not** invoke `gh pr create` under any circumstance
     while the branch is behind.
7. **Routed back to manual rebase.** The skill outputs the exact
   commands the operator should run themselves
   (`git fetch origin develop`, `git rebase origin/develop`, conflict
   resolution, `git push --force-with-lease` with an explicit reminder
   that **plain `--force` is forbidden** by the Hard Rules and that
   `--force-with-lease` is only safe because no open non-draft PR is
   anchored to the current head SHA), reminds them to re-invoke this
   skill once `git merge-base --is-ancestor origin/develop HEAD` exits
   `0`, and stops.
8. **No push, no PR, no pre-push lint.** Because step 6 short-circuits
   the flow, the skill must **not** run `task lint`, **must not** run
   `git push` in any form, and **must not** run `gh pr create`. The
   only side effect is the report back to the operator in their
   language.
