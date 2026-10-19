# Runs and cancel recipe

Read when step 3 or 4 of `SKILL.md` collects, re-checks, or cancels the runs.

## List the active runs once

One listing per active status covers every PR at once (a per-PR lookup spends rate limit and misses runs that don't carry the PR head SHA):

```
for s in queued in_progress waiting pending; do
  gh api "repos/{owner}/{repo}/actions/runs?status=$s&per_page=100" --paginate \
    --jq '.workflow_runs[] | select(.event | IN("pull_request","pull_request_target"))
          | {id, name, path, status, event, head_sha, prs: [.pull_requests[].number], html_url}'
done
```

The endpoint returns at most 1000 results per query. When a status returns 1000, say so in the report: the sweep is partial.

## Attribute each run to a PR

`head_sha` isn't the PR head for every event, so attribution depends on the event:

- `pull_request`: the run belongs to the open PR whose `headRefOid` equals `head_sha`
- `pull_request_target`: the run carries the **base** tip as `head_sha`, so the SHA says nothing. Attribute it only through `prs` (the run's `pull_requests[]` numbers). Fork PRs leave `prs` empty; such a run is unattributable

A run that can't be attributed to exactly one open PR is left alone and listed in the report.

## Keep / cancel predicate

Keep (never cancel) a run when **any** holds:

- `head_sha` equals the current PR's `headRefOid`, or `prs` contains the current PR's number. This also covers stacked PRs or two PRs opened from one commit, which share a SHA with the current PR
- the workflow `path` names a delivery lane (file name contains `release`, `publish`, `deploy`, or `cd-`): cancelling it can leave a partially published artifact. A reusable workflow's jobs run inside the caller's run, so the caller's `path` is the one to check
- the run can't be attributed (above)

Cancel the remaining runs whose attributed PR is open, non-current, and whose `status` is still `queued`, `in_progress`, `waiting`, or `pending`.

## Re-validate, then cancel

The operator's confirmation can be minutes old. Before the loop, re-read the current PR (`gh pr view <N> --json state,headRefOid`); if it merged, closed, or its head moved, stop and re-run from step 2. Before **each** cancel, re-read the run:

```
gh api repos/{owner}/{repo}/actions/runs/<id> --jq '{status, head_sha}'
```

Cancel only if `status` is still active and `head_sha` equals the recorded value; otherwise count it as skipped. Then `gh run cancel <id>`, which stops the run and every job of it. An error for a run that finished in between counts as already-finished, not failed.

The loop is safe to repeat: a cancelled run is no longer active, so a second invocation after a crash lists only what is left.

## Undo

Cancelling is reversible per run: `gh run rerun <id>`. A rebase of the PR onto the new `develop` tip starts fresh runs on its own, which is the normal path after the current PR merges.
