# Example 01: Fresh review run with findings

## Input prompt

"Review the agent at agents/release-notes-drafter.md against the spec and write the plan."

## Input files (optional)

- `agents/release-notes-drafter.md` — target agent under review; declares `tools: [Read, Grep, Edit]` and a `description` whose verbs are "draft" and "summarise".
- `spec/claude/agent-management/en.md` — authoring spec the checks derive from.
- `spec/claude/skill-vs-agent/en.md` — needed for the no-Skill-dispatch check.
- `spec/claude/review-plan/en.md` — fixes the severity vocabulary and plan shape.

## Expected behaviour

1. Verify the four required specs exist under `spec/claude/`, resolve the target to `agents/release-notes-drafter.md`, and confirm no plan already lives at `.audits/agent-review/release-notes-drafter.md` (ask the user before overwriting if it did).
2. Walk the spec's checks in declared order — frontmatter, tools scoping, body, no-Skill-dispatch grep, rationale section, referenced assets, duplicate-prevention sweep, info observations — record severities verbatim from the `review-plan` vocabulary, and flag `Edit` in `tools` as a `Critical` because the description verbs are "draft" / "summarise" but the body never produces a write (read-only-agent invariant).
3. Render `templates/plan.template.md` with `created: 2026-05-10`, `repo-revision: <git rev-parse HEAD>`, every finding in the four-line `Where` / `Fix` / `Verify` shape with a bracketed spec citation, no `- [x]` boxes, write the file to `.audits/agent-review/release-notes-drafter.md`, confirm the path back to the user, and leave the change unstaged unless the user asks for a commit.
