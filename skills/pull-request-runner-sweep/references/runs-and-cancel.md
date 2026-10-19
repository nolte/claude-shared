# Runs and cancel recipe

Read when step 3 of `SKILL.md` collects the runs.

## List a PR's active runs

Run-level, by head SHA (a PR's runs are keyed to its head commit):

```
gh api "repos/{owner}/{repo}/actions/runs?head_sha=<headRefOid>&per_page=100" --paginate \
  --jq '.workflow_runs[] | select(.status | IN("queued","in_progress","waiting","pending"))
        | select(.event | IN("pull_request","pull_request_target"))
        | {id, name, status, event, html_url}'
```

`gh run list --status queued` alone is not enough: it filters one status per call and cannot filter by SHA.

## Keep / cancel predicate

Cancel only when **all** hold:

- the run's `head_sha` equals the `headRefOid` of an open PR that is not current
- `event` is `pull_request` or `pull_request_target`
- `status` is `queued`, `in_progress`, `waiting`, or `pending`

A run on a fork PR carries the fork's SHA; the same SHA lookup works. A run whose SHA matches no open PR is out of scope.

## Cancel

`gh run cancel <id>` cancels the run and, with it, every job of it. It returns an error for a run that finished between listing and cancelling; count that as already-finished, not failed.

## Undo

Cancelling is reversible per run: `gh run rerun <id>`. A rebase of the PR onto the new `develop` tip starts fresh runs on its own, which is the normal path after the current PR merges.
