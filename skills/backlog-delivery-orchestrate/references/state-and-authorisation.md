# State file and standing authorisation

## Gate text

The single gate asks the operator to approve, in one answer:

1. the partition: membership, outcomes, ordering
2. the refresh policy
3. the standing authorisation below, applying to **the approved lanes and their PRs only**

## Covered by the authorisation

- create worktrees and branches for approved lanes
- push lane branches, including `--force-with-lease` after the rebase between merges
- open PRs, apply the labels `pull-request-merge` derives, flip draft to ready, apply `automerge`
- cancel in-flight and queued CI runs of this run's own waiting PRs
- squash-merge via the automerge path, close the member issues of a merged PR
- remove a lane worktree that is clean and merged

## Never covered

`--admin`; a merge strategy other than squash; waiving or re-running a red required check without classification; deleting a remote branch; touching an issue or PR that isn't in the approved partition; cancelling runs of PRs outside this run (they are left untouched and reported); pushing to `develop` directly.

## State file

`.resume/backlog-delivery-orchestrate/<run_id>.yml`, envelope per `spec/claude/resumable-work/` (`schema_version`, `skill`, `run_id`, `started_at`, `last_checkpoint_at`, `inputs`, `phase`, `decisions`, `status`). `inputs` is the repository plus the partition date. Under `state:`:

```yaml
state:
  partition_artifact: .audits/issue-backlog-partition/2026-10-19.md
  refresh: every=2
  authorisation: [worktrees, push, pr, label-ready-automerge, cancel-own-runs, squash-merge, close-issues, remove-clean-worktree]
  merged_count: 2
  merges_since_restart: 0   # reset on every restart; drives every=<N>
  lanes:
    - id: 2026-10-19-sentry-config
      kind: group            # group | single
      members: [664, 671]
      after: []
      worktree: ~/repos/.worktrees/<repo>/sentry-config
      branch: fix/sentry-config
      pr: 701
      head: 3f9a1c2          # PR head SHA when the lane returned; the merge train compares it before any force-push
      lane_run_id: 20261019T191500Z-c4d1   # the lane skill's own .resume run id
      status: pr-open        # planned | running | pr-open | merged | blocked
      blocked_reason: null
```

`phase` values this skill writes: `partitioned`, `authorised`, `round-<n>-running`, `round-<n>-done`, `awaiting-ci`, `merged-<pr>`, `ready-to-restart`, `closed`.

The file holds no secrets and no GitHub facts a later step relies on; lane status is a hint, the live PR state decides.
