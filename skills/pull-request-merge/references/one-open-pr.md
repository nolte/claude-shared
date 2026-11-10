# One open PR at a time

Read when other pull requests against `develop` are open while this skill runs.

This skill merges **one** PR — the one on the current branch. Under `spec/project/pull-request-workflow/<canonical_language>.md` §"Serial pull-request flow", an orchestrated run keeps exactly one PR against `develop` open, so the next PR doesn't exist yet when this one merges: the run opens it afterwards. Other open PRs (another author's, a dependency bot's) still merge one at a time per §"Sequential merge of multiple open PRs":

- Merge in **dependency order** when one PR builds on another — the prerequisite first.
- The Preconditions lag-check (`git merge-base --is-ancestor origin/develop HEAD`) enforces the rebase-between-merges rule: once another PR lands on `develop`, this branch lags, and the skill stops and hands back until it is rebased and its required checks are green on the rebased head (a green signal from before the rebase doesn't authorize the merge).
- Step 9 surfaces any PR still open after a merge, so the operator or the orchestrating run knows what holds the slot.
