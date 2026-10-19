# Lanes

Read at operation 3.

## Round planner

1. Take the approved lanes in partition order. A lane is **ready** when no ordering edge points at an unmerged lane (serial edges and dependency edges both block; disjoint touch surfaces don't).
2. A round is the first up-to-three ready lanes. Fewer are fine; never pad.
3. A lane waiting on another waits for that lane's **merge**, not its PR: its branch must start from the `develop` tip that contains the predecessor.
4. After the round's lanes return, the merge train drains their PRs (operation 4), then the next round is planned from the new state.

## Per lane

1. Create the worktree: `task worktree:add -- <branch> <slug>` (branch from the Conventional-Commits type in the partition record). Never under `.claude/worktrees/`. Set `CLAUDE_AGENT_WORKTREE_ROOT` under `${NOLTE_WORKTREE_ROOT:-~/repos/.worktrees}/<repo>/agents/` before the first isolated agent call.
2. Dispatch one agent per lane, all lanes of the round in one message. The brief follows `spec/claude/dispatch-brief/` and carries: the lane record from the partition artifact, the worktree path (use absolute paths or `git -C`; the shell resets to the primary checkout), the skill to run (`issue-batch-orchestrate` with the group record, or `issue-orchestrate` with the single's record), the relevant lines of the authorisation, and refutation authority (a brief claim the code contradicts is reported, not obeyed).
3. The brief ends the lane at **PR opened, first CI started**. It forbids merging, labelling `automerge`, cancelling runs, and touching any other worktree.
4. The agent returns: PR number, branch, worktree, one-paragraph summary, anything blocked. Record them in the lane entry.

## When a lane agent cannot write its worktree

Background and isolated agents have failed to reach worktrees outside the project directory. If a lane agent reports a permission failure on its worktree, switch that lane to **draft-and-return**: the agent returns the proposed edits, and the session applies them with `git -C <worktree>`. If that is also unavailable, run the lane in the session itself, serially, and say the round lost its parallelism. Never move a lane's edits into the primary checkout.

## Lane transcripts

A subagent's transcript isn't resumable on its own. Recovery after a crash comes from the lane skill's own checkpoint in the worktree (`.resume/<skill>/`) plus this skill's state file; re-dispatch the lane with `--resume`.
