# Merge train

Read at operation 4. Rule owner: `spec/project/pull-request-workflow/` §"Serial pull-request flow". Exactly one PR against `develop` is open at a time; the lanes' work waits as local, unpushed branches until it is the head.

## Each turn

1. **Read the slot live**: `gh pr list --base develop --state open --json number,headRefName,author,isCrossRepository,createdAt --limit 200`. Sort each open PR into exactly one class:
   - **own**: a PR recorded in this run's lanes
   - **bot**: author login on the dependency-bot allowlist (Renovate) and `isCrossRepository == false`
   - **foreign**: everything else, including another session's PR and any fork PR
2. **Foreign PR open** → don't promote. Set `phase: awaiting-slot`, report the PR and what it needs, checkpoint, and halt the train; never touch it. Lane rounds may continue locally. `--resume` re-reads the slot.
3. **Own PR open** (after a crash or restart) → land it (step 6) before anything else.
4. **Bot PRs open, nothing else** → drain them: run the script with the bot PRs, oldest first, and act on its exit (below). The script ticks a `BEHIND` bot PR's rebase checkbox and squash-merges it on `CLEAN`.
5. **Slot free** → promote the next `committed-locally` lane, in dependency order, then partition order:
   1. Check `git -C <worktree> rev-parse HEAD` equals the lane's `commit` and the tree is clean; otherwise set the lane aside and report it.
   2. `git -C <worktree> fetch origin develop` then `git -C <worktree> rebase origin/develop`. A conflict: `git -C <worktree> rebase --abort`, mark the lane `blocked`, set aside its dependents too, and promote the next independent lane.
   3. Run the repository's lint target in the worktree (§Pre-push verification). Don't re-run the full suite: the lane verified it once, and after the rebase CI is the verification.
   4. Run `pull-request-create --orchestrated` from the worktree with the lane's drafted title and body; its slot check refuses if the slot filled meanwhile, and the turn starts over at step 1; it pushes and opens the PR as Draft. Its title/body confirmation is answered by the standing authorisation; the body goes into the run report. Record `pr` and set the lane `merge-train`.
6. **Land the head.** Start the script in the background with the head PR, `${CLAUDE_PLUGIN_ROOT}/skills/backlog-delivery-orchestrate/scripts/merge-train.sh <pr>`, from the primary checkout. While it keeps the runners for the head, run `pull-request-merge` in wait mode from the lane worktree: its `review` and `security-review` delegation stays, and a blocking finding stops this PR and is shown verbatim. If the script reported `branch rebased onto develop`, first bring the worktree to the remote head: `git -C <worktree> fetch origin <branch>` and `git -C <worktree> reset --keep origin/<branch>` (the tree is clean, so nothing is lost). When wait mode ends with the head still pending, re-invoke it; the script keeps running until its own cap.
7. **After the merge**: verify `state == MERGED` and the merge commit on `origin/develop`, close the lane's member issues with the cross-reference comment `pull-request-merge` prescribes, and remove the lane worktree only if it is clean (`git worktree remove` without `--force`). The remote branch is the platform's job (`delete_branch_on_merge`): confirm a `404` on the ref, never delete it.
8. Checkpoint, then the refresh check (operation 5), then the next turn.

## Acting on the script's exit

| Exit | Last line | Action |
|---|---|---|
| 0 | `train done` | every queued PR merged; continue with step 7 for own PRs, then the next turn |
| 1 | `#N FAIL <checks>` | classify once with `workflow-health-triage`. A real defect: fix it with a follow-up commit on the same branch in the lane worktree (no amend, no force-push), lint, push, restart the script. Flake or infrastructure: one `gh run rerun --failed`, then restart the script. A second red stops this PR |
| 1 | `#N DIRTY …` | stop the train, set the lane `blocked`, report the conflict; the slot stays occupied until the operator resolves it |
| 1 | `#N CLOSED …` | record it; a closed own PR sets its lane `blocked` |
| 2 | usage or environment error | fix the invocation (a cross-repository PR in the queue is refused by design); never work around the refusal |
| 3 | `#N PENDING …` | set `phase: awaiting-ci`, checkpoint, halt; never promote the next branch onto a `develop` tip the pending head is about to move. `--resume` restarts the script |

A cancelled run is not a failure and never reaches this table: the script ignores it.

## When the script is not running

After a crash or a restart, runs of other branches may have been queued meanwhile. Restarting the script for the head cleans them up on its first poll. Without a head (all lanes still local), there is nothing to cancel. `pull-request-runner-sweep` in its non-interactive mode is the manual equivalent when the operator wants a one-off cleanup under the recorded authorisation.

## Stop conditions (this lane is set aside; the train continues with independent lanes once the slot is free)

- a required check is red again after one classification and one repair
- a blocking review or security finding
- a rebase conflict at promotion
- the merge skill refuses (unresolved authorship, missing `automerge` label, `merge_failed` in the automerge run)

A set-aside lane whose PR is still open keeps the slot: close nothing on the operator's behalf, report it, and halt the train until it lands or is closed. A lane that depends on a set-aside lane is set aside with it. Report both at close.
