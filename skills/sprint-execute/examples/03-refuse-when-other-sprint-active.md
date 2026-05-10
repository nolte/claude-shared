# Example 03 — Refuse to start a feature on sprint 8 while sprint 7 is still active

Exercises the at-most-one-active-sprint invariant from `spec/project/sprint/` §Lifecycle. The user asks to start a feature whose `sprint` field points at a `planned` sprint, but a lower-numbered sprint is still `active`. The skill MUST refuse the transition with a verbatim error naming the conflicting `active` sprint, MUST NOT promote the planned sprint, and MUST NOT mutate the feature.

## Input prompt

> Start feature `F-21` — let's get the rate-limiter rewrite moving for sprint 8.

## Input files

`project/sprints/0007-auth-hardening.md` (still `active`, not yet closed):

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

`project/sprints/0008-rate-limiter-rewrite.md` (`planned`, not yet activatable because sprint 7 is still `active`):

```markdown
---
id: 0008
slug: rate-limiter-rewrite
status: planned
value_statement: API consumers see consistent 429 behaviour under burst load.
roadmap_items: [R-7]
features: [F-21]
verifies_sprint_value: F-21
started: null
ended: null
last_commit: null
artifact_ref: null
---

# Sprint 0008 — Rate-limiter rewrite

## Features

- [F-21](../features/rate-limiter-rewrite.md) — ready
```

`project/features/rate-limiter-rewrite.md`:

```markdown
---
id: F-21
slug: rate-limiter-rewrite
status: ready
sprint: 0008
roadmap_item: R-7
verifies_sprint_value: true
---
```

## Expected behaviour

1. Skill reads `project/features/rate-limiter-rewrite.md`; confirms `status: ready` and `sprint: 0008`.
2. Skill reads `project/sprints/0008-rate-limiter-rewrite.md`; confirms `F-21` is in the `features` list (back-reference is intact).
3. Skill walks every `project/sprints/*.md` to determine the at-most-one-active-sprint state. It finds `0007-auth-hardening` with `status: active`.
4. Operation B's step 3 enters the `planned while another sprint is active` branch. **Skill refuses the transition** and surfaces a verbatim error to the user that names both the offending feature's sprint and the conflicting `active` sprint, e.g.:

   > Cannot start feature `F-21`: its sprint `0008 — rate-limiter-rewrite` is `planned`, but sprint `0007 — auth-hardening` is currently `active`. The at-most-one-active-sprint invariant (`spec/project/sprint/` §Lifecycle) forbids promoting `0008` while `0007` is open. Close or cancel sprint `0007` via `sprint-review` first, then retry.

5. Skill MUST NOT mutate `project/sprints/0008-rate-limiter-rewrite.md` (no `status: active`, no `started:` write).
6. Skill MUST NOT mutate `project/features/rate-limiter-rewrite.md` (no `status: in_progress`).
7. Skill MUST NOT touch `project/sprints/0007-auth-hardening.md` in any way — closure is `sprint-review`'s authority and the skill MUST hand back to the operator.
8. Skill MUST NOT invoke operation D (no body / frontmatter sync) and MUST NOT invoke operation C (no `last_commit` write) as a "while I'm here" cleanup; per the Operations preamble, the skill never silently extends one operation into another.
9. Final user-facing summary names the next legitimate action explicitly: invoke `sprint-review` against sprint `0007` (close or cancel), then retry starting `F-21`.

This example is the load-bearing refusal path that the SKILL.md "Why this is a skill, not an agent" section calls out — the user-facing refusal MUST surface both sprint identities and the spec section that grounds the refusal.
