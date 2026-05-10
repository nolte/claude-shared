# Example 03: Close plan with deletion commit

## Input prompt

"All open items on the roadmap-init review are either fixed or deferred to issues — please close the plan."

## Input files (optional)

- `.audits/skill-review/roadmap-init.md` — plan with `status: in-progress`, every `Critical` either `- [x]` or downgraded, lower-severity items either `- [x]` or carrying a `→ deferred: https://github.com/<owner>/<repo>/issues/<n>` annotation, and `## Summary` recording the creation-time severity counts (e.g. `2C/3W/1S/0I`)

## Expected behaviour

1. Read `.audits/skill-review/roadmap-init.md`, refuse to proceed if any open `- [ ]` `Critical` remains (offer to help open tracking issues for any uncovered lower-severity items), and re-read the creation-time counts directly from `## Summary` rather than from current checkbox state — the commit message records the original review scale, not what is still open now.
2. Delete the plan file at `.audits/skill-review/roadmap-init.md`, then compose the deletion commit message exactly as `review(skill-review): close roadmap-init—2C/3W/1S/0I` in the subject (em-dash separator, single-letter severity codes, no abbreviations expanded), with the body listing every deferred-issue URL the plan referenced plus a trailing `Reviewed at repo-revision: <sha-from-frontmatter>` line.
3. Show the full commit message to the user and wait for explicit confirmation before running `git commit` — never bypass hooks, never skip signing, and never auto-commit on behalf of the user; on confirmation, stage the deletion and create the commit so `git log --oneline -- .audits/skill-review/roadmap-init.md` ends with the close subject above HEAD.
