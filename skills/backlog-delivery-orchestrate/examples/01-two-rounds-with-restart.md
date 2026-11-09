# Example 1: five lanes, two rounds, one open PR at a time, restart after every merge

Invocation: `/nolte-shared:backlog-delivery-orchestrate --refresh=per-merge`.

## partition and gate

`issue-backlog-partition` returns 2 groups (A, B), 3 singles (C, D, E), 1 pipeline issue, 4 exclusions. Edges: E shares a touch surface with A. The operator approves the partition, the `per-merge` policy, and the standing authorisation (push and open the head PR, automerge, update own head, tick the Renovate checkbox, cancel waiting and Renovate runs, merge Renovate on green) in one answer; the run id is `20261019T190000Z-a3f9`.

## round 1 (local only)

Ready lanes: A, B, C, D (E waits for A's merge). Three lane agents run in parallel: A, B, C. Each ends at `committed-locally`: verified, committed, not pushed. No PR exists yet and no CI runs. D waits only because three agents were running; it starts as round 2 as soon as they return, still locally.

## merge train

The slot read finds Renovate PR #700 (`renovate/pytest-8.x`) open. The script drains it first: `#700 behind -> bot rebase requested`, later `#700 clean -> squash merge requested`, `#700 MERGED`.

The slot is free. A is promoted first (E depends on it): rebase onto `develop`, `task lint`, `pull-request-create` opens #701 as Draft. The script runs in the background for #701 while `pull-request-merge --wait` reviews, flips ready, and applies `automerge`. Meanwhile Renovate opens #702 and pushes; the script prints `cancelled run 88123 (renovate/ruff-0.x)`. `#701 MERGED`; A's issues are closed. The refresh policy fires: the session ends with the restart command. Only #702 (Renovate) is open; B, C, D wait as local branches.

## restart

`/nolte-shared:backlog-delivery-orchestrate --resume 20261019T190000Z-a3f9` does not ask the gate again. The slot read finds #702: the script drains it (checkbox ticked, merged on green). B is promoted as #703 and merged. After each merge the session restarts; C becomes #704, D #705. E is now ready (A is merged), runs as round 3, returns `committed-locally`, and becomes #706.

## close

Report: 5 lane PRs merged, each opened only after the previous one was merged; 2 Renovate PRs merged by the train on green; the runs of waiting Renovate branches cancelled; the pipeline issue left to `feature-decompose`; nothing blocked.
