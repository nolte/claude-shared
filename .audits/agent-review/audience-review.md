---
review-type: agent-review
target: agents/audience-review.md
target-kind: agent
specs-applied:
  - slug: agent-management
    revision: unversioned
  - slug: skill-vs-agent
    revision: unversioned
  - slug: review-plan
    revision: unversioned
  - slug: agent-review
    revision: unversioned
repo-revision: 0ce5c10b491d8f49f4c286091d4d5ec289457bbd
created: 2026-04-24
status: complete
---

# Agent Review: audience-review

## Scope

Target: `agents/audience-review.md` (101 lines — frontmatter + body; no sibling `agents/audience-review/` assets).
Specs applied: `agent-management`, `skill-vs-agent`, `review-plan`, `agent-review` (all currently untracked in git; revision `unversioned`).
Narrowing: none — full review.
Explicitly out of scope: runtime behavior of the agent (no dispatch executed), Vale/markdown style (handled by `task lint`), the orchestrating skill beyond confirming the dispatch direction (no sibling skill dispatches `audience-review` at present).

## Summary

- BLOCKER: 0
- WARNING: 1
- SUGGESTION: 0
- INFO: 0

Go/no-go: PASS — every finding processed; plan ready for `close`.
Next concrete action: run `agent-review close audience-review` to delete the plan with commit `review(agent-review): close audience-review — 0B/1W/0S/0I`.

## Findings

### WARNING

- [x] [agent-management.recommendations-prompt-ordering] `agent-management` §Recommendations declares the SHOULD ordering "role and boundaries, then the expected output format, then the working procedure". `audience-review` opens with role (top paragraph — good) and rationale (required by `skill-vs-agent`, fine), then Inputs → Preconditions → **Review procedure → Output shape → Hard rules**. The detailed output shape thus appears *after* the procedure, inverting the SHOULD.
      Where: `agents/audience-review.md` — `## Review procedure` (line ~40) precedes `## Output shape` (line ~70); the opening paragraph does name "a structured findings report" as the output, which mitigates but does not satisfy the SHOULD about the detailed format.
      Fix: Move the `## Output shape` section to immediately before `## Review procedure`; re-read the surrounding prose to keep the transitions coherent.
      Verify: `grep -n "^## " agents/audience-review.md` shows `Output shape` appearing before `Review procedure` in the ordering; body length stays within the 200-line SHOULD target.

## Processing log

<!-- Append one line per item closure: YYYY-MM-DD — <item-shorthand> — <action taken> — verified: <method> -->
2026-04-24 — recommendations-prompt-ordering — swapped `## Output shape` and `## Review procedure` sections in `agents/audience-review.md` so the detailed output format precedes the working procedure per `agent-management` §Recommendations; updated the step-5 reference "output shape below" to "output shape above" — verified: `grep -n "^## " agents/audience-review.md` shows `Output shape` at line 40, `Review procedure` at line 74; body length 101 lines, within the 200-line SHOULD target
