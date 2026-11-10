# Open-PR slot check

Read before the first push and again immediately before `gh pr create` (step 6). Rule owner: `spec/project/pull-request-workflow/<canonical_language>.md` §"Serial pull-request flow".

## Measure

```
gh pr list --base develop --state open --json number,title,headRefName,author,isDraft --limit 200
```

Drop the row whose `headRefName` equals `OPERATING_BRANCH` (re-entering this skill for a branch whose PR is already open isn't a second PR). Every other row occupies the slot: Draft or not, human or dependency bot (Renovate), this session's or anyone else's. Measure live; never take the count from a checkpoint. Exactly 200 rows means the list may be truncated: treat the slot as occupied.

## Decide

| Caller | Slot free | Slot occupied |
|---|---|---|
| **Orchestrated**: promotion at the head of a merge train (`backlog-delivery-orchestrate` passes `--orchestrated`) | push and open | **refuse**: no push, no `gh pr create`. Report the rows; the train drains the slot first |
| **Standalone**: an operator, or `issue-orchestrate` / `issue-batch-orchestrate` run on their own | push and open | **warn**: list the rows with what each needs to land, then offer: wait and land the open one first (recommended), hand this branch to a running train, or open a second pull request on an **explicit override**. Don't push before the answer: a pushed branch is visible work that can start runs |

Record the override as a decision (`decisions: [{gate: open-pr-slot, answer: override, occupied_by: [<n>, …]}]`) so a resumed run doesn't ask again for the same set and the report names it.

## Why the push is gated too

A pushed branch with no PR doesn't run `pull_request` workflows, but the serial flow keeps waiting work local and unpushed until it is the head, so the slot check happens before the first push, not only before `gh pr create`.
