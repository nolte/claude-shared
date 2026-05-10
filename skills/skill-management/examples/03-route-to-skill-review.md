# Example 03: Route a review request to skill-review

## Input prompt

"Review the `roadmap-init` skill against the spec and tell me whether it is spec-compliant."

## Input files

- `skills/roadmap-init/SKILL.md` — the skill the user wants reviewed; only inspected far enough to confirm the request is a review (not a scaffold or revise).
- `skills/skill-review/SKILL.md` — the skill that owns review/audit work and writes the persistent plan under `.audits/skill-review/<name>.md`.
- `spec/claude/skill-management/en.md`, `spec/claude/skill-vs-agent/en.md`, `spec/claude/review-plan/en.md` — canonical specs that `skill-review` (not this skill) applies during the review.

## Expected behaviour

1. Recognise that the request is a **review / audit**, not a scaffold and not a targeted revise — phrases like "review … against the spec", "is this skill spec-compliant", "audit skills/<name>" are out-of-scope triggers for `skill-management` (per SKILL.md §"Review / audit" and the `Do NOT use for reviewing or auditing` carve-out in the skill's own `description`).
2. Refuse to start the review inside this skill: do **not** read the spec files in depth, do **not** open `.audits/skill-review/`, do **not** draft a plan, and do **not** edit `skills/roadmap-init/SKILL.md`. Any of these would silently overlap with `skill-review` and produce a non-persistent, non-spec-cited shadow review.
3. Explain to the user in German, in two or three sentences, that (a) `skill-management` only scaffolds and revises skills, (b) reviewing an existing skill against the spec is owned by `skill-review`, which produces a persistent, spec-cited plan under `.audits/skill-review/roadmap-init.md` per `spec/claude/review-plan/`, and (c) the correct next step is to invoke the `skill-review` skill with the same target.
4. Hand off cleanly: name the exact downstream skill (`skill-review`), name the exact artefact path it will produce (`.audits/skill-review/roadmap-init.md`), and stop. Do not chain into `skill-review` automatically — the user should invoke it explicitly so the routing decision stays auditable.
5. If the user instead clarifies that they want to **revise** `roadmap-init` (e.g. "rewrite its description", "add a Hard rules section"), drop back into `skill-management`'s revise operation (per SKILL.md §"Operations" step 2). Otherwise stay stopped.
