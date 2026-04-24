# Skill Review Walkthrough

A worked end-to-end example of reviewing `audience-identify` with this skill. All paths are relative to the repository root.

## Scenario

The portfolio has gained new review specs (`skill-management`, `skill-vs-agent`, `review-plan`). The author wants to confirm the existing `audience-identify` skill is still compliant before cutting a release.

## Turn 1 — user invokes

> "Mach mal ein Skill-Review für `audience-identify`."

Expected skill behavior (`run`):

1. Precondition check — all four canonical specs exist under `spec/claude/`, canonical language is `en`, `.audits/` is tracked.
2. Target resolution — defaults to `skills/audience-identify/` (user gave only the name).
3. Existing-plan check — no file at `.audits/skill-review/audience-identify.md`, so proceed.
4. Narrow-scope ask — "voller Review", none.
5. Read the review surface: `SKILL.md`, sibling `templates/`, any referenced asset.
6. Apply checks in order (frontmatter → triggers → body → rationale → assets → duplicate-prevention → INFO).
7. Write the plan.

Expected plan path: `.audits/skill-review/audience-identify.md`, populated per `templates/plan.template.md`, with frontmatter fields filled from git state (`repo-revision`, `created`), severity counts in `## Summary`, one subsection per occurring severity in `## Findings`.

## Turn 2 — user reports partial fix

> "Finding 2 und 4 sind gefixt, commit ist gelandet."

Expected skill behavior (`update`):

1. Read `.audits/skill-review/audience-identify.md`.
2. Re-run the specific checks that produced items 2 and 4 — if both now pass, mark them `- [x]`; if one still fails, leave `- [ ]` and report that back.
3. Append two `## Processing log` lines:

   ```
   2026-04-24 — <item-2-shorthand> — fix landed in <commit-sha> — verified: re-ran check
   2026-04-24 — <item-4-shorthand> — fix landed in <commit-sha> — verified: re-ran check
   ```

4. Flip frontmatter `status` from `open` to `in-progress` (first closure).
5. Show the diff — do **not** commit.

## Turn 3 — user defers a remaining SUGGESTION

> "Item 5 ist eine Idee für später, mach ein Issue draus."

Expected skill behavior (`update`, deferral path):

1. Help draft a GitHub issue body, open it via `gh issue create` — or wait for the user to open it manually and report back the URL.
2. Annotate item 5 in place: append `→ deferred: https://github.com/<owner>/<repo>/issues/<n>` to the item's trailing line.
3. Leave the item `- [ ]` — it is *not* checked, but the deferral annotation satisfies the close-lifecycle rule.

## Turn 4 — user asks to close

> "Alle offenen Punkte sind durch. Plan kannst du schließen."

Expected skill behavior (`close`):

1. Read `.audits/skill-review/audience-identify.md`.
2. Verify no `- [ ]` `BLOCKER` remains. Lower-severity items must each be either `- [x]` or carry a `→ deferred:` annotation. Refuse and report if any BLOCKER is still open.
3. Read the creation-time counts from `## Summary` (not current state) — for example `2B/3W/1S/0I`.
4. Delete the plan file.
5. Compose the deletion commit:

   ```
   review(skill-review): close audience-identify — 2B/3W/1S/0I

   Deferred: https://github.com/<owner>/<repo>/issues/<n>
   Reviewed at repo-revision: <sha-from-frontmatter>
   ```

6. Show the message and wait for user confirmation before running `git commit`.

## Outcomes visible in git history

```text
$ git log --oneline -- .audits/skill-review/audience-identify.md
<new-sha> review(skill-review): close audience-identify — 2B/3W/1S/0I
<sha-3>   review(skill-review): update audience-identify progress (defer #42)
<sha-2>   review(skill-review): mark items 2,4 closed
<sha-1>   review(skill-review): open plan for audience-identify
```

The plan file is absent at HEAD, but the history tells the full story: when it was opened, what progressed, what was deferred, and the final severity counts at close.

## What the skill does NOT do in this flow

- Does not run the reviewed skill (`audience-identify`) — review targets the artifact, never live behavior.
- Does not bump `.claude-plugin/plugin.json` — the release workflow owns that per `release-automation` §Plugin manifest alignment.
- Does not dispatch a sub-agent — the reading volume is bounded, so the skill reads specs and target inline.
- Does not edit `spec/claude/skill-management/` when a finding would be better resolved by a spec change — it flags the `INFO` case and leaves the spec edit to a follow-up via the `spec` skill.
