# Lanes

Read at operation 3.

## Round planner

1. Take the approved lanes in partition order. A lane is **ready** when no ordering edge points at an unmerged lane (serial edges and dependency edges both block; disjoint touch surfaces don't).
2. A round is the first up-to-three ready lanes. Fewer are fine; never pad. The cap of three counts **running lane agents**. Lanes that returned `committed-locally` don't count against it: they hold no PR and no runner.
3. A lane waiting on another waits for that lane's **merge**, not its commit: its branch must start from the `develop` tip that contains the predecessor.
4. A new round may start while the merge train runs, as long as the running lane agents stay at three or fewer. The train always has priority: when both a promotion and a new round are possible, promote first.

## Per lane

1. Create the worktree: `task worktree:add -- <branch> <slug>` (branch from the Conventional-Commits type in the partition record). Never under `.claude/worktrees/`. Set `CLAUDE_AGENT_WORKTREE_ROOT` under `${NOLTE_WORKTREE_ROOT:-~/repos/.worktrees}/<repo>/agents/` before the first isolated agent call.
2. Dispatch one agent per lane, all lanes of the round in one message. The brief follows `spec/claude/dispatch-brief/` and carries: the lane record from the partition artifact, the worktree path (use absolute paths or `git -C`; the shell resets to the primary checkout), the skill to run **as a lane** (`issue-batch-orchestrate` with the group record, or `issue-orchestrate` with the single's record), the relevant lines of the authorisation, and refutation authority (a brief claim the code contradicts is reported, not obeyed).
3. The brief ends the lane at **`committed-locally`**: the lane skill's full verification is green in the worktree, its transient artifacts are removed, and the work is committed. It forbids `git push`, opening a PR, merging, labelling, cancelling runs, and touching any other worktree.
4. The agent returns: branch, worktree, the commit SHA of the branch tip, the lane skill's own run id (its `.resume/<skill>/` file), the PR title and body draft the lane skill composed, a one-paragraph summary, anything blocked. Record them in the lane entry (`commit`, `lane_run_id`, status `committed-locally`). Verify the claim: `git -C <worktree> rev-parse HEAD` equals the returned commit, `git -C <worktree> status --porcelain` is empty, and `git ls-remote origin refs/heads/<branch>` returns nothing.

## When a lane agent cannot write its worktree

Background and isolated agents have failed to reach worktrees outside the project directory. If a lane agent reports a permission failure on its worktree, switch that lane to **draft-and-return**: the agent returns the proposed edits, and the session applies and commits them with `git -C <worktree>`. If that is also unavailable, run the lane in the session itself, serially, and say the round lost its parallelism. Never move a lane's edits into the primary checkout.

## Resuming a lane

A lane entry with status `running` after a crash is **not** re-created. Check first: does the worktree exist, and does it carry a commit beyond `origin/develop` with a clean tree? If the lane skill's checkpoint says its verification finished, record `committed-locally` with that commit. If only the worktree exists, re-dispatch into it with the lane skill's `--resume <lane_run_id>`; never run `task worktree:add` twice for one branch.

## Lane transcripts

A subagent's transcript isn't resumable on its own. Recovery after a crash comes from the lane skill's own checkpoint in the worktree (`.resume/<skill>/`) plus this skill's state file; re-dispatch the lane with `--resume`.
