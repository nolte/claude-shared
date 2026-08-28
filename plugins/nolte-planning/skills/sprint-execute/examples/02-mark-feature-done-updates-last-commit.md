# Example 02 — Marking a feature done updates the sprint's last_commit

Exercises operation C (`in_progress → done`) and confirms that the skill is the canonical writer of the sprint's `last_commit` frontmatter field, resolved via `git rev-parse HEAD` per `spec/project/sprint/` §Frontmatter schema. Confirms the Hard rule that `last_commit` is written **only** as a side effect of a feature in that sprint reaching `done`.

## Input prompt

> Mark feature `F-12` done — every acceptance criterion is checked and the test hooks are green.

## Input files

`project/sprints/0007-auth-hardening.md` (already `active`, `last_commit` carries an older SHA from a previous done feature in this sprint):

```markdown
---
id: 0007
slug: auth-hardening
status: active
value_statement: Operators can rotate session secrets without downtime.
roadmap_items: [R-3, R-5]
features: [F-12, F-13]
verifies_sprint_value: F-12
started: 2026-05-04
ended: null
last_commit: 8a1f2c4d9e0b1a2c3d4e5f6789abcdef01234567
artifact_ref: null
---

# Sprint 0007 — Auth hardening

## Features

- [F-12](../features/auth-flow-refactor.md) — in_progress
- [F-13](../features/session-secret-rotation.md) — done
```

`project/features/auth-flow-refactor.md`:

```markdown
---
id: F-12
slug: auth-flow-refactor
status: in_progress
sprint: 0007
roadmap_item: R-3
verifies_sprint_value: true
started: 2026-05-04
ended: null
---

# F-12 — Auth flow refactor

## Acceptance criteria

- [x] Session tokens rotate without invalidating in-flight requests.
- [x] Old session secrets are revoked within 60 s of rotation.
- [x] Rotation surface is documented under `docs/operations/`.

## Test hooks

- `tests/integration/test_session_rotation.py::test_no_invalidation` — passing
- `tests/integration/test_session_rotation.py::test_revocation_timing` — passing
- `tests/docs/test_operations_section.py::test_rotation_documented` — passing
```

Working tree state: current branch tip resolves to commit SHA `c4f9e2a1b3d5f7a9c1e3b5d7f9a1c3e5b7d9f1a3` (i.e. `git rev-parse HEAD` returns that string).

## Expected behaviour

1. Skill reads `project/features/auth-flow-refactor.md`; confirms `status: in_progress`, every acceptance-criterion checkbox is `[x]`, and every `## Test hooks` entry's status is `passing` (none `pending` or `failing`). Per `spec/project/feature/` §Lifecycle and gates, the gates pass.
2. Skill reads `project/sprints/0007-auth-hardening.md`; confirms `status: active` (the sprint named by `F-12.sprint` is in an allowed state for closure of a feature).
3. Skill mutates `project/features/auth-flow-refactor.md` frontmatter: `status: done`, `ended: 2026-05-10`.
4. Skill runs `git rev-parse HEAD` exactly once and captures the returned SHA `c4f9e2a1b3d5f7a9c1e3b5d7f9a1c3e5b7d9f1a3`.
5. Skill mutates `project/sprints/0007-auth-hardening.md` frontmatter: `last_commit: c4f9e2a1b3d5f7a9c1e3b5d7f9a1c3e5b7d9f1a3` (overwriting the older SHA). This is the sole legitimate write of `last_commit` per the Hard rules.
6. Skill updates the body bullet for `F-12` in the sprint's `## Features` list to read `done` so the body and frontmatter remain in sync (operation D's atomicity rule applies even within operation C — body and frontmatter must stay coherent).
7. Skill does **not** touch the sprint's `status`, `started`, `ended`, `artifact_ref`, or `value_statement` fields. The sprint stays `active`; closure is `sprint-review`'s authority.
8. Skill surfaces the updated sprint state to the user: features remaining `in_progress` (none — both `F-12` and `F-13` are now `done`), the new `last_commit` SHA, and a hint that `sprint-review` is now invokable because every feature in the sprint is `done`.

Failure modes that MUST be surfaced instead of silently succeeding:

- Any unchecked acceptance-criterion checkbox or any `pending` / `failing` test-hook status — refuse and name the offending criterion / hook; do not write `done`, do not write `last_commit`.
- Sprint `0007` not in `active` or `review` — refuse per `spec/project/feature/` §Lifecycle and gates.
- `git rev-parse HEAD` failing (e.g. detached worktree without commits) — refuse the operation; do not write `done` to the feature without also writing `last_commit` to the sprint, since the two writes are coupled.
