# State file and standing authorisation

Rule owner for the authorisation: `spec/project/pull-request-workflow/` §"Serial pull-request flow".

## Gate text

The single gate asks the operator to approve, in one answer:

1. the partition: membership, outcomes, ordering
2. the refresh policy
3. the standing authorisation below, applying to **the approved lanes, their PRs, and open dependency-bot PRs** only

## Covered by the authorisation

- create worktrees and branches for approved lanes, and commit in them
- push the head lane branch and open its PR (`pull-request-create`'s confirmation is answered by this gate)
- apply the labels `pull-request-merge` derives, flip draft to ready, apply `automerge`
- update the run's own head branch by rebase (`gh pr update-branch --rebase`), and push follow-up fix commits to it
- tick a dependency bot's rebase checkbox (`- [ ] <!-- rebase-check -->`), at most once per head commit
- cancel queued and in-progress `pull_request` / `pull_request_target` runs of waiting train branches and of dependency-bot branches, without a per-run confirmation
- squash-merge a dependency-bot PR whose required checks are all green (`CLEAN`); squash-merge the run's own PRs via the automerge path
- one `gh run rerun --failed` of a red check that `workflow-health-triage` classified as flake or infrastructure
- close the member issues of a merged PR; remove a lane worktree that is clean and merged

## Never covered

`--admin`; a merge strategy other than squash; waiving a red required check, or re-running one without classification; deleting a remote branch; touching an issue or PR outside the approved partition other than a dependency-bot PR; any action on a foreign PR (it is reported and waited for); cancelling `push`, `schedule`, `workflow_dispatch`, `release`, or `merge_group` runs, runs on `develop` or `main`, or delivery-workflow runs; pushing to `develop` directly; force-pushing a PR branch outside the platform's rebase update.

## State file

`.resume/backlog-delivery-orchestrate/<run_id>.yml`, envelope per `spec/claude/resumable-work/` (`schema_version`, `skill`, `run_id`, `started_at`, `last_checkpoint_at`, `inputs`, `phase`, `decisions`, `status`). `inputs` is the repository plus the partition date. `schema_version` is `2`: the lane keys changed with the serial flow, so a version-1 file is refused with `start-new` or `discard`. Under `state:`:

```yaml
state:
  partition_artifact: .audits/issue-backlog-partition/2026-10-19.md
  refresh: every=2
  authorisation: [worktrees, commit, push-head, open-head-pr, label-ready-automerge, update-own-head, tick-bot-rebase, cancel-waiting-and-bot-runs, squash-merge-bot-on-green, rerun-classified, close-issues, remove-clean-worktree]
  merged_count: 2
  merges_since_restart: 0   # reset on every restart; drives every=<N>
  lanes:
    - id: 2026-10-19-sentry-config
      kind: group            # group | single
      members: [664, 671]
      after: []
      worktree: ~/repos/.worktrees/<repo>/sentry-config
      branch: fix/sentry-config
      commit: 3f9a1c2        # branch tip when the lane returned; checked before promotion
      pr: null               # set at promotion
      lane_run_id: 20261019T191500Z-c4d1   # the lane skill's own .resume run id
      status: committed-locally   # planned | running | committed-locally | merge-train | merged | blocked
      blocked_reason: null
```

`phase` values this skill writes: `partitioned`, `authorised`, `round-<n>-running`, `round-<n>-done`, `train-head-<pr>`, `awaiting-slot`, `awaiting-ci`, `merged-<pr>`, `ready-to-restart`, `closed`.

The file holds no secrets and no GitHub facts a later step relies on; lane status is a hint, the live PR state decides.
