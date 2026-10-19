# Example 1: five lanes, two rounds, restart after every merge

Invocation: `/nolte-shared:backlog-delivery-orchestrate --refresh=per-merge`.

## partition and gate

`issue-backlog-partition` returns 2 groups (A, B), 3 singles (C, D, E), 1 pipeline issue, 4 exclusions. Edges: E shares a touch surface with A. The operator approves the partition, the `per-merge` policy, and the authorisation in one answer; the run id is `20261019T190000Z-a3f9`.

## round 1

Ready lanes: A, B, C, D (E waits for A). The first three run in parallel: A, B, C. D is deferred to round 2 because three is the cap. Each agent ends at an open PR: #701, #702, #703.

## merge train

PR 701 goes first (A, which E depends on): rebase, sweep (the runs of #702 and #703 are cancelled, answered by the authorisation), merge, `MERGED` on `origin/develop`, issues closed. Refresh policy fires: the session ends with the restart command.

## restart

`/nolte-shared:backlog-delivery-orchestrate --resume 20261019T190000Z-a3f9` re-reads GitHub, finds #702 and #703 still open, does not ask the gate again, rebases #702, sweeps, merges. After the third merge, round 2 starts with D and E.

## close

Report: 5 PRs merged, the pipeline issue left to `feature-decompose`, nothing blocked.
