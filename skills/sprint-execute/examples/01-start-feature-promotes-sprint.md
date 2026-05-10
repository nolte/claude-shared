# Example 01 — Starting the first feature promotes a planned sprint to active

Exercises operation B (`ready → in_progress`) cascading into operation A (`planned → active`) as a side effect, per `spec/project/sprint/` §Lifecycle. Confirms that the skill performs the sprint promotion implicitly when the operator starts the first feature, and surfaces a one-line "Starting sprint" confirmation before mutating the feature.

## Input prompt

> Start feature `F-12` — I'm picking up the auth-flow refactor today.

## Input files

`project/sprints/0007-auth-hardening.md` (planned, lowest-numbered planned sprint, no other sprint currently `active`):

```markdown
---
id: 0007
slug: auth-hardening
status: planned
value_statement: Operators can rotate session secrets without downtime.
roadmap_items: [R-3, R-5]
features: [F-12, F-13]
verifies_sprint_value: F-12
started: null
ended: null
last_commit: null
artifact_ref: null
---

# Sprint 0007 — Auth hardening

## Features

- [F-12](../features/auth-flow-refactor.md) — ready
- [F-13](../features/session-secret-rotation.md) — ready
```

`project/features/auth-flow-refactor.md` (the feature the operator is starting):

```markdown
---
id: F-12
slug: auth-flow-refactor
status: ready
sprint: 0007
roadmap_item: R-3
verifies_sprint_value: true
---
```

`project/features/session-secret-rotation.md`:

```markdown
---
id: F-13
slug: session-secret-rotation
status: ready
sprint: 0007
roadmap_item: R-5
verifies_sprint_value: false
---
```

No other sprint file under `project/sprints/` has `status: active`.

## Expected behaviour

1. Skill reads every `project/sprints/*.md` frontmatter, confirms no sprint is currently `active`, and confirms `0007` is the lowest-numbered `planned` sprint.
2. Skill detects that `F-12`'s `sprint` field points at a `planned` sprint and that operation A's preconditions hold; invokes operation A first.
3. Skill mutates `project/sprints/0007-auth-hardening.md` frontmatter: `status: active`, `started: 2026-05-10`.
4. Skill surfaces a one-line confirmation to the user verbatim: `Starting sprint 0007 — auth-hardening`.
5. Skill then performs operation B on `F-12`: confirms `F-12` appears in sprint `0007`'s `features` list (it does), then mutates the feature frontmatter to `status: in_progress`.
6. Skill checks the roadmap-item back-reference for `R-3`; if `R-3` is still `proposed`, flips it to `active` per `spec/project/roadmap/` §Lifecycle. (Out of scope for this example to model the roadmap file.)
7. Skill does **not** touch `last_commit` (operation C is the only canonical writer per the Hard rules).
8. Skill does **not** touch `F-13` and does **not** sync the body bullet for `F-13` (no operation D triggered).
9. Final user-facing summary names the new sprint state (`active`, `started: 2026-05-10`) and the new feature state (`F-12: in_progress`).

Failure modes that MUST be surfaced instead of silently succeeding:

- If any other sprint file has `status: active`, refuse with a verbatim error naming that sprint's number and slug; do not mutate `0007` and do not transition `F-12`.
- If `0007` isn't the lowest-numbered `planned` sprint, refuse and name the lower-numbered `planned` sprint that should activate first.
- If `F-12` isn't in `0007`'s `features` list, stop and report the broken back-reference per `spec/project/sprint/` §Roadmap and feature linkage.
