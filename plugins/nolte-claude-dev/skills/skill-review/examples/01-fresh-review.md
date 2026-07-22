# Example 01: Fresh review with validator run

## Input prompt

"Please review the `roadmap-init` skill against the spec and write the plan."

## Input files (optional)

- `skills/roadmap-init/SKILL.md` — the skill under review (frontmatter, body, rationale, hard rules)
- `spec/claude/skill-management/en.md` — canonical authoring spec
- `spec/claude/skill-vs-agent/en.md` — canonical orchestration spec
- `spec/claude/review-plan/en.md` — canonical plan-format spec
- `spec/claude/skill-review/en.md` — canonical reviewer-procedure spec

## Expected behaviour

1. Run the four-file precondition check under `spec/claude/`, resolve `<canonical>` from `spec/.spec-config.yml` (`en`), confirm `.audits/` is tracked, default the target to `skills/roadmap-init/`, and check that `.audits/skill-review/roadmap-init.md` does not yet exist.
2. Read the review surface in declared order (`SKILL.md` first, then every relative-path reference, then any sibling agent the skill dispatches to), invoke the external skill-structure validator (`skills-ref` or equivalent), capture its name plus version, and map validator errors to `Critical` and warnings to `Warning` with each rule identifier in the bracketed prefix per `skill-review` §"Checks derived from external skill-structure validation"; if no validator is provisioned, write `Validator: override — <one-line justification>` into `## Scope` instead of silently skipping.
3. Apply the remaining checks in the spec's declared order (frontmatter → description/triggers → body → rationale → assets → duplicate-prevention via `Grep` over every other `skills/*/SKILL.md` and `agents/*.md` `description:` line → best-practices → `Info`), draft the plan from `templates/plan.template.md` with `repo-revision` set to `git rev-parse HEAD` (or `unknown`), `created: 2026-05-10`, `status: open`, every item rendered as `- [ ]` with a four-line `statement` / `Where` / `Fix` / `Verify` block and a bracketed spec citation, write the file to `.audits/skill-review/roadmap-init.md`, confirm the path back to the user, and leave it as a working-tree change without committing.
