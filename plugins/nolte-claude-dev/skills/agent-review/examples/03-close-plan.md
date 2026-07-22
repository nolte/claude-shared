# Example 03: Close the plan after every item is processed

## Input prompt

"Close the agent review plan for release-notes-drafter — every Critical is fixed and the two Suggestions are deferred to GitHub issues."

## Input files (optional)

- `.audits/agent-review/release-notes-drafter.md` — plan with all `Critical` items `- [x]`, two `Suggestion` items closed via `→ deferred: https://github.com/nolte/claude-shared/issues/123` and `→ deferred: https://github.com/nolte/claude-shared/issues/124`, no open `- [ ]` `Critical` lines remaining.
- `agents/release-notes-drafter.md` — the reviewed agent (read once more only to spot-check that the closed Criticals stayed closed).

## Expected behaviour

1. Read the plan, refuse to proceed if any open `- [ ]` `Critical` is found (offer to help open tracking issues if `Warning` / `Suggestion` lines lack a `→ deferred:` URL), and parse the at-creation-time totals from `## Summary` — for example `Critical: 3`, `Warning: 1`, `Suggestion: 2`, `Info: 1`.
2. Compose the deletion commit message exactly: subject `review(agent-review): close release-notes-drafter—3C/1W/2S/1I`, body listing the two deferred issue URLs and the plan's recorded `repo-revision` SHA; no hook bypass, no signing skip, English-only.
3. Show the message to the user, wait for explicit confirmation, then `git rm` the plan file at `.audits/agent-review/release-notes-drafter.md` and run `git commit` with the prepared message — leaving the working tree clean and the plan archived only in git history.
