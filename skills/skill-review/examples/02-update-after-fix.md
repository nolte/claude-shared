# Example 02: Update plan after item closures

## Input prompt

"I fixed findings 1 and 3 in the roadmap-init review, commits c0ffee1 and c0ffee2 just landed on develop — please mark them off."

## Input files (optional)

- `.audits/skill-review/roadmap-init.md` — existing plan with `status: open`, findings 1..N rendered as `- [ ]`
- `skills/roadmap-init/SKILL.md` — the skill under review, now containing the user's fixes

## Expected behaviour

1. Read `.audits/skill-review/roadmap-init.md`, locate items 1 and 3, and re-run the specific check that produced each finding by re-reading `skills/roadmap-init/SKILL.md` (and re-grepping for the duplicate-prevention case) — never take the user's word alone when verification is cheap.
2. For every item where the check now passes, flip its checkbox to `- [x]` in place; for any item still failing, leave it `- [ ]` and report the still-failing condition back to the user with the exact `Verify` step that did not pass.
3. Append two lines to `## Processing log` in the form `2026-05-10 — <item-shorthand> — fix landed in c0ffee1 — verified: re-ran check` (one per closure), flip frontmatter `status` from `open` to `in-progress` because this is the first closure on this plan, show the resulting diff to the user, and stop without committing — committing the plan update is the user's call.
