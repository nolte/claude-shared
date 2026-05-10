# Example 02: Revise an existing skill's frontmatter

## Input prompt

"The `description` of `skills/quality-gate/SKILL.md` is over 1024 characters and reads like prose. Trim it under the limit and give it a clean shape so routing stays reliable."

## Input files

- `skills/quality-gate/SKILL.md` — the existing skill whose frontmatter needs revision; the `description` field currently exceeds 1024 characters and lacks an explicit list of user-trigger phrasings.
- `spec/claude/skill-management/en.md` — canonical authoring spec, consulted for the description-length rule, the trigger-enumeration rule, and the optional `when_to_use` shape.
- Sibling skills under `skills/` (e.g. `dependency-audit/SKILL.md`) — used as shape references for a clean, trigger-enumerated `description`.

## Expected behaviour

1. Confirm this is a **revise** operation (per SKILL.md §"Operations" step 2), not a fresh scaffold and not a review — clarify in German that auditing against the spec is `skill-review`'s job, not this skill's, so this pass will only edit the frontmatter shape and not produce a `.audits/skill-review/` plan.
2. Read `skills/quality-gate/SKILL.md`, measure the current `description` length, identify the concrete user phrasings already buried in the prose ("run the quality gate", "run lint and tests", "make sure CI will pass", "vor dem Commit prüfen", …), and identify any "Don't use for …" carve-outs that must survive the trim (e.g. the `dependency-audit` and docs-build carve-outs).
3. Draft a revised `description` under 1024 characters that (a) opens with one sentence stating what the skill does, (b) enumerates the surviving English and German trigger phrasings explicitly, (c) preserves every `Don't use for …` carve-out verbatim, and (d) keeps the `name` and `tags` fields untouched. If the spec sanctions a separate `when_to_use` field for the trigger list, split the triggers out of `description` into `when_to_use` and shorten `description` to the single-sentence purpose; otherwise keep them inline.
4. Present a unified diff of the frontmatter block to the user in German for explicit approval before writing — body, hard rules, and operations sections are out of scope for this revise unless the user opts in.
5. Apply the approved edit with `Edit`, confirm the new `description` length is under 1024 characters, and close in German with: (a) the absolute path that was edited, (b) a one-line note that no plugin version was bumped (per SKILL.md §"Target location" — `release-automation` owns versioning), and (c) a recommendation to invoke `skill-review` next so the revised skill is validated against the spec (per SKILL.md §"Operations" step 2 closing sentence).
