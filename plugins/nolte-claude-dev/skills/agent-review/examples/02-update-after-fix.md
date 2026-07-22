# Example 02: Update pass after the author fixed two findings

## Input prompt

"I removed Edit from the tools list and added a counter-dimension to the rationale section in agents/release-notes-drafter.md — please update the review plan."

## Input files (optional)

- `.audits/agent-review/release-notes-drafter.md` — existing plan with `status: open`, two of its findings (`F-2` read-only-agent invariant, `F-5` missing counter-dimension) claimed as closed by the user.
- `agents/release-notes-drafter.md` — agent file the author just edited; expected to no longer list `Edit` in `tools` and to contain at least one counter-dimension paragraph in `## Rationale`.

## Expected behaviour

1. Read `.audits/agent-review/release-notes-drafter.md`, identify the two items the user claims are closed (`F-2`, `F-5`), and re-run exactly those two checks against the current `agents/release-notes-drafter.md` — re-inspect the `tools` list for `F-2` and re-grep `## Rationale` for a counter-dimension marker for `F-5`.
2. If both verifications pass, mark `F-2` and `F-5` `- [x]` in place, leave every other `- [ ]` untouched, and append two lines to `## Processing log`: `2026-05-10 — F-2 — removed Edit from tools — verified: re-read frontmatter` and `2026-05-10 — F-5 — added counter-dimension paragraph — verified: re-grepped ## Rationale`.
3. Flip `status:` from `open` to `in-progress` (this is the first closure on the plan), do **not** stage or commit, and show the diff to the user so they can review and commit themselves.
