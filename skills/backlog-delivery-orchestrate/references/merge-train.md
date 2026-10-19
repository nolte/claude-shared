# Merge train

Read at operation 4. One PR at a time; the order is dependency first, then partition order.

## Per PR

1. **Re-read live state**: `gh pr view <n> --json state,isDraft,headRefOid,mergeStateStatus,labels`. If it was merged or closed meanwhile, record that and move on.
2. **Re-sync.** `git -C <worktree> fetch origin develop`; if the branch lags, `git -C <worktree> rebase origin/develop`, then `git -C <worktree> push --force-with-lease`. Rebase conflicts stop this PR (blocked, reported). The rebased head is a new commit: its required checks must report success again.
3. **Focus the runners.** Run `pull-request-runner-sweep` with this PR as the explicit current PR. Pre-answer its confirmation for runs of PRs recorded in this run's lanes; any other PR's runs are shown to the operator and need their own answer.
4. **Merge.** Run `pull-request-merge` with wait mode for this PR, from its worktree. Its own `review` and `security-review` delegation stays; a blocking finding stops this PR and is shown verbatim. Its label, ready, and `automerge` steps are covered by the authorisation.
5. **Verify** `state == MERGED` and the merge commit on `origin/develop` (the skill's step 7).
6. **Close** the merged lane's member issues listed in the approved partition, with the cross-reference comment `pull-request-merge` prescribes.
7. **Clean up** the lane worktree only if it is clean and its branch is merged; otherwise leave it and say so.
8. Checkpoint, then the refresh check (operation 5).

## Stop conditions (this PR is set aside, the train continues with independent PRs)

- a required check is red after one classification via `workflow-health-triage` (no blind rerun)
- a blocking review or security finding
- a rebase conflict
- the merge skill refuses (unresolved authorship, missing `automerge` label, `merge_failed` in the automerge run)

A PR that depends on a set-aside PR is set aside with it. Report both at close.
