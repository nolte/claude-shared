# Example 01 — Clean merge via the `automerge` label

Happy path: the PR is open + draft, every required check is already
green, the repository ships the `automerge.yaml` workflow plus an
`automerge` label, and no security-sensitive paths are touched. The
skill flips draft → ready, applies the `automerge` label, and the
reusable automerge workflow squash-merges the PR onto `develop`.

## Input prompt

> Promote the draft PR on this branch.

## Input files

Repository state assumed by the harness when this prompt fires:

- Current branch: `feat/skill-examples` (not `develop`, not `main`).
- Working tree: clean (`git status --porcelain` returns nothing).
- `gh auth status`: authenticated against the repository's remote.
- One open PR is associated with the current branch:
  - `state: OPEN`, `isDraft: true`, `baseRefName: develop`.
  - `title: feat(skills): add example scenarios for pull-request-merge`.
  - `mergeable: MERGEABLE`, `mergeStateStatus: BLOCKED` (blocked only
    by the draft flag, not by failing checks).
  - Touched paths (`gh pr diff --name-only`):
    `skills/pull-request-merge/examples/01-clean-merge-via-automerge-label.md`,
    `skills/pull-request-merge/examples/02-pending-checks-reports-and-stops.md`,
    `skills/pull-request-merge/examples/03-wait-mode-with-explicit-flag.md`.
  - Existing labels on the PR: none.
- Feature branch contains `origin/develop`'s tip
  (`git merge-base --is-ancestor origin/develop HEAD` → exit 0).
- `gh pr checks` reports every required status check on `develop`
  with `bucket: pass` / `state: SUCCESS` (`lint`, `test`, `docs-build`,
  `markdownlint`, `commitlint`).
- `gh label list` includes `type:feat`, `area:skill`, and `automerge`
  (among others). It does **not** include `cicd` or `area:claude` —
  those wouldn't apply here anyway because no `.github/workflows/` or
  `.claude/` paths were touched.
- Repository ships `.github/workflows/automerge.yaml` backed by the
  `nolte/gh-plumbing` reusable-automerge with `MERGE_METHOD: squash`.

## Expected behaviour

1. **Preconditions pass silently.** The skill confirms branch ≠
   `develop`/`main`, clean tree, authenticated `gh`, and the
   freshness check (`merge-base --is-ancestor`).
2. **Step 1 inspection runs in parallel** (`gh pr view`, `gh pr checks`,
   `gh pr diff --name-only`, `gh label list`). The skill reports
   the PR number, title, base, head, and the green check rollup.
3. **Step 2 delegates to `review`.** No security-sensitive paths
   (`.github/workflows/`, `.github/settings.yml`, `**/*.sh`, auth /
   signing code) are touched, so `security-review` is **not**
   invoked. The `review` skill returns no blocking findings; the
   skill records that and continues.
4. **Step 3 derives labels.** From the Conventional-Commits prefix
   `feat`, the candidates are `type:feat`, `kind:feat`, `feat`; the
   first that exists in the repo (`type:feat`) wins. Touched paths
   under `skills/` add the candidate `area:skill`, which exists. The
   skill applies both in a single
   `gh pr edit <number> --add-label type:feat --add-label area:skill`
   call and reports them.
5. **Step 4 re-verifies required checks.** Every required check on
   `develop` reports `SUCCESS`. The skill proceeds — it does **not**
   poll, sleep, or enter wait mode (no `--wait` argument and no
   wait-style instruction in the prompt).
6. **Step 5 flips draft → ready.** `gh pr ready <number>` runs;
   `gh pr view --json isDraft` confirms `false`.
7. **Step 6 triggers automerge via the label.** The skill applies
   the `automerge` label using
   `gh api -X POST repos/<owner>/<repo>/issues/<number>/labels
   -f "labels[]=automerge"`. It does **not** fall back to
   `gh pr merge --squash --auto`, because the repository ships the
   automerge workflow and the label exists.
8. **Step 7a verifies the merge landed.** `gh pr view --json
   state,mergedAt,mergeCommit,url` returns `state: MERGED`,
   `mergedAt` populated, `mergeCommit.oid` populated. `git fetch
   origin develop && git log --oneline -1 origin/develop` shows
   the merge commit SHA on `origin/develop`.
9. **Step 7b is skipped.** The PR isn't `OPEN` with green checks +
   `automerge` label — it's already `MERGED` — so the
   automerge-workflow log audit doesn't run.
10. **Step 8 offers (does not execute) cleanup.** The skill verifies
    the remote feature branch is gone via
    `gh api repos/<owner>/<repo>/git/refs/heads/feat/skill-examples`
    returning `404` (`delete_branch_on_merge: true` did its job),
    then offers `git checkout develop && git pull --ff-only` and
    `git branch -d feat/skill-examples` for the user to confirm.
11. **Final report (in German per global user-language policy)**
    surfaces: PR URL, merged-at timestamp, merge commit SHA on
    `origin/develop`, the labels applied (`type:feat`, `area:skill`,
    `automerge`), and the offered local-cleanup commands. No
    workflow-health classification is attached because nothing
    failed.

Hard-rule compliance to verify in this scenario:

- No `--admin` flag was passed at any point.
- No merge strategy other than `--squash` was selected (the
  reusable automerge workflow's `MERGE_METHOD: squash` is the
  active path; `--squash --auto` was never invoked).
- No GitHub label was created from the skill.
- The `review` skill delegation was not skipped.
- No silent rebase / merge of `develop` into the feature branch.
- No polling occurred outside wait mode.
- The merge was confirmed via `state: MERGED` on the PR itself,
  not via the `automerge.yaml` workflow's `SUCCESS` conclusion.
- The remote feature branch was not deleted by the skill — the
  platform setting handled it.
