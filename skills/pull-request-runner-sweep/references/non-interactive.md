# Non-interactive mode

Read when the skill is invoked with `--non-interactive`. Rule owner: `spec/project/pull-request-workflow/<canonical_language>.md` §"Serial pull-request flow", which lets a merge train cancel runs of waiting train branches and of dependency-bot branches without a per-run confirmation, under a standing authorisation recorded at the run's single gate.

## Invocation

```
/nolte-shared:pull-request-runner-sweep --non-interactive --current <N> --authorisation <state-file>
```

All three arguments are required. `<state-file>` is the caller's checkpoint, for example `.resume/backlog-delivery-orchestrate/<run_id>.yml`.

## Verify the authorisation before anything else

Refuse, and fall back to the interactive mode, when any of these fails:

- the file parses, its `status` is `in_progress`, and `state.authorisation` lists `cancel-waiting-and-bot-runs`
- `<N>` is open, targets `develop`, and is one of the file's lane PRs (`state.lanes[].pr`) or a dependency-bot PR (author on the allowlist, `isCrossRepository == false`)

## What changes

- Step 2 doesn't rank or ask: `<N>` is current.
- The candidate set narrows to runs whose branch is a waiting train branch of the file (`state.lanes[].branch`, excluding `<N>`'s) or starts with the dependency-bot prefix (`renovate/`). Runs of every other PR are left alone, listed in the report, and never cancelled in this mode.
- Step 4 doesn't wait for approval; the recorded authorisation is the approval. The report names the state file and its `run_id` as the authority.

## What doesn't change

Everything in `references/runs-and-cancel.md` still applies: only `pull_request` and `pull_request_target` runs, the keep predicate (current PR, delivery workflows, unattributable runs), the re-validation of the current PR and of each run right before its cancel, and the cancelled-run ids in the report. Every hard rule except the per-run confirmation stays in force.
